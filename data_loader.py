# data_loader.py
import pandas as pd
import streamlit as st
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
    return plant_df, inventory_df, demand_df

def find_transition_sheets(xls):
    """
    Return a dict mapping sheet_name -> df where sheet likely contains transition matrix.
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

def load_excel_data(uploaded_file):
    """
    Main function to load and parse Excel data into the instance dictionary.
    Returns instance dict with all necessary data structures.
    """
    uploaded_file.seek(0)
    xls = pd.ExcelFile(uploaded_file)
    
    # Load core sheets
    plant_df, inventory_df, demand_df = load_core_sheets(xls)
    
    # Extract basic data
    lines = list(plant_df['Plant'])
    capacities = {row['Plant']: row['Capacity per day'] for _, row in plant_df.iterrows()}
    
    # Get grades from demand sheet
    grades = [col for col in demand_df.columns if col != demand_df.columns[0]]
    
    # Process dates
    dates = sorted(list(set(demand_df.iloc[:, 0].dt.date.tolist())))
    num_days = len(dates)
    
    # Process demand data
    demand_data = {}
    for grade in grades:
        if grade in demand_df.columns:
            demand_data[grade] = {
                demand_df.iloc[i, 0].date(): demand_df[grade].iloc[i] 
                for i in range(len(demand_df))
            }
        else:
            demand_data[grade] = {date: 0 for date in dates}
    
    # Convert demand to (grade, day_index) format
    demand = {}
    for g in grades:
        for d_idx, date in enumerate(dates):
            demand[(g, d_idx)] = demand_data[g].get(date, 0)
    
    # Process inventory parameters
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
        lines_value = row['Lines']
        if pd.notna(lines_value) and lines_value != '':
            plants_for_row = [x.strip() for x in str(lines_value).split(',')]
        else:
            plants_for_row = lines
            st.warning(f"⚠️ Lines for grade '{grade}' are not specified, allowing all lines")
        
        # Add plants to allowed_lines
        for plant in plants_for_row:
            if plant not in allowed_lines[grade]:
                allowed_lines[grade].append(plant)
        
        # Global inventory parameters (only set once per grade)
        if grade not in grade_inventory_defined:
            initial_inventory[grade] = row.get('Opening Inventory', 0) if pd.notna(row.get('Opening Inventory')) else 0
            min_inventory[grade] = row.get('Min. Inventory', 0) if pd.notna(row.get('Min. Inventory')) else 0
            max_inventory[grade] = row.get('Max. Inventory', 1000000000) if pd.notna(row.get('Max. Inventory')) else 1000000000
            min_closing_inventory[grade] = row.get('Min. Closing Inventory', 0) if pd.notna(row.get('Min. Closing Inventory')) else 0
            grade_inventory_defined.add(grade)
        
        # Plant-specific parameters
        for plant in plants_for_row:
            grade_plant_key = (grade, plant)
            
            min_run_days[grade_plant_key] = int(row.get('Min. Run Days', 1)) if pd.notna(row.get('Min. Run Days')) else 1
            max_run_days[grade_plant_key] = int(row.get('Max. Run Days', 9999)) if pd.notna(row.get('Max. Run Days')) else 9999
            
            # Force Start Date
            if pd.notna(row.get('Force Start Date')):
                try:
                    force_start_date[grade_plant_key] = pd.to_datetime(row['Force Start Date']).date()
                except:
                    force_start_date[grade_plant_key] = None
                    st.warning(f"⚠️ Invalid Force Start Date for grade '{grade}' on plant '{plant}'")
            else:
                force_start_date[grade_plant_key] = None
            
            # Rerun Allowed
            rerun_val = row.get('Rerun Allowed')
            if pd.notna(rerun_val):
                val_str = str(rerun_val).strip().lower()
                rerun_allowed[grade_plant_key] = val_str not in ['no', 'n', 'false', '0']
            else:
                rerun_allowed[grade_plant_key] = True
    
    # Process shutdown dates
    shutdown_day_indices = {}
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
                    shutdown_day_indices[plant] = set()
                    continue
                
                shutdown_days = set()
                for d, date in enumerate(dates):
                    if start_date <= date <= end_date:
                        shutdown_days.add(d)
                
                if shutdown_days:
                    shutdown_day_indices[plant] = shutdown_days
                    st.info(f"🔧 Shutdown scheduled for {plant}: {start_date.strftime('%d-%b-%y')} to {end_date.strftime('%d-%b-%y')} ({len(shutdown_days)} days)")
                else:
                    shutdown_day_indices[plant] = set()
                    st.info(f"ℹ️ Shutdown period for {plant} is outside planning horizon")
                    
            except Exception as e:
                st.warning(f"⚠️ Invalid shutdown dates for {plant}: {e}")
                shutdown_day_indices[plant] = set()
        else:
            shutdown_day_indices[plant] = set()
    
    # Process transition rules
    transition_sheets = find_transition_sheets(xls)
    transition_rules = {}
    
    for sheet_name, df in transition_sheets.items():
        if df is None:
            continue
        
        # Try to match sheet name to plant
        matched_plant = None
        for plant in lines:
            if plant.lower() in sheet_name.lower():
                matched_plant = plant
                break
        
        if matched_plant:
            transition_rules[matched_plant] = {}
            for prev_grade in df.index:
                allowed_transitions = []
                for current_grade in df.columns:
                    try:
                        if str(df.loc[prev_grade, current_grade]).lower() == 'yes':
                            allowed_transitions.append(current_grade)
                    except:
                        pass
                transition_rules[matched_plant][prev_grade] = allowed_transitions
    
    # Material running info
    material_running_info = {}
    for _, row in plant_df.iterrows():
        plant = row['Plant']
        material = row.get('Material Running')
        expected_days = row.get('Expected Run Days')
        
        if pd.notna(material) and pd.notna(expected_days):
            try:
                material_running_info[plant] = (str(material).strip(), int(expected_days))
            except (ValueError, TypeError):
                st.warning(f"⚠️ Invalid Material Running or Expected Run Days for plant '{plant}'")
    
    # Build instance dictionary
    instance = {
        'grades': grades,
        'lines': lines,
        'dates': dates,
        'num_days': num_days,
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
        'material_running_info': material_running_info,
        # Store original dataframes for preview
        'plant_df': plant_df,
        'inventory_df': inventory_df,
        'demand_df': demand_df
    }
    
    return instance
