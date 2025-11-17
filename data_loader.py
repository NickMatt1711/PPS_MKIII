# data_loader.py
import pandas as pd
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
    Strategy:
      - Identify all sheets with the word 'transition' in their name (case-insensitive)
      - Try to map each Plant name to an appropriate transition sheet by matching plant name in sheet name.
      - If a transition sheet doesn't mention plant name, it may still be a generic transition matrix; we include it under a special key.
    """
    all_names = xls.sheet_names
    transition_sheets = [s for s in all_names if TRANSITION_KEYWORD in s.lower()]
    # load all transition sheets into dict keyed by sheet_name
    loaded = {}
    for s in transition_sheets:
        try:
            df = pd.read_excel(xls, sheet_name=s, index_col=0)
            loaded[s] = df
        except Exception:
            # fallback: try without index_col
            try:
                df = pd.read_excel(xls, sheet_name=s)
                loaded[s] = df
            except Exception:
                loaded[s] = None
    return loaded

# NEW: Enhanced data processing function
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
        # Higher penalties for critical grades
        if grade in ['BOPP', 'TQPP']:
            min_inv_penalty[grade] = 8
            min_closing_penalty[grade] = 12
        else:
            min_inv_penalty[grade] = 5
            min_closing_penalty[grade] = 8
    
    return rerun_allowed, min_inv_penalty, min_closing_penalty
