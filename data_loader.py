"""
Data Loading and Preprocessing Module
======================================

CORRECTED: Proper buffer day calculation and demand period handling
"""

import io
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import date, timedelta
import pandas as pd
import streamlit as st

import constants


class DataLoadError(Exception):
    """Custom exception for data loading errors."""
    pass


def load_excel_data(uploaded_file: io.BytesIO) -> Dict[str, Any]:
    """
    Load and validate Excel data following the exact logic from original implementation.
    CORRECTED: Proper date range handling and separation of:
       - demand_period_dates (actual demand horizon shown to user)
       - dates (planning horizon used by solver after buffer days)
    """
    try:
        uploaded_file.seek(0)
        excel_file = pd.ExcelFile(uploaded_file)
        
        # Validate required sheets
        _validate_sheets(excel_file)
        
        # Load core sheets
        plant_df = pd.read_excel(excel_file, sheet_name=constants.SHEET_PLANT)
        inventory_df = pd.read_excel(excel_file, sheet_name=constants.SHEET_INVENTORY)
        demand_df = pd.read_excel(excel_file, sheet_name=constants.SHEET_DEMAND)
        
        # Parse plants/lines
        lines = list(plant_df['Plant'])
        capacities = {row['Plant']: row['Capacity per day'] for _, row in plant_df.iterrows()}
        
        # Parse grades from demand sheet
        grades = [col for col in demand_df.columns if col != demand_df.columns[0]]
        
        # Initialize inventory parameters
        initial_inventory = {}
        min_inventory = {}
        max_inventory = {}
        min_closing_inventory = {}
        min_run_days = {}
        max_run_days = {}
        force_start_date = {}
        allowed_lines = {grade: [] for grade in grades}
        rerun_allowed = {}
        
        grade_inventory_defined = set()
        
        # Process inventory sheet
        for _, row in inventory_df.iterrows():
            grade = row['Grade Name']
            
            # Parse allowed lines
            lines_value = row['Lines']
            if pd.notna(lines_value) and lines_value != '':
                plants_for_row = [x.strip() for x in str(lines_value).split(',')]
            else:
                plants_for_row = lines
            
            # Add plants to allowed_lines
            for plant in plants_for_row:
                if plant not in allowed_lines[grade]:
                    allowed_lines[grade].append(plant)
            
            # Inventory parameters per grade
            if grade not in grade_inventory_defined:
                initial_inventory[grade] = row['Opening Inventory'] if pd.notna(row['Opening Inventory']) else 0
                min_inventory[grade] = row['Min. Inventory'] if pd.notna(row['Min. Inventory']) else 0
                max_inventory[grade] = row['Max. Inventory'] if pd.notna(row['Max. Inventory']) else 1000000000
                min_closing_inventory[grade] = row['Min. Closing Inventory'] if pd.notna(row['Min. Closing Inventory']) else 0
                grade_inventory_defined.add(grade)
            
            # Plant-specific parameters
            for plant in plants_for_row:
                key = (grade, plant)
                min_run_days[key] = int(row['Min. Run Days']) if pd.notna(row['Min. Run Days']) else 1
                max_run_days[key] = int(row['Max. Run Days']) if pd.notna(row['Max. Run Days']) else 9999
                
                # Force start date
                if pd.notna(row['Force Start Date']):
                    try:
                        force_start_date[key] = pd.to_datetime(row['Force Start Date']).date()
                    except:
                        force_start_date[key] = None
                else:
                    force_start_date[key] = None
                
                # Rerun allowed
                rerun_val = row['Rerun Allowed']
                if pd.notna(rerun_val):
                    val_str = str(rerun_val).strip().lower()
                    rerun_allowed[key] = val_str not in ['no', 'n', 'false', '0']
                else:
                    rerun_allowed[key] = True
        
        # Material running info
        material_running_info = {}
        for _, row in plant_df.iterrows():
            plant = row['Plant']
            material = row['Material Running']
            expected_days = row['Expected Run Days']
            
            if pd.notna(material) and pd.notna(expected_days):
                try:
                    material_running_info[plant] = (str(material).strip(), int(expected_days))
                except (ValueError, TypeError):
                    pass
        
        # =============== DEMAND DATE HANDLING (CORRECTED) ====================
        # Extract ACTUAL demand period dates (this must be displayed to user)
        date_series = pd.to_datetime(demand_df.iloc[:, 0])
        demand_period_dates = sorted(list(set([d.date() for d in date_series])))
        
        st.info(
            f"📅 Demand period: {len(demand_period_dates)} days "
            f"({demand_period_dates[0].strftime('%d-%b-%y')} to {demand_period_dates[-1].strftime('%d-%b-%y')})"
        )
        
        # Demand dict - only the actual demand dates
        demand_data = {}
        for grade in grades:
            demand_data[grade] = {}
            if grade in demand_df.columns:
                for i in range(len(demand_df)):
                    date_val = demand_df.iloc[i, 0]
                    date_obj = pd.to_datetime(date_val).date()
                    qty = demand_df[grade].iloc[i]
                    demand_data[grade][date_obj] = int(float(qty)) if pd.notna(qty) else 0
            else:
                for d in demand_period_dates:
                    demand_data[grade][d] = 0
        
        # Planning horizon initially equals demand horizon (buffer added later)
        dates = demand_period_dates.copy()
        
        # Shutdown periods (based only on demand horizon for now)
        shutdown_periods = _process_shutdown_dates(plant_df, dates)
        
        # Load transition matrices
        transition_dfs = {}
        for i in range(len(plant_df)):
            plant_name = plant_df['Plant'].iloc[i]
            
            possible_sheet_names = [
                f'Transition_{plant_name}',
                f'Transition_{plant_name.replace(" ", "_")}',
                f'Transition{plant_name.replace(" ", "")}',
            ]
            
            found = None
            for sheet_name in possible_sheet_names:
                try:
                    excel_file.seek(0)
                    found = pd.read_excel(excel_file, sheet_name=sheet_name, index_col=0)
                    break
                except:
                    continue
            
            transition_dfs[plant_name] = found
        
        # Process transition rules
        transition_rules = {}
        for line, df in transition_dfs.items():
            if df is not None:
                transition_rules[line] = {}
                for prev_grade in df.index:
                    allowed = [
                        current_grade
                        for current_grade in df.columns
                        if str(df.loc[prev_grade, current_grade]).lower() == 'yes'
                    ]
                    transition_rules[line][prev_grade] = allowed
            else:
                transition_rules[line] = None
        
        # Build final instance
        instance = {
            'grades': grades,
            'lines': lines,
            'dates': dates,                     # planning dates (with buffer later)
            'demand_period_dates': demand_period_dates,  # TRUE demand dates (NO BUFFER)
            'num_days': len(dates),
            'capacities': capacities,
            'demand_data': demand_data,
            'initial_inventory': initial_inventory,
            'min_inventory': min_inventory,
            'max_inventory': max_inventory,
            'min_closing_inventory': min_closing_inventory,
            'min_run_days': min_run_days,
            'max_run_days': max_run_days,
            'force_start_date': force_start_date,
            'allowed_lines': allowed_lines,
            'rerun_allowed': rerun_allowed,
            'shutdown_periods': shutdown_periods,
            'transition_rules': transition_rules,
            'material_running_info': material_running_info,
        }
        
        return instance
        
    except Exception as e:
        if isinstance(e, DataLoadError):
            raise
        else:
            raise DataLoadError(f"Error loading Excel data: {str(e)}")


def _validate_sheets(excel_file: pd.ExcelFile) -> None:
    """Validate that all required sheets exist."""
    sheet_names = excel_file.sheet_names
    required = [constants.SHEET_PLANT, constants.SHEET_INVENTORY, constants.SHEET_DEMAND]
    
    for sheet in required:
        if sheet not in sheet_names:
            raise DataLoadError(constants.ERROR_MESSAGES["missing_sheet"].format(sheet))


def _process_shutdown_dates(plant_df: pd.DataFrame, dates: List[date]) -> Dict[str, List[int]]:
    """
    Process shutdown dates for each plant following original rules.
    """
    shutdown_periods = {}
    
    for _, row in plant_df.iterrows():
        plant = row['Plant']
        shutdown_start = row.get('Shutdown Start Date')
        shutdown_end = row.get('Shutdown End Date')
        
        if pd.notna(shutdown_start) and pd.notna(shutdown_end):
            try:
                start_date = pd.to_datetime(shutdown_start).date()
                end_date = pd.to_datetime(shutdown_end).date()
                
                if start_date > end_date:
                    st.warning(f"⚠️ Shutdown start > end for {plant}. Ignoring.")
                    shutdown_periods[plant] = []
                    continue
                
                shutdown_days = [
                    i for i, d in enumerate(dates)
                    if start_date <= d <= end_date
                ]
                
                if shutdown_days:
                    shutdown_periods[plant] = shutdown_days
                    st.info(
                        f"🔧 Shutdown for {plant}: "
                        f"{start_date.strftime('%d-%b-%y')} to {end_date.strftime('%d-%b-%y')} "
                        f"({len(shutdown_days)} days)"
                    )
                else:
                    shutdown_periods[plant] = []
                    st.info(f"ℹ️ Shutdown for {plant} is outside demand horizon")
            
            except Exception as e:
                st.warning(f"⚠️ Invalid shutdown dates for {plant}: {e}")
                shutdown_periods[plant] = []
        else:
            shutdown_periods[plant] = []
    
    return shutdown_periods


def add_buffer_days(instance: Dict[str, Any], buffer_days: int) -> Dict[str, Any]:
    """
    CORRECTED:
    Adds buffer days ONLY to planning horizon (instance['dates'])
    but DOES NOT change demand_period_dates (used for display).
    """
    if buffer_days <= 0:
        return instance
    
    dates = instance['dates']
    original_num_days = len(dates)
    last_date = dates[-1]
    
    st.info(f"📅 Original demand period: {original_num_days} days")
    
    # Add buffer days
    buffer_dates = [(last_date + timedelta(days=i)) for i in range(1, buffer_days + 1)]
    
    # Extend planning horizon
    instance['dates'].extend(buffer_dates)
    instance['num_days'] = len(instance['dates'])
    
    # Set demand = 0 for buffer days
    for grade in instance['grades']:
        for bd in buffer_dates:
            instance['demand_data'][grade][bd] = 0
    
    st.success(
        f"✅ Planning horizon: {instance['num_days']} days "
        f"({original_num_days} demand + {buffer_days} buffer)"
    )
    st.info(
        f"📅 Buffer period: {buffer_dates[0].strftime('%d-%b-%y')} "
        f"to {buffer_dates[-1].strftime('%d-%b-%y')}"
    )
    
    return instance
