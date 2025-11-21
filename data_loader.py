"""
Data loading and transformation module for Polymer Production Scheduler.

This module handles:
- Excel file parsing and validation
- Data transformation from Excel format to solver-compatible format
- Transition matrix processing
- Shutdown period calculation
- Data integrity checks
"""

import pandas as pd
import streamlit as st
from datetime import timedelta, date
from typing import Dict, List, Tuple, Optional, Any
import io

from .constants import (
    REQUIRED_SHEETS,
    TRANSITION_KEYWORD,
    MAX_INVENTORY_VALUE,
    MAX_RUN_DAYS,
    RERUN_NOT_ALLOWED_VALUES,
    TRANSITION_ALLOWED_VALUE,
    get_error_message,
    get_warning_message
)


def load_excel_data(uploaded_file: io.BytesIO) -> Dict[str, Any]:
    """
    Load and process Excel data into solver-compatible format.
    
    Args:
        uploaded_file: BytesIO object containing Excel file
        
    Returns:
        Dictionary containing all processed data for the solver
        
    Raises:
        ValueError: If required sheets or columns are missing
    """
    # Read Excel file
    uploaded_file.seek(0)
    excel_file = pd.ExcelFile(uploaded_file)
    
    # Validate required sheets
    _validate_sheets(excel_file)
    
    # Load core sheets
    plant_df = pd.read_excel(excel_file, sheet_name='Plant')
    inventory_df = pd.read_excel(excel_file, sheet_name='Inventory')
    demand_df = pd.read_excel(excel_file, sheet_name='Demand')
    
    # Process each component
    lines = list(plant_df['Plant'])
    capacities = _extract_capacities(plant_df)
    material_running_info = _extract_material_running(plant_df)
    
    # Extract grades from demand
    grades = [col for col in demand_df.columns if col != demand_df.columns[0]]
    
    # Process dates
    dates, formatted_dates = _extract_dates(demand_df)
    
    # Process inventory parameters
    inventory_params = _process_inventory_data(inventory_df, grades, lines)
    
    # Process demand data
    demand_data = _process_demand_data(demand_df, grades, dates)
    
    # Process shutdown periods
    shutdown_periods = _process_shutdown_dates(plant_df, dates)
    
    # Load transition matrices
    transition_rules = _load_transition_matrices(excel_file, plant_df, grades)
    
    # Compile instance dictionary
    instance = {
        'grades': grades,
        'lines': lines,
        'dates': dates,
        'formatted_dates': formatted_dates,
        'capacities': capacities,
        'material_running_info': material_running_info,
        'initial_inventory': inventory_params['initial_inventory'],
        'min_inventory': inventory_params['min_inventory'],
        'max_inventory': inventory_params['max_inventory'],
        'min_closing_inventory': inventory_params['min_closing_inventory'],
        'min_run_days': inventory_params['min_run_days'],
        'max_run_days': inventory_params['max_run_days'],
        'force_start_date': inventory_params['force_start_date'],
        'allowed_lines': inventory_params['allowed_lines'],
        'rerun_allowed': inventory_params['rerun_allowed'],
        'demand': demand_data,
        'shutdown_day_indices': shutdown_periods,
        'transition_rules': transition_rules,
        # Store raw dataframes for preview
        'raw_plant_df': plant_df,
        'raw_inventory_df': inventory_df,
        'raw_demand_df': demand_df
    }
    
    return instance


def _validate_sheets(excel_file: pd.ExcelFile) -> None:
    """Validate that all required sheets exist."""
    sheet_names = excel_file.sheet_names
    for required in REQUIRED_SHEETS:
        if required not in sheet_names:
            raise ValueError(get_error_message("missing_sheet", sheet_name=required))


def _extract_capacities(plant_df: pd.DataFrame) -> Dict[str, float]:
    """Extract plant capacities."""
    return {row['Plant']: row['Capacity per day'] for _, row in plant_df.iterrows()}


def _extract_material_running(plant_df: pd.DataFrame) -> Dict[str, Tuple[str, int]]:
    """Extract material running information."""
    material_running = {}
    for _, row in plant_df.iterrows():
        plant = row['Plant']
        material = row.get('Material Running')
        expected_days = row.get('Expected Run Days')
        
        if pd.notna(material) and pd.notna(expected_days):
            try:
                material_running[plant] = (str(material).strip(), int(expected_days))
            except (ValueError, TypeError):
                st.warning(f"⚠️ Invalid Material Running data for {plant}")
    
    return material_running


def _extract_dates(demand_df: pd.DataFrame) -> Tuple[List[date], List[str]]:
    """Extract and format dates from demand sheet."""
    dates = sorted(list(set(demand_df.iloc[:, 0].dt.date.tolist())))
    formatted_dates = [d.strftime('%d-%b-%y') for d in dates]
    return dates, formatted_dates


def _process_inventory_data(
    inventory_df: pd.DataFrame,
    grades: List[str],
    lines: List[str]
) -> Dict[str, Any]:
    """
    Process inventory sheet data into structured parameters.
    
    Returns dictionary with keys:
    - initial_inventory, min_inventory, max_inventory, min_closing_inventory (per grade)
    - min_run_days, max_run_days, force_start_date, rerun_allowed (per grade-plant)
    - allowed_lines (per grade)
    """
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
    
    for _, row in inventory_df.iterrows():
        grade = row['Grade Name']
        
        # Process Lines column
        lines_value = row.get('Lines')
        if pd.notna(lines_value) and lines_value != '':
            plants_for_row = [x.strip() for x in str(lines_value).split(',')]
        else:
            plants_for_row = lines
            st.warning(f"⚠️ Lines not specified for grade '{grade}', allowing all lines")
        
        # Add to allowed_lines
        for plant in plants_for_row:
            if plant not in allowed_lines[grade]:
                allowed_lines[grade].append(plant)
        
        # Global inventory parameters (only set once per grade)
        if grade not in grade_inventory_defined:
            initial_inventory[grade] = row.get('Opening Inventory', 0) if pd.notna(row.get('Opening Inventory')) else 0
            min_inventory[grade] = row.get('Min. Inventory', 0) if pd.notna(row.get('Min. Inventory')) else 0
            max_inventory[grade] = row.get('Max. Inventory', MAX_INVENTORY_VALUE) if pd.notna(row.get('Max. Inventory')) else MAX_INVENTORY_VALUE
            min_closing_inventory[grade] = row.get('Min. Closing Inventory', 0) if pd.notna(row.get('Min. Closing Inventory')) else 0
            grade_inventory_defined.add(grade)
        
        # Plant-specific parameters
        for plant in plants_for_row:
            grade_plant_key = (grade, plant)
            
            # Min/Max Run Days
            min_run_days[grade_plant_key] = int(row.get('Min. Run Days', 1)) if pd.notna(row.get('Min. Run Days')) else 1
            max_run_days[grade_plant_key] = int(row.get('Max. Run Days', MAX_RUN_DAYS)) if pd.notna(row.get('Max. Run Days')) else MAX_RUN_DAYS
            
            # Force Start Date
            if pd.notna(row.get('Force Start Date')):
                try:
                    force_start_date[grade_plant_key] = pd.to_datetime(row['Force Start Date']).date()
                except:
                    force_start_date[grade_plant_key] = None
            else:
                force_start_date[grade_plant_key] = None
            
            # Rerun Allowed
            rerun_val = row.get('Rerun Allowed')
            if pd.notna(rerun_val):
                val_str = str(rerun_val).strip().lower()
                rerun_allowed[grade_plant_key] = val_str not in RERUN_NOT_ALLOWED_VALUES
            else:
                rerun_allowed[grade_plant_key] = True
    
    return {
        'initial_inventory': initial_inventory,
        'min_inventory': min_inventory,
        'max_inventory': max_inventory,
        'min_closing_inventory': min_closing_inventory,
        'min_run_days': min_run_days,
        'max_run_days': max_run_days,
        'force_start_date': force_start_date,
        'allowed_lines': allowed_lines,
        'rerun_allowed': rerun_allowed
    }


def _process_demand_data(
    demand_df: pd.DataFrame,
    grades: List[str],
    dates: List[date]
) -> Dict[Tuple[str, int], float]:
    """
    Process demand data into (grade, day_index) -> demand dictionary.
    """
    demand_data = {}
    
    for grade in grades:
        if grade in demand_df.columns:
            for i in range(len(demand_df)):
                demand_date = demand_df.iloc[i, 0].date()
                try:
                    day_index = dates.index(demand_date)
                    demand_data[(grade, day_index)] = demand_df[grade].iloc[i]
                except ValueError:
                    pass
        else:
            st.warning(f"⚠️ Demand data not found for grade '{grade}'. Assuming zero demand.")
            for d in range(len(dates)):
                demand_data[(grade, d)] = 0
    
    return demand_data


def _process_shutdown_dates(
    plant_df: pd.DataFrame,
    dates: List[date]
) -> Dict[str, List[int]]:
    """
    Process shutdown periods and return day indices for each plant.
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
                    st.warning(get_warning_message("shutdown_invalid", plant=plant))
                    shutdown_periods[plant] = []
                    continue
                
                # Find day indices
                shutdown_days = []
                for d, date_val in enumerate(dates):
                    if start_date <= date_val <= end_date:
                        shutdown_days.append(d)
                
                if shutdown_days:
                    shutdown_periods[plant] = shutdown_days
                    st.info(f"🔧 Shutdown scheduled for {plant}: {start_date.strftime('%d-%b-%y')} to {end_date.strftime('%d-%b-%y')} ({len(shutdown_days)} days)")
                else:
                    shutdown_periods[plant] = []
                    st.info(get_warning_message("shutdown_outside_horizon", plant=plant))
                    
            except Exception as e:
                st.warning(f"⚠️ Invalid shutdown dates for {plant}: {e}")
                shutdown_periods[plant] = []
        else:
            shutdown_periods[plant] = []
    
    return shutdown_periods


def _load_transition_matrices(
    excel_file: pd.ExcelFile,
    plant_df: pd.DataFrame,
    grades: List[str]
) -> Dict[str, Optional[Dict[str, List[str]]]]:
    """
    Load and process transition matrices for each plant.
    
    Returns:
        Dictionary mapping plant name to transition rules.
        Transition rules: {prev_grade: [allowed_next_grades]}
    """
    transition_rules = {}
    
    for _, row in plant_df.iterrows():
        plant_name = row['Plant']
        
        # Try different sheet name variations
        possible_sheet_names = [
            f'Transition_{plant_name}',
            f'Transition_{plant_name.replace(" ", "_")}',
            f'Transition{plant_name.replace(" ", "")}'
        ]
        
        transition_df = None
        for sheet_name in possible_sheet_names:
            try:
                transition_df = pd.read_excel(excel_file, sheet_name=sheet_name, index_col=0)
                st.info(f"✅ Loaded transition matrix for {plant_name} from sheet '{sheet_name}'")
                break
            except:
                continue
        
        if transition_df is not None:
            # Process transition matrix
            plant_rules = {}
            for prev_grade in transition_df.index:
                allowed_transitions = []
                for next_grade in transition_df.columns:
                    if str(transition_df.loc[prev_grade, next_grade]).lower() == TRANSITION_ALLOWED_VALUE:
                        allowed_transitions.append(next_grade)
                plant_rules[prev_grade] = allowed_transitions
            transition_rules[plant_name] = plant_rules
        else:
            st.info(get_warning_message("no_transition_matrix", plant=plant_name))
            transition_rules[plant_name] = None
    
    return transition_rules


def add_buffer_days(instance: Dict[str, Any], buffer_days: int) -> Dict[str, Any]:
    """
    Add buffer days to the planning horizon.
    
    Args:
        instance: Solver instance dictionary
        buffer_days: Number of buffer days to add
        
    Returns:
        Updated instance with extended dates and zero demand for buffer period
    """
    if buffer_days <= 0:
        return instance
    
    dates = instance['dates']
    last_date = dates[-1]
    
    # Extend dates
    for i in range(1, buffer_days + 1):
        dates.append(last_date + timedelta(days=i))
    
    # Update formatted dates
    instance['formatted_dates'] = [d.strftime('%d-%b-%y') for d in dates]
    
    # Add zero demand for buffer days
    grades = instance['grades']
    num_original_days = len(dates) - buffer_days
    
    for grade in grades:
        for d in range(num_original_days, len(dates)):
            instance['demand'][(grade, d)] = 0
    
    return instance
