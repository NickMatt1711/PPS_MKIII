"""
Excel file loading and validation
"""

import pandas as pd
import io
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import streamlit as st
from constants import REQUIRED_SHEETS, PLANT_COLUMNS, INVENTORY_COLUMNS


class ExcelDataLoader:
    """Handles loading and validation of Excel data"""
    
    def __init__(self, file_buffer: io.BytesIO):
        self.file_buffer = file_buffer
        self.data = {}
        self.errors = []
        self.warnings = []
    
    def load_and_validate(self) -> Tuple[bool, Dict, List[str], List[str]]:
        """Load all sheets and validate structure"""
        try:
            # Load required sheets
            for sheet in REQUIRED_SHEETS:
                try:
                    self.file_buffer.seek(0)
                    df = pd.read_excel(self.file_buffer, sheet_name=sheet)
                    self.data[sheet] = df
                except Exception as e:
                    self.errors.append(f"Missing or invalid sheet '{sheet}': {str(e)}")
                    return False, {}, self.errors, self.warnings
            
            # Load optional transition sheets
            self.file_buffer.seek(0)
            xl_file = pd.ExcelFile(self.file_buffer)
            transition_sheets = [s for s in xl_file.sheet_names if s.startswith('Transition_')]
            
            for sheet in transition_sheets:
                try:
                    self.file_buffer.seek(0)
                    df = pd.read_excel(self.file_buffer, sheet_name=sheet, index_col=0)
                    self.data[sheet] = df
                except Exception as e:
                    self.warnings.append(f"Could not load transition sheet '{sheet}': {str(e)}")
            
            # Validate sheet structures
            self._validate_plant_sheet()
            self._validate_inventory_sheet()
            self._validate_demand_sheet()
            
            if self.errors:
                return False, {}, self.errors, self.warnings
            
            return True, self.data, self.errors, self.warnings
            
        except Exception as e:
            self.errors.append(f"Error loading Excel file: {str(e)}")
            return False, {}, self.errors, self.warnings
    
    def _validate_plant_sheet(self):
        """Validate Plant sheet structure"""
        df = self.data.get('Plant')
        if df is None:
            return
        
        required_cols = [PLANT_COLUMNS['plant'], PLANT_COLUMNS['capacity']]
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            self.errors.append(f"Plant sheet missing columns: {', '.join(missing)}")
        
        # Check for valid capacities
        if PLANT_COLUMNS['capacity'] in df.columns:
            if df[PLANT_COLUMNS['capacity']].isna().any():
                self.errors.append("Plant sheet contains missing capacity values")
            if (df[PLANT_COLUMNS['capacity']] <= 0).any():
                self.errors.append("Plant sheet contains invalid capacity values (must be > 0)")
    
    def _validate_inventory_sheet(self):
        """Validate Inventory sheet structure"""
        df = self.data.get('Inventory')
        if df is None:
            return
        
        required_cols = [INVENTORY_COLUMNS['grade']]
        missing = [col for col in required_cols if col not in df.columns]
        
        if missing:
            self.errors.append(f"Inventory sheet missing columns: {', '.join(missing)}")
    
    def _validate_demand_sheet(self):
        """Validate Demand sheet structure"""
        df = self.data.get('Demand')
        if df is None:
            return
        
        if len(df.columns) < 2:
            self.errors.append("Demand sheet must have at least 2 columns (Date + Grade(s))")
        
        # Check if first column contains dates
        try:
            pd.to_datetime(df.iloc[:, 0])
        except:
            self.errors.append("First column of Demand sheet must contain valid dates")


def process_plant_data(plant_df: pd.DataFrame) -> Dict:
    """Process plant sheet into structured data"""
    result = {
        'lines': list(plant_df[PLANT_COLUMNS['plant']]),
        'capacities': {},
        'material_running': {},
        'shutdown_periods': {},
        'pre_shutdown_grades': {},  # NEW
        'restart_grades': {},       # NEW
    }
    
    for _, row in plant_df.iterrows():
        plant = row[PLANT_COLUMNS['plant']]
        result['capacities'][plant] = row[PLANT_COLUMNS['capacity']]
        
        # Material running info
        if pd.notna(row.get(PLANT_COLUMNS['material_running'])):
            material = str(row[PLANT_COLUMNS['material_running']]).strip()
            
            # Check if expected_days is provided and valid
            if pd.notna(row.get(PLANT_COLUMNS['expected_days'])):
                try:
                    expected_days = int(row[PLANT_COLUMNS['expected_days']])
                except:
                    expected_days = None  # None means not specified (free after day 0)
            else:
                expected_days = None  # None means not specified (free after day 0)
            
            result['material_running'][plant] = (material, expected_days)
        
        # Shutdown periods (will be processed later with dates)
        shutdown_start = row.get(PLANT_COLUMNS['shutdown_start'])
        shutdown_end = row.get(PLANT_COLUMNS['shutdown_end'])
        
        if pd.notna(shutdown_start) and pd.notna(shutdown_end):
            result['shutdown_periods'][plant] = {
                'start': shutdown_start,
                'end': shutdown_end
            }
            
            # NEW: Pre Shutdown Grade - only store if not empty/blank
            pre_shutdown_grade = row.get(PLANT_COLUMNS['pre_shutdown_grade'])
            if pd.notna(pre_shutdown_grade):
                grade_str = str(pre_shutdown_grade).strip()
                if grade_str:  # Only store if not empty after stripping
                    result['pre_shutdown_grades'][plant] = grade_str
            
            # NEW: Restart Grade - only store if not empty/blank
            restart_grade = row.get(PLANT_COLUMNS['restart_grade'])
            if pd.notna(restart_grade):
                grade_str = str(restart_grade).strip()
                if grade_str:  # Only store if not empty after stripping
                    result['restart_grades'][plant] = grade_str
    
    return result


def process_inventory_data(inventory_df: pd.DataFrame, lines: List[str]) -> Dict:
    """Process inventory sheet into structured data"""
    grades = inventory_df[INVENTORY_COLUMNS['grade']].unique().tolist()
    
    result = {
        'grades': grades,
        'initial_inventory': {},
        'min_inventory': {},
        'max_inventory': {},
        'min_closing_inventory': {},
        'min_run_days': {},
        'max_run_days': {},
        'force_start_date': {},
        'allowed_lines': {grade: [] for grade in grades},
        'rerun_allowed': {},
    }
    
    grade_inventory_defined = set()
    
    for _, row in inventory_df.iterrows():
        grade = row[INVENTORY_COLUMNS['grade']]
        
        # Process Lines column
        lines_value = row.get(INVENTORY_COLUMNS['lines'])
        if pd.notna(lines_value) and lines_value != '':
            plants_for_row = [x.strip() for x in str(lines_value).split(',')]
        else:
            plants_for_row = lines
        
        # Add plants to allowed_lines
        for plant in plants_for_row:
            if plant not in result['allowed_lines'][grade]:
                result['allowed_lines'][grade].append(plant)
        
        # Global inventory parameters (only set once per grade)
        if grade not in grade_inventory_defined:
            result['initial_inventory'][grade] = row.get(INVENTORY_COLUMNS['opening'], 0)
            if pd.isna(result['initial_inventory'][grade]):
                result['initial_inventory'][grade] = 0
            
            result['min_inventory'][grade] = row.get(INVENTORY_COLUMNS['min_inv'], 0)
            if pd.isna(result['min_inventory'][grade]):
                result['min_inventory'][grade] = 0
            
            result['max_inventory'][grade] = row.get(INVENTORY_COLUMNS['max_inv'], 1000000000)
            if pd.isna(result['max_inventory'][grade]):
                result['max_inventory'][grade] = 1000000000
            
            result['min_closing_inventory'][grade] = row.get(INVENTORY_COLUMNS['min_closing'], 0)
            if pd.isna(result['min_closing_inventory'][grade]):
                result['min_closing_inventory'][grade] = 0
            
            grade_inventory_defined.add(grade)
        
        # Plant-specific parameters
        for plant in plants_for_row:
            grade_plant_key = (grade, plant)
            
            result['min_run_days'][grade_plant_key] = int(row.get(INVENTORY_COLUMNS['min_run'], 1))
            if pd.isna(result['min_run_days'][grade_plant_key]):
                result['min_run_days'][grade_plant_key] = 1
            
            result['max_run_days'][grade_plant_key] = int(row.get(INVENTORY_COLUMNS['max_run'], 9999))
            if pd.isna(result['max_run_days'][grade_plant_key]):
                result['max_run_days'][grade_plant_key] = 9999
            
            # Force Start Date
            if pd.notna(row.get(INVENTORY_COLUMNS['force_start'])):
                try:
                    result['force_start_date'][grade_plant_key] = pd.to_datetime(
                        row[INVENTORY_COLUMNS['force_start']]
                    ).date()
                except:
                    result['force_start_date'][grade_plant_key] = None
            else:
                result['force_start_date'][grade_plant_key] = None
            
            # Rerun Allowed
            rerun_val = row.get(INVENTORY_COLUMNS['rerun'])
            if pd.notna(rerun_val):
                val_str = str(rerun_val).strip().lower()
                result['rerun_allowed'][grade_plant_key] = val_str not in ['no', 'n', 'false', '0']
            else:
                result['rerun_allowed'][grade_plant_key] = True
    
    return result


def process_demand_data(demand_df: pd.DataFrame, buffer_days: int = 0) -> Tuple[Dict, List, int]:
    """Process demand sheet into structured data"""
    grades = [col for col in demand_df.columns if col != demand_df.columns[0]]
    
    dates = sorted(list(set(demand_df.iloc[:, 0].dt.date.tolist())))
    num_days = len(dates)
    
    # Add buffer days
    last_date = dates[-1]
    for i in range(1, buffer_days + 1):
        dates.append(last_date + timedelta(days=i))
    
    num_days = len(dates)
    
    demand_data = {}
    for grade in grades:
        if grade in demand_df.columns:
            demand_data[grade] = {
                demand_df.iloc[i, 0].date(): demand_df[grade].iloc[i] 
                for i in range(len(demand_df))
            }
        else:
            demand_data[grade] = {date: 0 for date in dates}
    
    # Set buffer days demand to 0
    for grade in grades:
        for date in dates[-buffer_days:]:
            if date not in demand_data[grade]:
                demand_data[grade][date] = 0
    
    return demand_data, dates, num_days


def process_shutdown_dates(shutdown_periods: Dict, dates: List) -> Dict:
    """Convert shutdown start/end dates to day indices"""
    processed = {}
    
    for plant, period in shutdown_periods.items():
        try:
            start_date = pd.to_datetime(period['start']).date()
            end_date = pd.to_datetime(period['end']).date()
            
            if start_date > end_date:
                st.warning(f"⚠️ Invalid shutdown period for {plant}")
                processed[plant] = []
                continue
            
            shutdown_days = []
            for d, date in enumerate(dates):
                if start_date <= date <= end_date:
                    shutdown_days.append(d)
            
            processed[plant] = shutdown_days
            
        except Exception as e:
            st.warning(f"⚠️ Error processing shutdown for {plant}: {e}")
            processed[plant] = []
    
    return processed


def process_transition_rules(transition_dfs: Dict) -> Dict:
    """Process transition matrices - extract plant name from sheet name"""
    transition_rules = {}
    
    for sheet_name, df in transition_dfs.items():
        # Extract plant name from sheet name (e.g., "Transition_Plant1" -> "Plant1")
        if sheet_name.startswith('Transition_'):
            plant_name = sheet_name.replace('Transition_', '')
        else:
            plant_name = sheet_name
        
        if df is not None:
            transition_rules[plant_name] = {}
            for prev_grade in df.index:
                allowed_transitions = []
                for current_grade in df.columns:
                    if str(df.loc[prev_grade, current_grade]).lower() == 'yes':
                        allowed_transitions.append(current_grade)
                transition_rules[plant_name][prev_grade] = allowed_transitions
        else:
            transition_rules[plant_name] = None
    
    return transition_rules
