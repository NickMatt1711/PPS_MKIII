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
    CORRECTED: Proper date range handling
    
    Returns:
        Dictionary containing all problem instance data matching original structure
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
        
        # Parse plants/lines (matching original logic exactly)
        lines = list(plant_df['Plant'])
        capacities = {row['Plant']: row['Capacity per day'] for _, row in plant_df.iterrows()}
        
        # Parse grades from demand
        grades = [col for col in demand_df.columns if col != demand_df.columns[0]]
        
        # Initialize inventory parameters (matching original structure)
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
        
        # Process inventory sheet (exact logic from original)
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
            
            # Global inventory parameters (only set once per grade)
            if grade not in grade_inventory_defined:
                initial_inventory[grade] = row['Opening Inventory'] if pd.notna(row['Opening Inventory']) else 0
                min_inventory[grade] = row['Min. Inventory'] if pd.notna(row['Min. Inventory']) else 0
                max_inventory[grade] = row['Max. Inventory'] if pd.notna(row['Max. Inventory']) else 1000000000
                min_closing_inventory[grade] = row['Min. Closing Inventory'] if pd.notna(row['Min. Closing Inventory']) else 0
                grade_inventory_defined.add(grade)
            
            # Plant-specific parameters
            for plant in plants_for_row:
                grade_plant_key = (grade, plant)
                min_run_days[grade_plant_key] = int(row['Min. Run Days']) if pd.notna(row['Min. Run Days']) else 1
                max_run_days[grade_plant_key] = int(row['Max. Run Days']) if pd.notna(row['Max. Run Days']) else 9999
                
                # Force start date
                if pd.notna(row['Force Start Date']):
                    try:
                        force_start_date[grade_plant_key] = pd.to_datetime(row['Force Start Date']).date()
                    except:
                        force_start_date[grade_plant_key] = None
                else:
                    force_start_date[grade_plant_key] = None
                
                # Rerun allowed
                rerun_val = row['Rerun Allowed']
                if pd.notna(rerun_val):
                    val_str = str(rerun_val).strip().lower()
                    rerun_allowed[grade_plant_key] = val_str not in ['no', 'n', 'false', '0']
                else:
                    rerun_allowed[grade_plant_key] = True
        
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
        
        # CORRECTED: Parse demand data - get EXACT date range from demand sheet
        demand_data = {}
        
        # Get dates from demand sheet - these are the ACTUAL demand period dates
        date_series = pd.to_datetime(demand_df.iloc[:, 0])
        demand_period_dates = sorted([d.date() for d in date_series])
        
        # Remove any duplicates
        demand_period_dates = sorted(list(set(demand_period_dates)))
        
        st.info(f"📅 Demand period: {len(demand_period_dates)} days ({demand_period_dates[0].strftime('%d-%b-%y')} to {demand_period_dates[-1].strftime('%d-%b-%y')})")
        
        # Parse demand for each grade (only for demand period)
        for grade in grades:
            demand_data[grade] = {}
            if grade in demand_df.columns:
                for i in range(len(demand_df)):
                    date_val = demand_df.iloc[i, 0]
                    date_obj = pd.to_datetime(date_val).date()
                    demand_qty = demand_df[grade].iloc[i]
                    demand_data[grade][date_obj] = float(demand_qty) if pd.notna(demand_qty) else 0
            else:
                for date_obj in demand_period_dates:
                    demand_data[grade][date_obj] = 0
        
        # CORRECTED: dates list will be extended with buffer days in add_buffer_days()
        # For now, just use the demand period dates
        dates = demand_period_dates
        
        # Parse shutdown periods (using demand period dates for now)
        shutdown_periods = _process_shutdown_dates(plant_df, dates)
        
        # Load transition matrices (exact logic from original)
        transition_dfs = {}
        for i in range(len(plant_df)):
            plant_name = plant_df['Plant'].iloc[i]
            
            possible_sheet_names = [
                f'Transition_{plant_name}',
                f'Transition_{plant_name.replace(" ", "_")}',
                f'Transition{plant_name.replace(" ", "")}',
            ]
            
            transition_df_found = None
            for sheet_name in possible_sheet_names:
                try:
                    excel_file.seek(0)
                    transition_df_found = pd.read_excel(excel_file, sheet_name=sheet_name, index_col=0)
                    break
                except:
                    continue
            
            transition_dfs[plant_name] = transition_df_found
        
        # Process transition rules
        transition_rules = {}
        for line, df in transition_dfs.items():
            if df is not None:
                transition_rules[line] = {}
                for prev_grade in df.index:
                    allowed_transitions = []
                    for current_grade in df.columns:
                        if str(df.loc[prev_grade, current_grade]).lower() == 'yes':
                            allowed_transitions.append(current_grade)
                    transition_rules[line][prev_grade] = allowed_transitions
            else:
                transition_rules[line] = None
        
        # Build instance dict (matching original structure exactly)
        instance = {
            'grades': grades,
            'lines': lines,
            'dates': dates,  # Will be extended in add_buffer_days()
            'num_days': len(dates),  # Will be updated in add_buffer_days()
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
    Process shutdown dates for each plant - exact logic from original.
    
    Returns:
        Dict mapping plant -> list of shutdown day indices
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
                    st.warning(f"⚠️ Shutdown start date after end date for {plant}. Ignoring shutdown.")
                    shutdown_periods[plant] = []
                    continue
                
                shutdown_days = []
                for d, date in enumerate(dates):
                    if start_date <= date <= end_date:
                        shutdown_days.append(d)
                
                if shutdown_days:
                    shutdown_periods[plant] = shutdown_days
                    st.info(f"🔧 Shutdown scheduled for {plant}: {start_date.strftime('%d-%b-%y')} to {end_date.strftime('%d-%b-%y')} ({len(shutdown_days)} days)")
                else:
                    shutdown_periods[plant] = []
                    st.info(f"ℹ️ Shutdown period for {plant} is outside planning horizon")
                    
            except Exception as e:
                st.warning(f"⚠️ Invalid shutdown dates for {plant}: {e}")
                shutdown_periods[plant] = []
        else:
            shutdown_periods[plant] = []
    
    return shutdown_periods


def add_buffer_days(instance: Dict[str, Any], buffer_days: int) -> Dict[str, Any]:
    """
    CORRECTED: Extend planning horizon by adding buffer days ONLY at the end.
    Buffer days purpose: Allow production runs starting near end of demand period
    to complete their minimum run days requirement.
    """
    if buffer_days <= 0:
        return instance
    
    dates = instance['dates']
    original_num_days = len(dates)
    last_date = dates[-1]
    
    st.info(f"📅 Original demand period: {original_num_days} days")
    
    # Add buffer days AFTER the demand period
    buffer_dates = []
    for i in range(1, buffer_days + 1):
        buffer_dates.append(last_date + timedelta(days=i))
    
    # Extend dates list
    instance['dates'].extend(buffer_dates)
    instance['num_days'] = len(instance['dates'])
    
    # Set demand to ZERO for all buffer days
    for grade in instance['grades']:
        for buffer_date in buffer_dates:
            instance['demand_data'][grade][buffer_date] = 0
    
    # Update shutdown periods if they extend into buffer period
    for line in instance['lines']:
        if line in instance['shutdown_periods'] and instance['shutdown_periods'][line]:
            # Shutdown periods are stored as day indices, no need to update
            pass
    
    st.success(f"✅ Planning horizon extended: {instance['num_days']} days ({original_num_days} demand + {buffer_days} buffer)")
    st.info(f"📅 Buffer period: {buffer_dates[0].strftime('%d-%b-%y')} to {buffer_dates[-1].strftime('%d-%b-%y')}")
    
    return instance
