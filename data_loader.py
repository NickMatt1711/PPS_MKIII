"""
Excel parsing, validation, and preparation of structures used by solver.
"""

import pandas as pd
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any
from constants import SAMPLE_TEMPLATE

def get_sample_workbook():
    try:
        if SAMPLE_TEMPLATE.exists():
            return SAMPLE_TEMPLATE.read_bytes()
        return None
    except Exception:
        return None

def process_shutdown_dates(plant_df: pd.DataFrame, dates: List) -> Dict[str, List[int]]:
    shutdown_periods = {}
    for _, row in plant_df.iterrows():
        plant = row["Plant"]
        s = row.get("Shutdown Start Date")
        e = row.get("Shutdown End Date")
        if pd.notna(s) and pd.notna(e):
            try:
                start = pd.to_datetime(s).date()
                end = pd.to_datetime(e).date()
                if start > end:
                    shutdown_periods[plant] = []
                    continue
                shutdown_days = [d for d, dt in enumerate(dates) if start <= dt <= end]
                shutdown_periods[plant] = shutdown_days
            except Exception:
                shutdown_periods[plant] = []
        else:
            shutdown_periods[plant] = []
    return shutdown_periods

def load_transition_matrices(excel_bytes: bytes, plant_df: pd.DataFrame) -> Dict[str, Any]:
    transition_dfs = {}
    import io
    xl = pd.ExcelFile(io.BytesIO(excel_bytes))
    for plant in plant_df['Plant'].tolist():
        possible_names = [
            f"Transition_{plant}",
            f"Transition_{plant.replace(' ', '_')}",
            f"Transition{plant.replace(' ', '')}"
        ]
        found = None
        for nm in possible_names:
            if nm in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=nm, index_col=0)
                found = df
                break
        transition_dfs[plant] = found
    return transition_dfs

def parse_input_excel(excel_bytes: bytes, buffer_days: int = 3):
    import io
    xl = pd.ExcelFile(io.BytesIO(excel_bytes))
    # Required sheets
    plant_df = pd.read_excel(xl, sheet_name="Plant")
    inventory_df = pd.read_excel(xl, sheet_name="Inventory")
    demand_df = pd.read_excel(xl, sheet_name="Demand")
    # Dates from demand
    date_col = demand_df.columns[0]
    dates = sorted(list(set(pd.to_datetime(demand_df[date_col]).dt.date.tolist())))
    last = dates[-1]
    for i in range(1, buffer_days + 1):
        dates.append(last + timedelta(days=i))
    formatted_dates = [d.strftime("%d-%b-%y") for d in dates]
    # Grades
    grades = [c for c in demand_df.columns if c != date_col]
    # demand_data by grade: dict grade -> {date: demand}
    demand_data = {}
    for g in grades:
        if g in demand_df.columns:
            demand_data[g] = {
                pd.to_datetime(demand_df.iloc[i, 0]).date(): demand_df[g].iloc[i]
                for i in range(len(demand_df))
            }
        else:
            demand_data[g] = {d: 0 for d in dates}
    # Fill buffer days zero demand
    for g in grades:
        for d in dates[-buffer_days:]:
            demand_data[g].setdefault(d, 0)
    # Inventory parsing: allowed_lines, initial_inventory, min/max etc.
    allowed_lines = {g: [] for g in grades}
    initial_inventory = {}
    min_inventory = {}
    max_inventory = {}
    min_closing_inventory = {}
    min_run_days = {}
    max_run_days = {}
    force_start_date = {}
    rerun_allowed = {}
    grade_inventory_defined = set()
    for _, row in inventory_df.iterrows():
        grade = row['Grade Name']
        lines_val = row.get('Lines')
        if pd.notna(lines_val) and str(lines_val).strip() != "":
            plants_for_row = [x.strip() for x in str(lines_val).split(',')]
        else:
            plants_for_row = plant_df['Plant'].tolist()
        for p in plants_for_row:
            if p not in allowed_lines[grade]:
                allowed_lines[grade].append(p)
        if grade not in grade_inventory_defined:
            initial_inventory[grade] = row.get('Opening Inventory', 0) if pd.notna(row.get('Opening Inventory')) else 0
            min_inventory[grade] = row.get('Min. Inventory', 0) if pd.notna(row.get('Min. Inventory')) else 0
            max_inventory[grade] = row.get('Max. Inventory', 10**9) if pd.notna(row.get('Max. Inventory')) else 10**9
            min_closing_inventory[grade] = row.get('Min. Closing Inventory', 0) if pd.notna(row.get('Min. Closing Inventory')) else 0
            grade_inventory_defined.add(grade)
        for p in plants_for_row:
            key = (grade, p)
            min_run_days[key] = int(row.get('Min. Run Days')) if pd.notna(row.get('Min. Run Days')) else 1
            max_run_days[key] = int(row.get('Max. Run Days')) if pd.notna(row.get('Max. Run Days')) else 9999
            if pd.notna(row.get('Force Start Date')):
                try:
                    force_start_date[key] = pd.to_datetime(row.get('Force Start Date')).date()
                except Exception:
                    force_start_date[key] = None
            else:
                force_start_date[key] = None
            rv = row.get('Rerun Allowed')
            if pd.notna(rv):
                val = str(rv).strip().lower()
                rerun_allowed[key] = val not in ['no', 'n', 'false', '0']
            else:
                rerun_allowed[key] = True
    # material_running_info
    material_running_info = {}
    for _, row in plant_df.iterrows():
        plant = row['Plant']
        material = row.get('Material Running')
        expected = row.get('Expected Run Days')
        if pd.notna(material) and pd.notna(expected):
            try:
                material_running_info[plant] = (str(material).strip(), int(expected))
            except Exception:
                pass
    # capacities
    capacities = {row['Plant']: int(row['Capacity per day']) for _, row in plant_df.iterrows()}
    # shutdown periods
    shutdown_periods = process_shutdown_dates(plant_df, dates)
    # transitions
    transition_dfs = load_transition_matrices(excel_bytes, plant_df)
    transition_rules = {}
    for plant, df in transition_dfs.items():
        if df is None:
            transition_rules[plant] = None
        else:
            transition_rules[plant] = {}
            for prev in df.index:
                allowed = []
                for cur in df.columns:
                    if str(df.loc[prev, cur]).strip().lower() == "yes":
                        allowed.append(cur)
                transition_rules[plant][prev] = allowed
    return {
        "plant_df": plant_df,
        "inventory_df": inventory_df,
        "demand_df": demand_df,
        "dates": dates,
        "formatted_dates": formatted_dates,
        "num_days": len(dates),
        "grades": grades,
        "lines": list(plant_df['Plant']),
        "capacities": capacities,
        "demand_data": demand_data,
        "initial_inventory": initial_inventory,
        "min_inventory": min_inventory,
        "max_inventory": max_inventory,
        "min_closing_inventory": min_closing_inventory,
        "min_run_days": min_run_days,
        "max_run_days": max_run_days,
        "force_start_date": force_start_date,
        "rerun_allowed": rerun_allowed,
        "material_running_info": material_running_info,
        "shutdown_periods": shutdown_periods,
        "transition_rules": transition_rules,
        "transition_dfs": transition_dfs,
    }
