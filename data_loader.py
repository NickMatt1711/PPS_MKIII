# data_loader.py
import pandas as pd
from datetime import timedelta
from constants import TRANSITION_KEYWORD

def read_workbook_bytes(io_bytes):
    """
    Return a pandas.ExcelFile object for a bytes-like IO (BytesIO).
    """
    return pd.ExcelFile(io_bytes)

def load_core_sheets(xls):
    """
    Expects a pandas.ExcelFile (or file-like path). Returns plant_df, inventory_df, demand_df.
    Raises ValueError with readable message if missing.
    """
    names = xls.sheet_names
    if 'Plant' not in names:
        raise ValueError("Missing 'Plant' sheet in workbook.")
    if 'Inventory' not in names:
        raise ValueError("Missing 'Inventory' sheet in workbook.")
    if 'Demand' not in names:
        raise ValueError("Missing 'Demand' sheet in workbook.")
    
    plant_df = pd.read_excel(xls, sheet_name='Plant')
    inventory_df = pd.read_excel(xls, sheet_name='Inventory')
    demand_df = pd.read_excel(xls, sheet_name='Demand')
    
    # Basic validation
    if plant_df.empty:
        raise ValueError("Plant sheet is empty")
    if inventory_df.empty:
        raise ValueError("Inventory sheet is empty")
    if demand_df.empty:
        raise ValueError("Demand sheet is empty")
    
    return plant_df, inventory_df, demand_df

def find_transition_sheets(xls):
    """
    Return a dict mapping plant_name -> (sheet_name, df) where sheet likely contains transition matrix.
    """
    all_names = xls.sheet_names
    transition_sheets = [s for s in all_names if TRANSITION_KEYWORD in s.lower()]
    
    loaded = {}
    for s in transition_sheets:
        try:
            df = pd.read_excel(xls, sheet_name=s, index_col=0)
            loaded[s] = df
        except Exception:
            try:
                df = pd.read_excel(xls, sheet_name=s)
                loaded[s] = df
            except Exception:
                loaded[s] = None
    return loaded

def process_shutdown_dates(plant_df, dates):
    """Process shutdown dates for each plant"""
    shutdown_periods = {}
    
    for index, row in plant_df.iterrows():
        plant = row['Plant']
        shutdown_start = row.get('Shutdown Start Date')
        shutdown_end = row.get('Shutdown End Date')
        
        # Check if both start and end dates are provided
        if pd.notna(shutdown_start) and pd.notna(shutdown_end):
            try:
                start_date = pd.to_datetime(shutdown_start).date()
                end_date = pd.to_datetime(shutdown_end).date()
                
                # Validate date range
                if start_date > end_date:
                    shutdown_periods[plant] = []
                    continue
                
                # Find day indices for shutdown period
                shutdown_days = []
                for d, date in enumerate(dates):
                    if start_date <= date <= end_date:
                        shutdown_days.append(d)
                
                if shutdown_days:
                    shutdown_periods[plant] = shutdown_days
                else:
                    shutdown_periods[plant] = []
                    
            except Exception as e:
                shutdown_periods[plant] = []
        else:
            shutdown_periods[plant] = []
    
    return shutdown_periods

def load_excel_data(uploaded_file):
    """
    Main function to load and process Excel data into instance dict
    """
    xls = read_workbook_bytes(uploaded_file)
    plant_df, inventory_df, demand_df = load_core_sheets(xls)
    transition_map = find_transition_sheets(xls)
    
    # Process plant data
    lines = list(plant_df['Plant'])
    capacities = {row['Plant']: row['Capacity per day'] for index, row in plant_df.iterrows()}
    
    # Process material running info
    material_running_info = {}
    for index, row in plant_df.iterrows():
        plant = row['Plant']
        material = row.get('Material Running')
        expected_days = row.get('Expected Run Days')
        
        if pd.notna(material) and pd.notna(expected_days):
            try:
                material_running_info[plant] = (str(material).strip(), int(expected_days))
            except (ValueError, TypeError):
                material_running_info[plant] = (None, 0)
    
    # Process demand data to get grades and dates
    grades = [col for col in demand_df.columns if col != demand_df.columns[0]]
    dates = sorted(list(set(demand_df.iloc[:, 0].dt.date.tolist())))
    
    # Process demand into proper format
    demand_data = {}
    for grade in grades:
        if grade in demand_df.columns:
            demand_data[grade] = {}
            for i in range(len(demand_df)):
                date = demand_df.iloc[i, 0].date()
                demand_val = demand_df[grade].iloc[i]
                if pd.notna(demand_val):
                    demand_data[grade][date] = demand_val
                else:
                    demand_data[grade][date] = 0
        else:
            demand_data[grade] = {date: 0 for date in dates}
    
    # Process inventory data with grade-plant combinations
    initial_inventory = {}
    min_inventory = {}
    max_inventory = {}
    min_closing_inventory = {}
    min_run_days = {}
    max_run_days = {}
    force_start_date = {}
    allowed_lines = {grade: [] for grade in grades}
    rerun_allowed = {}
    
    # Track which grades have global inventory settings defined
    grade_inventory_defined = set()
    
    for index, row in inventory_df.iterrows():
        grade = row['Grade Name']
        
        # Process Lines column
        lines_value = row['Lines']
        if pd.notna(lines_value) and lines_value != '':
            plants_for_row = [x.strip() for x in str(lines_value).split(',')]
        else:
            plants_for_row = lines
        
        # Add plants to allowed_lines for this grade
        for plant in plants_for_row:
            if plant not in allowed_lines[grade]:
                allowed_lines[grade].append(plant)
        
        # Global inventory parameters (only set once per grade)
        if grade not in grade_inventory_defined:
            if pd.notna(row['Opening Inventory']):
                initial_inventory[grade] = row['Opening Inventory']
            else:
                initial_inventory[grade] = 0
            
            if pd.notna(row['Min. Inventory']):
                min_inventory[grade] = row['Min. Inventory']
            else:
                min_inventory[grade] = 0
            
            if pd.notna(row['Max. Inventory']):
                max_inventory[grade] = row['Max. Inventory']
            else:
                max_inventory[grade] = 1000000
            
            if pd.notna(row['Min. Closing Inventory']):
                min_closing_inventory[grade] = row['Min. Closing Inventory']
            else:
                min_closing_inventory[grade] = 0
            
            grade_inventory_defined.add(grade)
        
        # Plant-specific parameters
        for plant in plants_for_row:
            grade_plant_key = (grade, plant)
            
            # Min Run Days
            if pd.notna(row['Min. Run Days']):
                min_run_days[grade_plant_key] = int(row['Min. Run Days'])
            else:
                min_run_days[grade_plant_key] = 1
            
            # Max Run Days
            if pd.notna(row['Max. Run Days']):
                max_run_days[grade_plant_key] = int(row['Max. Run Days'])
            else:
                max_run_days[grade_plant_key] = 9999
            
            # Force Start Date
            if pd.notna(row['Force Start Date']):
                try:
                    force_start_date[grade_plant_key] = pd.to_datetime(row['Force Start Date']).date()
                except:
                    force_start_date[grade_plant_key] = None
            else:
                force_start_date[grade_plant_key] = None
            
            # Rerun Allowed parsing
            rerun_val = row['Rerun Allowed']
            if pd.notna(rerun_val):
                val_str = str(rerun_val).strip().lower()
                if val_str in ['no', 'n', 'false', '0']:
                    rerun_allowed[grade_plant_key] = False
                else:
                    rerun_allowed[grade_plant_key] = True
            else:
                rerun_allowed[grade_plant_key] = True
    
    # Process shutdown periods
    shutdown_periods = process_shutdown_dates(plant_df, dates)
    
    # Process transition rules
    transition_rules = {}
    for plant_name in lines:
        # Find transition sheet for this plant
        transition_df = None
        for sheet_name, df in transition_map.items():
            if plant_name.lower() in sheet_name.lower():
                transition_df = df
                break
        
        if transition_df is not None:
            transition_rules[plant_name] = {}
            for prev_grade in transition_df.index:
                allowed_transitions = []
                for current_grade in transition_df.columns:
                    if str(transition_df.loc[prev_grade, current_grade]).lower() == 'yes':
                        allowed_transitions.append(current_grade)
                transition_rules[plant_name][prev_grade] = allowed_transitions
        else:
            transition_rules[plant_name] = None
    
    # Convert demand data to solver format (grade, day_index) -> demand
    demand_solver_format = {}
    for grade in grades:
        for d, date in enumerate(dates):
            demand_solver_format[(grade, d)] = demand_data[grade].get(date, 0)
    
    # Create instance dictionary
    instance = {
        'grades': grades,
        'lines': lines,
        'dates': dates,
        'capacities': capacities,
        'initial_inventory': initial_inventory,
        'min_inventory': min_inventory,
        'max_inventory': max_inventory,
        'min_closing_inventory': min_closing_inventory,
        'demand': demand_solver_format,
        'allowed_lines': allowed_lines,
        'min_run_days': min_run_days,
        'max_run_days': max_run_days,
        'force_start_date': force_start_date,
        'rerun_allowed': rerun_allowed,
        'shutdown_day_indices': shutdown_periods,
        'transition_rules': transition_rules,
        'material_running_info': material_running_info,
        
        # Keep original dataframes for preview
        'plant_df': plant_df,
        'inventory_df': inventory_df,
        'demand_df': demand_df,
        'transition_map': transition_map,
    }
    
    return instance
