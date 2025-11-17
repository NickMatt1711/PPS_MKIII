# data_loader.py
import pandas as pd
from datetime import datetime
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

def process_rerun_and_penalty_data(inventory_df):
    """
    Process Rerun Allowed rules and set up penalty parameters.
    Returns rerun_allowed dict and penalty dicts.
    """
    rerun_allowed = {}
    min_inv_penalty = {}
    min_closing_penalty = {}
    
    for _, row in inventory_df.iterrows():
        grade = row['Grade Name']
        rerun_allowed[grade] = row.get('Rerun Allowed', 'Yes') == 'Yes'
        
        # Set penalty weights based on business importance
        if grade in ['BOPP', 'TQPP']:
            min_inv_penalty[grade] = 8
            min_closing_penalty[grade] = 12
        else:
            min_inv_penalty[grade] = 5
            min_closing_penalty[grade] = 8
    
    return rerun_allowed, min_inv_penalty, min_closing_penalty

def load_excel_data(uploaded_file):
    """
    Main function to load and process all Excel data into instance dictionary.
    """
    xls = read_workbook_bytes(uploaded_file)
    plant_df, inventory_df, demand_df = load_core_sheets(xls)
    transition_sheets = find_transition_sheets(xls)
    
    # Process plant data
    plants = plant_df['Plant'].tolist()
    capacities = dict(zip(plant_df['Plant'], plant_df['Capacity per day']))
    
    # Process shutdown periods
    shutdown_day_indices = {}
    dates = pd.to_datetime(demand_df['Date']).tolist()
    num_days = len(dates)
    
    for _, plant_row in plant_df.iterrows():
        plant = plant_row['Plant']
        shutdown_start = plant_row.get('Shutdown Start Date')
        shutdown_end = plant_row.get('Shutdown End Date')
        
        if pd.notna(shutdown_start) and pd.notna(shutdown_end):
            shutdown_start = pd.to_datetime(shutdown_start)
            shutdown_end = pd.to_datetime(shutdown_end)
            shutdown_days = []
            for i, date in enumerate(dates):
                if shutdown_start <= date <= shutdown_end:
                    shutdown_days.append(i)
            shutdown_day_indices[plant] = set(shutdown_days)
    
    # Process inventory data
    grades = inventory_df['Grade Name'].tolist()
    initial_inventory = dict(zip(inventory_df['Grade Name'], inventory_df['Opening Inventory']))
    min_inventory = dict(zip(inventory_df['Grade Name'], inventory_df['Min. Inventory']))
    max_inventory = dict(zip(inventory_df['Grade Name'], inventory_df['Max. Inventory']))
    min_closing_inventory = dict(zip(inventory_df['Grade Name'], inventory_df['Min. Closing Inventory']))
    min_run_days = {}
    max_run_days = {}
    
    # Process allowed lines
    allowed_lines = {}
    for _, row in inventory_df.iterrows():
        grade = row['Grade Name']
        lines_str = row.get('Lines', '')
        if pd.notna(lines_str):
            allowed_lines[grade] = [line.strip() for line in str(lines_str).split(',')]
        else:
            allowed_lines[grade] = plants  # Default to all plants
        
        # Process run days per plant
        min_run = row.get('Min. Run Days', 1)
        max_run = row.get('Max. Run Days', num_days)
        for plant in allowed_lines[grade]:
            min_run_days[(grade, plant)] = min_run
            max_run_days[(grade, plant)] = max_run
    
    # Process demand data
    demand = {}
    for _, row in demand_df.iterrows():
        date_idx = dates.index(pd.to_datetime(row['Date']))
        for grade in grades:
            demand[(grade, date_idx)] = row[grade]
    
    # Process transition rules
    transition_rules = {}
    for sheet_name, df in transition_sheets.items():
        plant_name = sheet_name.replace('Transition_', '').replace('transition_', '')
        if plant_name not in plants:
            plant_name = sheet_name  # Use sheet name as fallback
        
        rules = {}
        for from_grade in df.index:
            allowed_next = []
            for to_grade in df.columns:
                if df.loc[from_grade, to_grade] in ['Yes', True, 1, '1']:
                    allowed_next.append(to_grade)
            rules[from_grade] = allowed_next
        transition_rules[plant_name] = rules
    
    # Process rerun and penalty data
    rerun_allowed, min_inv_penalty, min_closing_penalty = process_rerun_and_penalty_data(inventory_df)
    
    # Build instance dictionary
    instance = {
        'plants': plants,
        'grades': grades,
        'dates': dates,
        'capacities': capacities,
        'initial_inventory': initial_inventory,
        'min_inventory': min_inventory,
        'max_inventory': max_inventory,
        'min_closing_inventory': min_closing_inventory,
        'min_run_days': min_run_days,
        'max_run_days': max_run_days,
        'demand': demand,
        'allowed_lines': allowed_lines,
        'transition_rules': transition_rules,
        'shutdown_day_indices': shutdown_day_indices,
        'rerun_allowed': rerun_allowed,
        'min_inv_penalty': min_inv_penalty,
        'min_closing_penalty': min_closing_penalty,
        # Keep dataframes for preview
        'plant_df': plant_df,
        'inventory_df': inventory_df,
        'demand_df': demand_df
    }
    
    return instance
