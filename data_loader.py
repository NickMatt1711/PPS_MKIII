"""
Data Loading and Preprocessing Module
======================================

Handles Excel file parsing, validation, and transformation into solver-ready format.
"""

import io
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import date, timedelta
import pandas as pd
import streamlit as st

# Use absolute imports
import constants


class DataLoadError(Exception):
    """Custom exception for data loading errors."""
    pass


def load_excel_data(uploaded_file: io.BytesIO) -> Dict[str, Any]:
    """
    Load and validate Excel data, returning a complete instance dictionary.
    
    Args:
        uploaded_file: BytesIO object containing Excel file
        
    Returns:
        Dictionary containing all problem instance data:
        - grades: List of product grades
        - lines: List of production lines/plants
        - dates: List of date objects for planning horizon
        - capacities: Dict mapping line -> daily capacity
        - demand: Dict mapping (grade, day_index) -> demand quantity
        - initial_inventory: Dict mapping grade -> starting inventory
        - min_inventory: Dict mapping grade -> minimum inventory
        - max_inventory: Dict mapping grade -> maximum inventory
        - min_closing_inventory: Dict mapping grade -> minimum closing inventory
        - min_run_days: Dict mapping (grade, line) -> minimum run days
        - max_run_days: Dict mapping (grade, line) -> maximum run days
        - force_start_date: Dict mapping grade -> date object
        - allowed_lines: Dict mapping grade -> list of allowed lines
        - rerun_allowed: Dict mapping (grade, line) -> boolean
        - shutdown_day_indices: Dict mapping line -> set of shutdown day indices
        - transition_rules: Dict mapping line -> (prev_grade -> list of allowed next grades)
        - material_running: Dict mapping line -> (grade, expected_days)
        
    Raises:
        DataLoadError: If data is invalid or missing required information
    """
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        excel_file = pd.ExcelFile(uploaded_file)
        
        # Validate required sheets exist
        _validate_sheets(excel_file)
        
        # Load core sheets
        plant_df = pd.read_excel(excel_file, sheet_name=constants.SHEET_PLANT)
        inventory_df = pd.read_excel(excel_file, sheet_name=constants.SHEET_INVENTORY)
        demand_df = pd.read_excel(excel_file, sheet_name=constants.SHEET_DEMAND)
        
        # Validate column names
        _validate_columns(plant_df, inventory_df, demand_df)
        
        # Parse plants/lines
        lines, capacities, material_running = _parse_plant_data(plant_df)
        
        # Parse grades and inventory parameters
        (grades, initial_inventory, min_inventory, max_inventory,
         min_closing_inventory, min_run_days, max_run_days,
         force_start_date, allowed_lines, rerun_allowed) = _parse_inventory_data(
            inventory_df, lines
        )
        
        # Parse demand and establish planning horizon
        dates, demand = _parse_demand_data(demand_df, grades)
        
        # Parse shutdown periods
        shutdown_day_indices = _parse_shutdown_data(plant_df, dates)
        
        # Load transition matrices
        transition_rules = _parse_transition_rules(excel_file, lines, grades)
        
        # Build complete instance
        instance = {
            'grades': grades,
            'lines': lines,
            'dates': dates,
            'capacities': capacities,
            'demand': demand,
            'initial_inventory': initial_inventory,
            'min_inventory': min_inventory,
            'max_inventory': max_inventory,
            'min_closing_inventory': min_closing_inventory,
            'min_run_days': min_run_days,
            'max_run_days': max_run_days,
            'force_start_date': force_start_date,
            'allowed_lines': allowed_lines,
            'rerun_allowed': rerun_allowed,
            'shutdown_day_indices': shutdown_day_indices,
            'transition_rules': transition_rules,
            'material_running': material_running,
        }
        
        # Validate instance integrity
        _validate_instance(instance)
        
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


def _validate_columns(plant_df: pd.DataFrame, 
                     inventory_df: pd.DataFrame,
                     demand_df: pd.DataFrame) -> None:
    """Validate that required columns exist in each sheet."""
    # Plant sheet validation
    required_plant = [constants.PLANT_COLS["name"], constants.PLANT_COLS["capacity"]]
    for col in required_plant:
        if col not in plant_df.columns:
            raise DataLoadError(
                constants.ERROR_MESSAGES["missing_column"].format(col, constants.SHEET_PLANT)
            )
    
    # Inventory sheet validation
    required_inventory = [
        constants.INVENTORY_COLS["grade"], constants.INVENTORY_COLS["opening_inv"],
        constants.INVENTORY_COLS["min_inv"], constants.INVENTORY_COLS["max_inv"],
        constants.INVENTORY_COLS["min_run"], constants.INVENTORY_COLS["max_run"]
    ]
    for col in required_inventory:
        if col not in inventory_df.columns:
            raise DataLoadError(
                constants.ERROR_MESSAGES["missing_column"].format(col, constants.SHEET_INVENTORY)
            )
    
    # Demand sheet should have at least 2 columns (date + at least one grade)
    if len(demand_df.columns) < 2:
        raise DataLoadError("Demand sheet must have at least 2 columns (Date + Grades)")


def _parse_plant_data(plant_df: pd.DataFrame) -> Tuple[List[str], Dict[str, float], Dict[str, Tuple[str, int]]]:
    """
    Parse plant/line data.
    
    Returns:
        - List of line names
        - Dict mapping line -> capacity
        - Dict mapping line -> (material_running, expected_days)
    """
    lines = []
    capacities = {}
    material_running = {}
    
    for _, row in plant_df.iterrows():
        line_name = str(row[constants.PLANT_COLS["name"]]).strip()
        capacity = float(row[constants.PLANT_COLS["capacity"]])
        
        if capacity <= 0:
            raise DataLoadError(constants.ERROR_MESSAGES["capacity_zero"].format(line_name))
        
        if not (constants.MIN_CAPACITY <= capacity <= constants.MAX_CAPACITY):
            st.warning(f"Unusual capacity for {line_name}: {capacity} MT/day")
        
        lines.append(line_name)
        capacities[line_name] = capacity
        
        # Parse material running info (optional)
        if constants.PLANT_COLS["material_running"] in row and constants.PLANT_COLS["expected_days"] in row:
            mat = row[constants.PLANT_COLS["material_running"]]
            exp_days = row[constants.PLANT_COLS["expected_days"]]
            
            if pd.notna(mat) and pd.notna(exp_days):
                try:
                    material_running[line_name] = (str(mat).strip(), int(exp_days))
                except (ValueError, TypeError):
                    pass
    
    if not lines:
        raise DataLoadError(constants.ERROR_MESSAGES["no_plants"])
    
    return lines, capacities, material_running


def _parse_inventory_data(inventory_df: pd.DataFrame, lines: List[str]) -> Tuple:
    """
    Parse inventory and grade parameters.
    
    Returns tuple of:
        - grades list
        - initial_inventory dict
        - min_inventory dict
        - max_inventory dict
        - min_closing_inventory dict
        - min_run_days dict
        - max_run_days dict
        - force_start_date dict
        - allowed_lines dict
        - rerun_allowed dict
    """
    grades = []
    grade_set = set()
    
    initial_inventory = {}
    min_inventory = {}
    max_inventory = {}
    min_closing_inventory = {}
    min_run_days = {}
    max_run_days = {}
    force_start_date = {}
    allowed_lines = {}
    rerun_allowed = {}
    
    for _, row in inventory_df.iterrows():
        grade = str(row[constants.INVENTORY_COLS["grade"]]).strip()
        
        # Parse allowed lines for this row
        lines_value = row.get(constants.INVENTORY_COLS["lines"], None)
        if pd.notna(lines_value) and str(lines_value).strip():
            row_lines = [l.strip() for l in str(lines_value).split(',')]
        else:
            row_lines = lines.copy()
        
        # Initialize grade in allowed_lines dict
        if grade not in allowed_lines:
            allowed_lines[grade] = []
        
        for line in row_lines:
            if line not in lines:
                st.warning(f"Line '{line}' specified for grade '{grade}' not found in Plant sheet")
                continue
            
            if line not in allowed_lines[grade]:
                allowed_lines[grade].append(line)
        
        # Set grade-level parameters (only once per grade)
        if grade not in grade_set:
            grade_set.add(grade)
            grades.append(grade)
            
            initial_inventory[grade] = float(row.get(constants.INVENTORY_COLS["opening_inv"], 0))
            min_inventory[grade] = float(row.get(constants.INVENTORY_COLS["min_inv"], 0))
            max_inventory[grade] = float(row.get(constants.INVENTORY_COLS["max_inv"], 1e9))
            min_closing_inventory[grade] = float(row.get(constants.INVENTORY_COLS["min_closing"], 0))
            
            # Parse force start date
            force_val = row.get(constants.INVENTORY_COLS["force_start"], None)
            if pd.notna(force_val):
                try:
                    force_start_date[grade] = pd.to_datetime(force_val).date()
                except Exception as e:
                    st.warning(f"Invalid force start date for grade '{grade}': {e}")
        
        # Set grade-line specific parameters
        for line in row_lines:
            if line not in lines:
                continue
            
            key = (grade, line)
            min_run_days[key] = int(row.get(constants.INVENTORY_COLS["min_run"], 1))
            max_run_days[key] = int(row.get(constants.INVENTORY_COLS["max_run"], 9999))
            
            # Parse rerun allowed
            rerun_val = row.get(constants.INVENTORY_COLS["rerun"], "Yes")
            if pd.notna(rerun_val):
                rerun_str = str(rerun_val).strip().lower()
                rerun_allowed[key] = rerun_str not in ['no', 'n', 'false', '0']
            else:
                rerun_allowed[key] = True
    
    if not grades:
        raise DataLoadError(constants.ERROR_MESSAGES["no_grades"])
    
    return (grades, initial_inventory, min_inventory, max_inventory,
            min_closing_inventory, min_run_days, max_run_days,
            force_start_date, allowed_lines, rerun_allowed)


def _parse_demand_data(demand_df: pd.DataFrame, grades: List[str]) -> Tuple[List[date], Dict]:
    """
    Parse demand data and establish planning horizon.
    
    Returns:
        - List of date objects
        - Dict mapping (grade, day_index) -> demand
    """
    # First column is dates
    date_col = demand_df.columns[0]
    
    # Convert to datetime
    try:
        dates_series = pd.to_datetime(demand_df[date_col])
        dates = sorted([d.date() for d in dates_series])
    except Exception as e:
        raise DataLoadError(f"Invalid dates in demand sheet: {e}")
    
    if not dates:
        raise DataLoadError("No valid dates found in demand sheet")
    
    # Parse demand for each grade
    demand = {}
    grade_columns = [col for col in demand_df.columns if col != date_col]
    
    for grade in grades:
        if grade not in grade_columns:
            st.warning(f"Grade '{grade}' not found in demand sheet. Setting demand to 0.")
            for d_idx in range(len(dates)):
                demand[(grade, d_idx)] = 0
        else:
            grade_demand = demand_df[grade].fillna(0).tolist()
            for d_idx, qty in enumerate(grade_demand):
                demand[(grade, d_idx)] = float(qty)
    
    return dates, demand


def _parse_shutdown_data(plant_df: pd.DataFrame, dates: List[date]) -> Dict[str, Set[int]]:
    """
    Parse shutdown periods for each plant.
    
    Returns:
        Dict mapping line -> set of day indices during shutdown
    """
    shutdown_day_indices = {}
    
    if constants.PLANT_COLS["shutdown_start"] not in plant_df.columns:
        return {line: set() for line in plant_df[constants.PLANT_COLS["name"]]}
    
    for _, row in plant_df.iterrows():
        line = str(row[constants.PLANT_COLS["name"]]).strip()
        start_val = row.get(constants.PLANT_COLS["shutdown_start"], None)
        end_val = row.get(constants.PLANT_COLS["shutdown_end"], None)
        
        if pd.notna(start_val) and pd.notna(end_val):
            try:
                start_date = pd.to_datetime(start_val).date()
                end_date = pd.to_datetime(end_val).date()
                
                if start_date > end_date:
                    st.warning(f"Shutdown start after end for {line}. Ignoring.")
                    shutdown_day_indices[line] = set()
                    continue
                
                shutdown_indices = set()
                for d_idx, d in enumerate(dates):
                    if start_date <= d <= end_date:
                        shutdown_indices.add(d_idx)
                
                shutdown_day_indices[line] = shutdown_indices
                
                if shutdown_indices:
                    st.info(
                        f"🔧 Shutdown for {line}: "
                        f"{start_date.strftime(constants.DATE_FORMAT_DISPLAY)} to "
                        f"{end_date.strftime(constants.DATE_FORMAT_DISPLAY)} "
                        f"({len(shutdown_indices)} days)"
                    )
            except Exception as e:
                st.warning(f"Error parsing shutdown dates for {line}: {e}")
                shutdown_day_indices[line] = set()
        else:
            shutdown_day_indices[line] = set()
    
    return shutdown_day_indices


def _parse_transition_rules(excel_file: pd.ExcelFile, 
                            lines: List[str], 
                            grades: List[str]) -> Dict[str, Dict[str, List[str]]]:
    """
    Parse transition matrices from sheets named 'Transition_[LineName]'.
    
    Returns:
        Dict mapping line -> (prev_grade -> list of allowed next grades)
    """
    transition_rules = {}
    sheet_names = excel_file.sheet_names
    
    for line in lines:
        # Try multiple naming conventions
        possible_names = [
            f"Transition_{line}",
            f"Transition_{line.replace(' ', '_')}",
            f"Transition{line.replace(' ', '')}",
        ]
        
        found_sheet = None
        for sheet_name in possible_names:
            if sheet_name in sheet_names:
                found_sheet = sheet_name
                break
        
        if found_sheet:
            try:
                trans_df = pd.read_excel(excel_file, sheet_name=found_sheet, index_col=0)
                
                # Build transition rules
                rules = {}
                for prev_grade in trans_df.index:
                    allowed_next = []
                    for curr_grade in trans_df.columns:
                        cell_value = str(trans_df.loc[prev_grade, curr_grade]).lower()
                        if any(yes_val in cell_value for yes_val in constants.TRANSITION_YES_VALUES):
                            allowed_next.append(curr_grade)
                    rules[str(prev_grade)] = allowed_next
                
                transition_rules[line] = rules
                st.info(f"✓ Loaded transition matrix for {line}")
            except Exception as e:
                st.warning(f"Could not load transition matrix for {line}: {e}")
                transition_rules[line] = None
        else:
            transition_rules[line] = None
    
    return transition_rules


def _validate_instance(instance: Dict[str, Any]) -> None:
    """
    Perform final validation checks on the complete instance.
    """
    # Check for empty allowed_lines
    for grade in instance['grades']:
        if not instance['allowed_lines'].get(grade, []):
            raise DataLoadError(f"Grade '{grade}' has no allowed production lines")
    
    # Check demand coverage
    num_days = len(instance['dates'])
    for grade in instance['grades']:
        for d in range(num_days):
            if (grade, d) not in instance['demand']:
                instance['demand'][(grade, d)] = 0.0
    
    # Validate force start dates are within horizon
    for grade, force_date in instance['force_start_date'].items():
        if force_date and force_date not in instance['dates']:
            if force_date < instance['dates'][0]:
                st.warning(f"Force start date for '{grade}' is before planning horizon")
            elif force_date > instance['dates'][-1]:
                st.warning(f"Force start date for '{grade}' is after planning horizon")


def add_buffer_days(instance: Dict[str, Any], buffer_days: int) -> Dict[str, Any]:
    """
    Extend planning horizon by adding buffer days at the end.
    
    Args:
        instance: Problem instance dictionary
        buffer_days: Number of days to add
        
    Returns:
        Modified instance with extended dates and zero demand for buffer period
    """
    if buffer_days <= 0:
        return instance
    
    last_date = instance['dates'][-1]
    original_num_days = len(instance['dates'])
    
    # Extend dates
    for i in range(1, buffer_days + 1):
        instance['dates'].append(last_date + timedelta(days=i))
    
    # Set demand to zero for buffer days
    for grade in instance['grades']:
        for d in range(original_num_days, len(instance['dates'])):
            instance['demand'][(grade, d)] = 0.0
    
    st.info(f"📅 Added {buffer_days} buffer days to planning horizon")
    
    return instance
