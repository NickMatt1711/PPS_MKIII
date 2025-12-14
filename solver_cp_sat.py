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
                # Use try-except as not all grade/line/day combinations might exist if constraints filtered them early
                try:
                    if solver.Value(variables['is_producing'][grade, line, d_idx]):
                        produced_grade = grade
                        qty = solver.Value(variables['production_qty'][grade, line, d_idx])
                        break
                except KeyError:
                    continue # Skip if variable not defined (e.g., due to line constraint)
            
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
    params: Dict,
    # ADDED: These arguments are accepted but ignored to match the app.py call
    grades: Optional[List[str]] = None,
    progress_callback: Optional[Any] = None,
    lines: Optional[List[str]] = None,  # <-- Added to resolve TypeError
    dates: Optional[List[Any]] = None,  # <-- Added to resolve potential future TypeError
) -> Optional[Dict]:
    """
    Main function to build and solve the CP-SAT model.
    """
    # NOTE: grades, progress_callback, lines, and dates are ignored here to maintain the 
    # robust internal logic (which re-derives them) while satisfying the app.py call signature.
    
    model = cp_model.CpModel()
    
    # ---------------------------------------------------------
    # 1. Data Preprocessing & Indexing (Internal derivation used for robustness)
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

    max_capacity = max(p['Capacity per day'] for p in plant_info.values()) if plant_info else 100000
    
    # Determine a safe global max inventory based on max historical demand plus opening inventory and max capacity
    max_inv_estimate = df_demand[grades].sum().sum() + \
                       sum(int(inv_info.get(g, {}).get('Opening Inventory', 0)) for g in grades) + \
                       max_capacity * num_days 
    max_inv_global = max(max_inv_estimate, 500000) # Ensure a high cap

    
    # --- Create Variables ---
    for d in range(num_days):
        for line in lines:
            # Transitions variables (from day d-1 to d)
            if d > 0:
                V['transition'][line, d] = model.NewBoolVar(f'trans_{line}_{d}')
            
            for grade in grades:
                V['is_producing'][grade, line, d] = model.NewBoolVar(f'x_{grade}_{line}_{d}')
                
                # Production quantity is capacity (Rule 16) or 0
                capacity_int = int(plant_info[line]['Capacity per day'])
                V['production_qty'][grade, line, d] = model.NewIntVar(0, capacity_int, f'p_{grade}_{line}_{d}')
                V['start_campaign'][grade, line, d] = model.NewBoolVar(f'start_{grade}_{line}_{d}')

        for grade in grades:
            # Inventory can range from 0 to Max (Hard Constraint 5)
            # Use the Max. Inventory from the data or the global estimate
            max_inv_grade = int(inv_info.get(grade, {}).get('Max. Inventory', max_inv_global))
            V['inventory'][grade, d] = model.NewIntVar(0, max_inv_grade, f'inv_{grade}_{d}')
            
            # Stockout allows arbitrary deficit (to be minimized)
            V['stockout'][grade, d] = model.NewIntVar(0, max_inv_global, f'stockout_{grade}_{d}')

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
                    # This implies: V['production_qty'] == V['is_producing'] * capacity
                    prod_qty_var = V['production_qty'][grade, line, d]
                    is_prod_var = V['is_producing'][grade, line, d]

                    # If is_producing is 1, production_qty must be capacity
                    model.Add(prod_qty_var == capacity).OnlyEnforceIf(is_prod_var)
                    # If is_producing is 0, production_qty must be 0
                    model.Add(prod_qty_var == 0).OnlyEnforceIf(is_prod_var.Not())


        # --- Inventory Balance (Rule 2, 12) ---
        for grade in grades:
            demand = int(df_demand.iloc[d][grade])
            
            # Calculate Total Production of this grade across all lines
            total_prod_today = sum(V['production_qty'][grade, line, d] for line in lines)
            
            prev_inv = 0
            if d == 0:
                # Rule 2: Opening Inventory (Must handle NaN/None gracefully)
                open_inv_raw = inv_info.get(grade, {}).get('Opening Inventory', 0)
                prev_inv = int(open_inv_raw) if pd.notna(open_inv_raw) else 0
            else:
                prev_inv = V['inventory'][grade, d - 1]
            
            # Balance Equation: Inv[d] = Inv[d-1] + Prod[d] - Demand[d] + Stockout[d]
            # Rearranged: Inv[d] - Stockout[d] = Prev_Inv + Prod - Demand
            model.Add(
                V['inventory'][grade, d] - V['stockout'][grade, d] == 
                prev_inv + total_prod_today - demand
            )

    # --- Line Capabilities (Rule 9) ---
    for grade in grades:
        allowed_lines_raw = inv_info.get(grade, {}).get('Lines', '')
        # Robustly parse and clean allowed lines
        allowed_lines_str = str(allowed_lines_raw).replace(" ", "")
        allowed_lines = set(allowed_lines_str.split(',')) if allowed_lines_str and allowed_lines_str != 'nan' else set(lines)
        
        for line in lines:
            if line not in allowed_lines:
                # Forbidden line for this grade
                for d in range(num_days):
                    model.Add(V['is_producing'][grade, line, d] == 0)

    # --- Campaign Start Logic ---
    for line in lines:
        for grade in grades:
            # Day 0 start logic (only if production is allowed on this line/grade)
            is_allowed = V['is_producing'][grade, line, 0] in model.Proto().variables
            if is_allowed:
                model.Add(V['start_campaign'][grade, line, 0] == V['is_producing'][grade, line, 0])
            
            for d in range(1, num_days):
                if (grade, line, d) not in V['is_producing']: continue
                if (grade, line, d-1) not in V['is_producing']: continue
                
                # Start = 1 iff Producing[d]=1 AND Producing[d-1]=0
                is_prod = V['is_producing'][grade, line, d]
                was_prod = V['is_producing'][grade, line, d-1]
                start_var = V['start_campaign'][grade, line, d]
                
                # Implication: start == is_prod AND NOT was_prod
                model.AddBoolAnd([is_prod, was_prod.Not()]).OnlyEnforceIf(start_var)
                model.AddBoolOr([is_prod.Not(), was_prod]).OnlyEnforceIf(start_var.Not())
                

    # --- Min/Max Run Days (Rules 6 & 7) ---
    for grade in grades:
        min_run_raw = inv_info.get(grade, {}).get('Min. Run Days', 1)
        max_run_raw = inv_info.get(grade, {}).get('Max. Run Days', num_days)
        
        min_run = int(min_run_raw) if pd.notna(min_run_raw) else 1
        max_run = int(max_run_raw) if pd.notna(max_run_raw) else num_days
        
        for line in lines:
            for d in range(num_days):
                if (grade, line, d) not in V['is_producing']: continue

                # Min Run Constraints (Rule 6)
                if V['start_campaign'][grade, line, d]:
                    # If started on day d, must produce for min_run days (or until end of horizon)
                    limit = min(d + min_run, num_days)
                    for k in range(d, limit):
                        # Implication: if start=1, then is_producing[grade, line, k]=1
                        if (grade, line, k) in V['is_producing']:
                            model.Add(V['is_producing'][grade, line, k] == 1).OnlyEnforceIf(V['start_campaign'][grade, line, d])

                # Max Run Constraints (Rule 7, Rolling Window)
                # Sum of production in any window of size (max_run + 1) must be <= max_run
                if d + max_run + 1 <= num_days:
                    window = []
                    for k in range(d, d + max_run + 1):
                         if (grade, line, k) in V['is_producing']:
                            window.append(V['is_producing'][grade, line, k])
                    
                    if window:
                        model.Add(sum(window) <= max_run)


    # --- Rerun Allowed (Rule 10) ---
    for grade in grades:
        rerun_raw = inv_info.get(grade, {}).get('Rerun Allowed', 'Yes')
        rerun = str(rerun_raw).lower()
        if rerun == 'no':
            for line in lines:
                # Sum of starts <= 1
                model.Add(sum(V['start_campaign'][grade, line, d] for d in range(num_days) if (grade, line, d) in V['start_campaign']) <= 1)

    # --- Force Start Date (Rule 8) ---
    for grade in grades:
        force_date_raw = inv_info.get(grade, {}).get('Force Start Date')
        if pd.notna(force_date_raw):
            try:
                force_date = pd.to_datetime(force_date_raw).date()
                if force_date in date_to_idx:
                    f_idx = date_to_idx[force_date]
                    # Must be produced on at least one allowed line on this date
                    
                    allowed_lines_str = str(inv_info.get(grade, {}).get('Lines', '')).replace(" ", "")
                    allowed = set(allowed_lines_str.split(',')) if allowed_lines_str and allowed_lines_str != 'nan' else set(lines)
                    
                    # Sum of production vars on allowed lines must be >= 1
                    prod_vars = [V['is_producing'][grade, l, f_idx] for l in lines if l in allowed and (grade, l, f_idx) in V['is_producing']]
                    if prod_vars:
                        model.Add(sum(prod_vars) >= 1)
            except:
                pass # Ignore invalid dates

    # --- Material Running & Expected Run Days (Rule 1) ---
    for line in lines:
        p_data = plant_info[line]
        running_grade_raw = p_data.get('Material Running')
        exp_days_raw = p_data.get('Expected Run Days')
        
        running_grade = str(running_grade_raw).strip() if pd.notna(running_grade_raw) else None
        
        if running_grade in grades:
            # Clean exp_days
            exp_days = int(exp_days_raw) if pd.notna(exp_days_raw) and exp_days_raw is not None else 0
            
            # Rule 1: If 1 or more, must run for EXACTLY that length, then changeover.
            # If 0 or null, must run on day 1, then optimizer chooses.
            
            if exp_days >= 1:
                run_len = exp_days
                
                # 1. Force production for these days [0, run_len-1]
                limit = min(run_len, num_days)
                for d in range(limit):
                    if (running_grade, line, d) in V['is_producing']:
                        model.Add(V['is_producing'][running_grade, line, d] == 1)
                
                # 2. Mandatory Changeover (Crucial Rule 1 requirement)
                # Force production to STOP on day index 'run_len' (the day changeover starts)
                if run_len < num_days:
                    if (running_grade, line, run_len) in V['is_producing']:
                        model.Add(V['is_producing'][running_grade, line, run_len] == 0)
                        
            elif exp_days == 0 or running_grade is not None:
                # Case B: Just start on Day 1 (Index 0). Solver decides length.
                if (running_grade, line, 0) in V['is_producing']:
                    model.Add(V['is_producing'][running_grade, line, 0] == 1)


    # --- Transitions (Rule 11) ---
    for line in lines:
        t_matrix = transition_rules.get(line)
        if not t_matrix:
            continue
            
        for d in range(1, num_days):
            for g_from in grades:
                for g_to in grades:
                    if g_from == g_to:
                        continue
                        
                    # Check if production vars exist for both grades on these days
                    if (g_from, line, d-1) not in V['is_producing'] or \
                       (g_to, line, d) not in V['is_producing']:
                        continue # Skip if grade is not allowed on line

                    # Get transition allowed status: g_to is in allowed transitions from g_from
                    is_allowed = g_to in t_matrix.get(g_from, [])
                    
                    # Variables for logic
                    prod_prev = V['is_producing'][g_from, line, d-1]
                    prod_curr = V['is_producing'][g_to, line, d]
                    
                    if not is_allowed:
                        # Hard Constraint: Forbidden Transition ("No")
                        # Cannot produce G_from yesterday (1) AND G_to today (1)
                        # Sum must be <= 1 (i.e., not both 1)
                        model.Add(prod_prev + prod_curr <= 1)
                    else:
                        # Soft Constraint: Allowed but penalized ("Yes")
                        # If switch happens (prod_prev=1 and prod_curr=1), increment transition counter
                        # T >= prod_prev + prod_curr - 1
                        model.Add(V['transition'][line, d] >= prod_prev + prod_curr - 1)

    # ---------------------------------------------------------
    # 4. Objective Function (Soft Constraints)
    # ---------------------------------------------------------
    objective_terms = []
    
    # A. Minimize Stockouts (Rule 13, 14)
    for grade in grades:
        # Prioritize low demand products
        is_low_demand = total_demand[grade] < (sum(total_demand.values()) / len(grades) * 0.5)
        penalty_mult = WEIGHT_LOW_DEMAND_STOCKOUT_MULTIPLIER if is_low_demand else 1.0
        
        for d in range(num_days):
            objective_terms.append(V['stockout'][grade, d] * int(WEIGHT_STOCKOUT * penalty_mult))

    # B. Minimize Transitions (Rule 11, 13)
    for line in lines:
        for d in range(1, num_days):
            if (line, d) in V['transition']:
                objective_terms.append(V['transition'][line, d] * WEIGHT_TRANSITION)

    # C. Min Daily Inventory (Rule 4)
    # Soft constraint: Penalty if Inventory < Min Inventory
    for grade in grades:
        min_inv_raw = inv_info.get(grade, {}).get('Min. Inventory', 0)
        min_inv = int(min_inv_raw) if pd.notna(min_inv_raw) else 0

        if min_inv > 0:
            for d in range(num_days):
                # Create a slack variable for violation
                violation = model.NewIntVar(0, max_inv_global, f'min_inv_viol_{grade}_{d}')
                # violation >= Min - Actual (Violation is 0 if Actual >= Min)
                model.Add(violation >= min_inv - V['inventory'][grade, d])
                objective_terms.append(violation * WEIGHT_MIN_INV_VIOLATION)

    # D. Min Closing Inventory (Rule 3)
    # Check only on the last day
    for grade in grades:
        min_closing_raw = inv_info.get(grade, {}).get('Min. Closing Inventory', 0)
        min_closing = int(min_closing_raw) if pd.notna(min_closing_raw) else 0

        if min_closing > 0:
            violation = model.NewIntVar(0, max_inv_global, f'close_inv_viol_{grade}')
            # violation >= Min_Closing - Actual_Closing
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
