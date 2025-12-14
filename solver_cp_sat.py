"""
CP-SAT Solver for Polymer Production Optimization
Refactored to strictly adhere to production rules and constraints.
"""

from ortools.sat.python import cp_model
import pandas as pd
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple

# Constants for Optimization Weights (Can be tuned)
WEIGHT_STOCKOUT = 10000        # Highest priority: Avoid missing demand
WEIGHT_TRANSITION = 500        # Medium priority: Minimize changeovers
WEIGHT_MIN_INV_VIOLATION = 50  # Low priority: Try to keep buffer stock
WEIGHT_CLOSING_INV = 100       # Medium-Low: Hit end-of-period targets
WEIGHT_LOW_DEMAND_STOCKOUT_MULTIPLIER = 1.2 # Slightly higher penalty to ensure low demand items aren't ignored

class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Callback to capture solutions during search."""
    
    def __init__(self, variables, grades, lines, dates, num_days):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.vars = variables
        self.grades = grades
        self.lines = lines
        self.dates = dates
        self.num_days = num_days
        self.start_time = time.time()
        self.solutions = []
        self.best_objective = float('inf')

    def on_solution_callback(self):
        obj = self.ObjectiveValue()
        if obj < self.best_objective:
            self.best_objective = obj
        
        # We only store the basic structure here to be processed later
        # due to memory/performance in the callback loop
        pass

def extract_solution(solver, variables, grades, lines, dates, num_days):
    """Extracts the solution data from the solver into a structured dictionary."""
    
    production_schedule = []
    inventory_levels = {g: {} for g in grades}
    stockouts = {g: {} for g in grades}
    
    # 1. Extract Production Data
    for d_idx, date_obj in enumerate(dates):
        date_str = date_obj.strftime("%Y-%m-%d")
        
        for line in lines:
            produced_grade = None
            qty = 0
            
            # Check which grade is produced
            for grade in grades:
                if solver.Value(variables['is_producing'][grade, line, d_idx]):
                    produced_grade = grade
                    qty = solver.Value(variables['production_qty'][grade, line, d_idx])
                    break
            
            production_schedule.append({
                'Date': date_str,
                'Plant': line,
                'Grade': produced_grade if produced_grade else "None",
                'Quantity': qty
            })

        # 2. Extract Inventory & Stockout Data
        for grade in grades:
            inv_val = solver.Value(variables['inventory'][grade, d_idx])
            stock_val = solver.Value(variables['stockout'][grade, d_idx])
            
            inventory_levels[grade][date_str] = inv_val
            stockouts[grade][date_str] = stock_val

    return {
        "production_schedule": pd.DataFrame(production_schedule),
        "inventory": inventory_levels,
        "stockout": stockouts,
        "objective_value": solver.ObjectiveValue()
    }

def build_and_solve_model(
    df_plant: pd.DataFrame,
    df_inventory: pd.DataFrame,
    df_demand: pd.DataFrame,
    transition_rules: Dict,
    shutdown_periods: Dict,
    params: Dict
) -> Dict:
    """
    Main function to build and solve the CP-SAT model.
    """
    model = cp_model.CpModel()
    
    # ---------------------------------------------------------
    # 1. Data Preprocessing & Indexing
    # ---------------------------------------------------------
    
    # Dates
    dates = pd.to_datetime(df_demand['Date']).dt.date.tolist()
    num_days = len(dates)
    date_to_idx = {d: i for i, d in enumerate(dates)}
    
    # Grades & Lines
    grades = [c for c in df_demand.columns if c != 'Date']
    lines = df_plant['Plant'].tolist()
    
    # Lookups
    plant_info = df_plant.set_index('Plant').to_dict('index')
    inv_info = df_inventory.set_index('Grade Name').to_dict('index')
    
    # Calculate Total Demand per grade (for prioritization)
    total_demand = {g: df_demand[g].sum() for g in grades}
    
    # ---------------------------------------------------------
    # 2. Variables
    # ---------------------------------------------------------
    
    V = {} # Container for all variables
    
    # X[g, l, d]: Binary, 1 if grade g is produced on line l at day d
    V['is_producing'] = {}
    
    # P[g, l, d]: Integer, Production quantity
    V['production_qty'] = {}
    
    # S[g, l, d]: Binary, 1 if a campaign of grade g STARTS on line l at day d
    V['start_campaign'] = {}
    
    # I[g, d]: Continuous(Int), Inventory of grade g at end of day d
    V['inventory'] = {}
    
    # O[g, d]: Continuous(Int), Stockout quantity of grade g at end of day d
    V['stockout'] = {}
    
    # T[l, d]: Binary, 1 if a transition occurs on line l at day d
    V['transition'] = {}

    max_capacity = max(p['Capacity per day'] for p in plant_info.values())
    max_inv_global = max(i.get('Max. Inventory', 1000000) for i in inv_info.values())
    
    # --- Create Variables ---
    for d in range(num_days):
        for line in lines:
            # Transitions variables (from day d-1 to d)
            if d > 0:
                V['transition'][line, d] = model.NewBoolVar(f'trans_{line}_{d}')
            
            for grade in grades:
                V['is_producing'][grade, line, d] = model.NewBoolVar(f'x_{grade}_{line}_{d}')
                V['production_qty'][grade, line, d] = model.NewIntVar(0, int(plant_info[line]['Capacity per day']), f'p_{grade}_{line}_{d}')
                V['start_campaign'][grade, line, d] = model.NewBoolVar(f'start_{grade}_{line}_{d}')

        for grade in grades:
            # Inventory can range from 0 to Max (Hard Constraint 5)
            max_inv = int(inv_info.get(grade, {}).get('Max. Inventory', max_inv_global))
            V['inventory'][grade, d] = model.NewIntVar(0, max_inv, f'inv_{grade}_{d}')
            
            # Stockout allows arbitrary deficit (to be minimized)
            V['stockout'][grade, d] = model.NewIntVar(0, 1000000, f'stockout_{grade}_{d}')

    # ---------------------------------------------------------
    # 3. Hard Constraints
    # ---------------------------------------------------------
    
    for d in range(num_days):
        # --- Plant Constraints ---
        for line in lines:
            capacity = int(plant_info[line]['Capacity per day'])
            
            # Check Shutdowns (Rule 16 partial)
            is_shutdown = d in shutdown_periods.get(line, [])
            
            if is_shutdown:
                # Force everything to 0 on shutdown
                for grade in grades:
                    model.Add(V['is_producing'][grade, line, d] == 0)
                    model.Add(V['production_qty'][grade, line, d] == 0)
            else:
                # At most one grade per line per day
                model.Add(sum(V['is_producing'][grade, line, d] for grade in grades) <= 1)
                
                # Link Production Qty to Binary Variable (Rule 16: Full Capacity)
                for grade in grades:
                    # If producing, Qty = Capacity. If not, Qty = 0.
                    model.Add(V['production_qty'][grade, line, d] == capacity * V['is_producing'][grade, line, d])

        # --- Inventory Balance (Rule 2, 12) ---
        for grade in grades:
            demand = int(df_demand.iloc[d][grade])
            
            # Calculate Total Production of this grade across all lines
            total_prod_today = sum(V['production_qty'][grade, line, d] for line in lines)
            
            prev_inv = 0
            if d == 0:
                # Rule 2: Opening Inventory
                prev_inv = int(inv_info.get(grade, {}).get('Opening Inventory', 0))
            else:
                prev_inv = V['inventory'][grade, d - 1]
            
            # Balance Equation: Inv[d] = Inv[d-1] + Prod[d] - Demand[d] + Stockout[d]
            # (Stockout acts as a virtual supply to satisfy demand mathematically, but is penalized)
            # Rearranged: Inv[d] - Stockout[d] = Prev_Inv + Prod - Demand
            model.Add(
                V['inventory'][grade, d] - V['stockout'][grade, d] == 
                prev_inv + total_prod_today - demand
            )

    # --- Line Capabilities (Rule 9) ---
    for grade in grades:
        allowed_lines_str = str(inv_info.get(grade, {}).get('Lines', '')).replace(" ", "")
        allowed_lines = allowed_lines_str.split(',') if allowed_lines_str and allowed_lines_str != 'nan' else lines
        
        for line in lines:
            if line not in allowed_lines:
                # Forbidden line for this grade
                for d in range(num_days):
                    model.Add(V['is_producing'][grade, line, d] == 0)

    # --- Campaign Start Logic ---
    for line in lines:
        for grade in grades:
            # Day 0 start logic
            model.Add(V['start_campaign'][grade, line, 0] == V['is_producing'][grade, line, 0])
            
            for d in range(1, num_days):
                # Start = 1 iff Producing[d]=1 AND Producing[d-1]=0
                # Using OnlyEnforceIf logic
                is_prod = V['is_producing'][grade, line, d]
                was_prod = V['is_producing'][grade, line, d-1]
                
                # start >= is_prod - was_prod
                model.Add(V['start_campaign'][grade, line, d] >= is_prod - was_prod)
                # Ensure start is 0 if not actually starting (optimization naturally drives this low, but good to be explicit)
                model.Add(V['start_campaign'][grade, line, d] <= is_prod) 
                
    # --- Min/Max Run Days (Rules 6 & 7) ---
    for grade in grades:
        min_run = int(inv_info.get(grade, {}).get('Min. Run Days', 1))
        max_run = int(inv_info.get(grade, {}).get('Max. Run Days', num_days))
        
        for line in lines:
            for d in range(num_days):
                
                # Min Run Constraints
                if V['start_campaign'][grade, line, d]:
                    # If started on day d, must produce for min_run days (or until end of horizon)
                    limit = min(d + min_run, num_days)
                    for k in range(d, limit):
                        # Implication: if start=1, then is_producing[d+k]=1
                        model.Add(V['is_producing'][grade, line, k] == 1).OnlyEnforceIf(V['start_campaign'][grade, line, d])

                # Max Run Constraints (Rolling Window)
                # Sum of production in any window of size (max_run + 1) must be <= max_run
                if d + max_run + 1 <= num_days:
                    window = [V['is_producing'][grade, line, k] for k in range(d, d + max_run + 1)]
                    model.Add(sum(window) <= max_run)

    # --- Rerun Allowed (Rule 10) ---
    for grade in grades:
        rerun = str(inv_info.get(grade, {}).get('Rerun Allowed', 'Yes')).lower()
        if rerun == 'no':
            for line in lines:
                # Sum of starts <= 1
                model.Add(sum(V['start_campaign'][grade, line, d] for d in range(num_days)) <= 1)

    # --- Force Start Date (Rule 8) ---
    for grade in grades:
        force_date_raw = inv_info.get(grade, {}).get('Force Start Date')
        if pd.notna(force_date_raw):
            try:
                # Handle different date formats or timestamp objects
                if isinstance(force_date_raw, (pd.Timestamp, str)):
                    force_date = pd.to_datetime(force_date_raw).date()
                    if force_date in date_to_idx:
                        f_idx = date_to_idx[force_date]
                        # Must be produced on at least one allowed line on this date
                        # Check allowed lines first
                        allowed_lines_str = str(inv_info.get(grade, {}).get('Lines', '')).replace(" ", "")
                        allowed = allowed_lines_str.split(',') if allowed_lines_str and allowed_lines_str != 'nan' else lines
                        
                        model.Add(sum(V['is_producing'][grade, l, f_idx] for l in lines if l in allowed) >= 1)
            except:
                pass # Ignore invalid dates

    # --- Material Running & Expected Run Days (Rule 1) ---
    for line in lines:
        p_data = plant_info[line]
        running_grade = p_data.get('Material Running')
        exp_days = p_data.get('Expected Run Days')
        
        if pd.notna(running_grade) and running_grade in grades:
            # Clean exp_days
            if pd.isna(exp_days) or exp_days == 0:
                run_len = 0 # Treated as "Start here, optimize rest"
            else:
                run_len = int(exp_days)

            if run_len > 0:
                # Case A: Explicit Run Days
                # 1. Force production for these days
                limit = min(run_len, num_days)
                for d in range(limit):
                    model.Add(V['is_producing'][running_grade, line, d] == 1)
                
                # 2. Mandatory Changeover (Crucial Rule 1 requirement)
                # "Material... produced for EXACTLY those many days... changeover shall start on day N+1"
                if run_len < num_days:
                    model.Add(V['is_producing'][running_grade, line, run_len] == 0)
                    
            else:
                # Case B: Just start on Day 1 (Index 0)
                model.Add(V['is_producing'][running_grade, line, 0] == 1)
                # Solver decides length based on min/max run days and demand

    # --- Transitions (Rule 11) ---
    for line in lines:
        t_matrix = transition_rules.get(line)
        if not t_matrix:
            continue
            
        for d in range(1, num_days):
            # If line is NOT idle on d-1 and NOT idle on d
            # And Grade(d-1) != Grade(d) -> Transition
            
            for g_from in grades:
                for g_to in grades:
                    if g_from == g_to:
                        continue
                        
                    # Get transition allowed status
                    allowed_list = t_matrix.get(g_from, [])
                    is_allowed = g_to in allowed_list
                    
                    # Variables for logic
                    prod_prev = V['is_producing'][g_from, line, d-1]
                    prod_curr = V['is_producing'][g_to, line, d]
                    
                    if not is_allowed:
                        # Hard Constraint: Forbidden Transition
                        # Cannot produce G_from yesterday AND G_to today
                        model.Add(prod_prev + prod_curr <= 1)
                    else:
                        # Soft Constraint: Allowed but penalized
                        # If switch happens, increment transition counter
                        # T >= prod_prev + prod_curr - 1
                        # If both 1, T >= 1.
                        model.Add(V['transition'][line, d] >= prod_prev + prod_curr - 1)

    # ---------------------------------------------------------
    # 4. Objective Function (Soft Constraints)
    # ---------------------------------------------------------
    objective_terms = []
    
    # A. Minimize Stockouts (Rule 13, 14)
    for grade in grades:
        is_low_demand = total_demand[grade] < (sum(total_demand.values()) / len(grades) * 0.5)
        penalty_mult = WEIGHT_LOW_DEMAND_STOCKOUT_MULTIPLIER if is_low_demand else 1.0
        
        for d in range(num_days):
            objective_terms.append(V['stockout'][grade, d] * int(WEIGHT_STOCKOUT * penalty_mult))

    # B. Minimize Transitions (Rule 11, 13)
    for line in lines:
        for d in range(1, num_days):
            objective_terms.append(V['transition'][line, d] * WEIGHT_TRANSITION)

    # C. Min Daily Inventory (Rule 4)
    # Soft constraint: Penalty if Inventory < Min Inventory
    for grade in grades:
        min_inv = int(inv_info.get(grade, {}).get('Min. Inventory', 0))
        if min_inv > 0:
            for d in range(num_days):
                # Create a slack variable for violation
                violation = model.NewIntVar(0, max_inv_global, f'min_inv_viol_{grade}_{d}')
                # violation >= Min - Actual
                model.Add(violation >= min_inv - V['inventory'][grade, d])
                objective_terms.append(violation * WEIGHT_MIN_INV_VIOLATION)

    # D. Min Closing Inventory (Rule 3)
    # Check only on the last day
    for grade in grades:
        min_closing = int(inv_info.get(grade, {}).get('Min. Closing Inventory', 0))
        if min_closing > 0:
            violation = model.NewIntVar(0, max_inv_global, f'close_inv_viol_{grade}')
            model.Add(violation >= min_closing - V['inventory'][grade, num_days-1])
            objective_terms.append(violation * WEIGHT_CLOSING_INV)

    # Minimize Total Cost
    model.Minimize(sum(objective_terms))

    # ---------------------------------------------------------
    # 5. Solve
    # ---------------------------------------------------------
    solver = cp_model.CpSolver()
    
    # Parameters
    solver.parameters.max_time_in_seconds = params.get('time_limit_min', 10) * 60.0
    solver.parameters.num_search_workers = 8 # Parallelize
    solver.parameters.log_search_progress = True
    
    status = solver.Solve(model)
    
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return extract_solution(solver, V, grades, lines, dates, num_days)
    else:
        return None
