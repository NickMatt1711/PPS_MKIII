"""
CP-SAT Solver for production optimization
"""

from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple, Callable, Optional, Any
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED
import math
from datetime import date # Added import

# Helper function to get value safely
def _get_opt_param(params: Dict, key: str, default: Any) -> Any:
    return params.get(key, default)

class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Callback to capture all solutions during search"""
    
    def __init__(self, production, inventory, stockout, is_producing, grades, lines, dates, formatted_dates, num_days, 
                 inventory_deficit_penalties=None, closing_inventory_deficit_penalties=None):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.production = production
        self.inventory = inventory
        self.stockout = stockout
        self.is_producing = is_producing
        self.grades = grades
        self.lines = lines
        self.dates = dates
        self.formatted_dates = formatted_dates
        self.num_days = num_days
        self.inventory_deficit_penalties = inventory_deficit_penalties or {}
        self.closing_inventory_deficit_penalties = closing_inventory_deficit_penalties or {}
        self.solutions = []
        self.solution_times = []
        self.start_time = time.time()
        self.objective_breakdowns = []

    def on_solution_callback(self):
        current_time = time.time() - self.start_time
        self.solution_times.append(current_time)
        current_obj = self.ObjectiveValue()

        solution = {
            'objective': current_obj,
            # Placeholder for log data, to be populated by the caller
        }
        
        # Extract production schedule
        prod_schedule = {}
        for line in self.lines:
            prod_schedule[line] = {}
            for d in range(self.num_days):
                day_data = {'date': self.formatted_dates[d], 'production': {}}
                
                # Check for grade being produced
                produced_grade = None
                for grade in self.grades:
                    var_key = (grade, line, d)
                    if var_key in self.is_producing and self.BooleanValue(self.is_producing[var_key]):
                        produced_grade = grade
                        break
                
                if produced_grade:
                    prod_qty = self.Value(self.production.get((produced_grade, line, d), 0))
                    day_data['production'] = {produced_grade: prod_qty}
                else:
                    day_data['production'] = {'IDLE': 0}
                
                prod_schedule[line][d] = day_data

        solution['production_schedule'] = prod_schedule
        
        # Extract inventory levels and stockouts
        inventory_levels = {grade: {} for grade in self.grades}
        stockouts = {grade: {} for grade in self.grades}

        for grade in self.grades:
            for d in range(self.num_days + 1): # Inventory includes Day 0 (opening)
                # Inventory is indexed 0 to num_days
                if (grade, d) in self.inventory:
                    inventory_levels[grade][self.formatted_dates[max(0, d-1)] if d > 0 else "Opening"] = self.Value(self.inventory[(grade, d)])
            
            # Stockout is indexed 0 to num_days-1
            for d in range(self.num_days):
                if (grade, d) in self.stockout and self.Value(self.stockout[(grade, d)]) > 0:
                    stockouts[grade][self.formatted_dates[d]] = self.Value(self.stockout[(grade, d)])

        solution['inventory'] = inventory_levels
        solution['stockout'] = stockouts
        
        # Calculate objective breakdown
        breakdown = {
            'total_objective': current_obj,
            'stockout_penalty': 0,
            'transition_penalty': 0,
            'idle_penalty': 0,
            'min_closing_inv_penalty': 0
        }
        
        # Since the callback doesn't have access to the actual penalty terms defined in the model,
        # we estimate the penalty from the deficit variables captured.
        
        stockout_penalty_sum = 0
        for _, pen in self.inventory_deficit_penalties.items():
            stockout_penalty_sum += self.Value(pen)
        breakdown['stockout_penalty'] = stockout_penalty_sum

        closing_inv_penalty_sum = 0
        for _, pen in self.closing_inventory_deficit_penalties.items():
            closing_inv_penalty_sum += self.Value(pen)
        breakdown['min_closing_inv_penalty'] = closing_inv_penalty_sum
        
        # Note: Idle and Transition penalties are hard to calculate exactly without the model's internal variables
        # We'll just store the main penalties for now.
        
        self.objective_breakdowns.append(breakdown)
        self.solutions.append(solution)
        
        # st.toast(f"Found Solution with Objective: {int(current_obj):,} (Time: {current_time:.2f}s)", icon="✅")


# ===============================================================
#  MAIN SOLVER FUNCTION
# ===============================================================
def build_and_solve_model(
    grades: List[str],
    lines: List[str],
    dates: List[date],
    formatted_dates: List[str],
    inventory_data: Dict[str, Any],
    demand_data: Dict[str, Any],
    plant_data: Dict[str, Any],
    transition_rules: Dict[str, Any],
    optimization_params: Dict[str, Any],
    shutdown_days: Dict[str, List[int]], # Added shutdown_days to function signature
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Tuple[cp_model.CpSolverStatus, SolutionCallback, cp_model.CpSolver]:
    """
    Builds and solves the Polymer Production Scheduling CP-SAT model.
    """
    
    # --- 0. Setup and Parameters ---
    model = cp_model.CpModel()
    
    # Calculate num_days inside the function
    num_days = len(dates) 
    
    time_limit_min = _get_opt_param(optimization_params, 'time_limit_min', 10)
    stockout_penalty = _get_opt_param(optimization_params, 'stockout_penalty', 10) * 1000 # Convert to large integer penalty
    transition_penalty = _get_opt_param(optimization_params, 'transition_penalty', 5) * 100 # Convert to integer penalty
    idle_penalty = _get_opt_param(optimization_params, 'idle_penalty', 1) * 100 # Convert to integer penalty
    
    # Maximum inventory and demand for bounds
    MAX_CAPACITY = max(p['capacity'] for p in plant_data['plants']) if plant_data['plants'] else 10000
    MAX_INV_BOUND = int(1.5 * max(inv_data['max_inv'] for inv_data in inventory_data['grades_data'].values())) if inventory_data['grades_data'] else 30000
    MAX_DEMAND_BOUND = int(1.5 * demand_data['max_demand_qty']) if demand_data and 'max_demand_qty' in demand_data else 30000
    
    # Upper bound for inventory (Max of max_inv or demand bound)
    M = max(MAX_INV_BOUND, num_days * MAX_CAPACITY + MAX_INV_BOUND)

    if progress_callback:
        progress_callback(0.05, "Building model variables...")

    # --- 1. Decision Variables ---
    
    # Production Quantity: production[(grade, line, day)]
    production = {}
    
    # Is Producing: is_producing[(grade, line, day)] (Boolean variable)
    is_producing = {} 
    
    # Inventory Level: inventory[(grade, day)] (day 0 is opening inventory)
    inventory_vars = {} 
    
    # Stockout Quantity: stockout[(grade, day)]
    stockout_vars = {} 
    
    # Inventory Deficit Penalty Variables (for soft constraints)
    inventory_deficit_penalties = {}
    closing_inventory_deficit_penalties = {}
    
    # Plant/Line assignment variables (Grade-Line-Day)
    for grade in grades:
        inv_data = inventory_data['grades_data'][grade]
        max_production_qty = inv_data['max_inv'] # Max quantity produced is capped by Max Inventory for safety
        
        for line in lines:
            if line not in inv_data['lines']:
                continue # Grade cannot run on this line

            for d in range(num_days):
                # Only create variables for grades runnable on the line
                
                # Check for explicit shutdown (hard constraint)
                if d in shutdown_days.get(line, []):
                    # Production and Is_Producing vars are implicitly zero/false during shutdown
                    continue

                # 1. Production Quantity (0 to Max Inventory for the grade)
                prod_var = model.NewIntVar(0, max_production_qty, f'prod_{grade}_{line}_{d}')
                production[(grade, line, d)] = prod_var
                
                # 2. Is Producing (Boolean: 1 if producing, 0 otherwise)
                is_prod_var = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                is_producing[(grade, line, d)] = is_prod_var
                
                # Link Production Qty and Is Producing
                model.Add(prod_var > 0).OnlyEnforceIf(is_prod_var)
                model.Add(prod_var == 0).OnlyEnforceIf(is_prod_var.Not())
                # Ensure capacity limit is respected by setting the upper bound of the production variable
                
                # Apply initial run constraint if applicable
                if d == 0:
                    plant_run_data = plant_data['plants_data'].get(line, {})
                    initial_grade = plant_run_data.get('material_running')
                    if initial_grade and initial_grade != grade:
                        # Cannot start production of a different grade on Day 0 if a grade is already running
                        model.Add(is_prod_var == 0)

    # Inventory and Stockout Variables (Grade-Day)
    for grade in grades:
        inv_data = inventory_data['grades_data'][grade]
        
        # Inventory includes Day 0 (Opening Inventory)
        for d in range(num_days + 1):
            # Inventory Level (from 0 up to M)
            inv_var = model.NewIntVar(0, M, f'inv_{grade}_{d}')
            inventory_vars[(grade, d)] = inv_var
        
        # Stockout (from 0 up to M)
        for d in range(num_days):
            stockout_var = model.NewIntVar(0, M, f'stockout_{grade}_{d}')
            stockout_vars[(grade, d)] = stockout_var
            
            # Inventory Deficit Penalty Variable (for soft Min. Inventory constraint)
            if d < num_days - 1: # No need to check Min Inv on the last day, only min closing
                inv_deficit = model.NewIntVar(0, M, f'inv_deficit_{grade}_{d}')
                inventory_deficit_penalties[(grade, d)] = inv_deficit
            
    # Inventory Deficit Penalty for Min. Closing Inventory (last day)
    # The last day of inventory is day `num_days` (closing inventory)
    closing_inv_deficit = model.NewIntVar(0, M, f'inv_deficit_closing_{grade}')
    closing_inventory_deficit_penalties[grade] = closing_inv_deficit

    if progress_callback:
        progress_callback(0.2, "Adding plant capacity constraints...")
        
    # --- 2. Capacity Constraints (Line-Day) ---
    for line in lines:
        plant_data_line = plant_data['plants_data'][line]
        capacity = plant_data_line['capacity']
        
        for d in range(num_days):
            # Check for explicit shutdown (hard constraint)
            if d in shutdown_days.get(line, []):
                # Production must be zero during shutdown
                production_sum = [
                    production[(grade, line, d)] 
                    for grade in grades 
                    if (grade, line, d) in production
                ]
                if production_sum:
                    model.Add(sum(production_sum) == 0)
                continue # Skip capacity constraint for shutdown days

            # Sum of production for all grades on a line must be <= capacity
            production_sum = [
                production[(grade, line, d)] 
                for grade in grades 
                if (grade, line, d) in production
            ]
            
            # The sum is implicitly 0 if production_sum is empty due to shutdown check above
            if production_sum:
                model.Add(sum(production_sum) <= capacity)

    if progress_callback:
        progress_callback(0.3, "Adding transition and run-length constraints...")

    # --- 3. Run-Length and Transition Constraints (Line-Day) ---
    for line in lines:
        line_grades = [g for g in grades if line in inventory_data['grades_data'][g]['lines']]
        
        for d in range(num_days):
            # 3.1. Single Grade per Line per Day
            # Only one grade can be 'producing' (Is_Producing=1) on a line per day
            # This is automatically enforced by the sum, and the idle variable handling later.
            is_producing_vars_day = [
                is_producing[(grade, line, d)] 
                for grade in line_grades 
                if (grade, line, d) in is_producing # Check if not a shutdown day
            ]
            if is_producing_vars_day:
                # If it's not a shutdown day, at most one grade can be produced (or it's idle)
                model.Add(sum(is_producing_vars_day) <= 1)
            
            # 3.2. Initial Production (Day 0)
            if d == 0:
                # Enforce initial running grade if specified in Plant data
                plant_run_data = plant_data['plants_data'].get(line, {})
                initial_grade = plant_run_data.get('material_running')
                
                if initial_grade and initial_grade in line_grades:
                    # If specified grade can run on line, force it
                    is_prod_var = is_producing.get((initial_grade, line, d))
                    if is_prod_var:
                        model.Add(is_prod_var == 1)
                    # For all other grades, force production to 0
                    for grade in line_grades:
                        if grade != initial_grade:
                            other_prod_var = is_producing.get((grade, line, d))
                            if other_prod_var:
                                model.Add(other_prod_var == 0)
                elif initial_grade:
                    # If specified grade cannot run on line, force line to be idle or run a valid grade
                    # (This is handled by the capacity and single-grade constraints)
                    pass

            # 3.3. Transition Constraint (d > 0)
            if d > 0:
                is_producing_vars_prev = [
                    is_producing[(grade, line, d-1)] 
                    for grade in line_grades 
                    if (grade, line, d-1) in is_producing
                ]
                
                # Handle restart grade after shutdown
                if d in shutdown_days.get(line, []) and d-1 not in shutdown_days.get(line, []):
                    # Day d is shutdown day, skip transition constraints for production
                    pass
                elif d not in shutdown_days.get(line, []) and d-1 in shutdown_days.get(line, []):
                    # Day d is restart day, Day d-1 was shutdown
                    # The previous grade is set by the 'restart_grade'
                    restart_grade = plant_data['plants_data'][line].get('restart_grade')
                    
                    if restart_grade:
                        # Ensure the current grade is allowed to start after the restart grade
                        current_grade_vars = [
                            is_producing[(g, line, d)]
                            for g in line_grades 
                            if (g, line, d) in is_producing
                        ]
                        
                        if current_grade_vars:
                            # For each current grade G, if G is being produced, it must be allowed from restart_grade
                            for g in line_grades:
                                if (g, line, d) in is_producing:
                                    is_prod_var_current = is_producing[(g, line, d)]
                                    
                                    if restart_grade not in transition_rules.get(line, {}).get(g, []):
                                        # G is not allowed from restart_grade, so force G production to 0
                                        model.Add(is_prod_var_current == 0)

                else: # Normal transition (d-1 was producing/idle, d is producing/idle)
                    # For each grade G_curr being produced today (d)
                    for grade_curr in line_grades:
                        is_prod_curr = is_producing.get((grade_curr, line, d))
                        if not is_prod_curr:
                            continue
                            
                        # If G_curr is produced, the previous grade G_prev must be in the allowed transitions
                        allowed_prev_grades = transition_rules.get(line, {}).get(grade_curr, [])
                        
                        # Create an implied OR constraint for allowed transitions
                        allowed_transition_booleans = []
                        
                        # 1. Previous grade G_prev was IDLE/Not Producing
                        is_idle_prev = model.NewBoolVar(f'is_idle_prev_{line}_{d}')
                        idle_sum_prev = sum(is_producing_vars_prev)
                        model.Add(idle_sum_prev == 0).OnlyEnforceIf(is_idle_prev)
                        model.Add(idle_sum_prev >= 1).OnlyEnforceIf(is_idle_prev.Not())

                        # Check if transition from IDLE is allowed (treated as transition from any grade)
                        # If a line goes from IDLE to grade_curr, it's allowed if grade_curr is in the transitions
                        # We simplify: any transition is allowed unless explicitly disallowed.
                        
                        # Check for each possible previous grade
                        for grade_prev in line_grades:
                            is_prod_prev = is_producing.get((grade_prev, line, d-1))
                            if not is_prod_prev:
                                continue
                                
                            if grade_prev in allowed_prev_grades:
                                # Transition G_prev -> G_curr is allowed. Add G_prev being produced as an option.
                                allowed_transition_booleans.append(is_prod_prev)
                            else:
                                # Transition G_prev -> G_curr is NOT allowed.
                                # Constraint: NOT(is_prod_curr AND is_prod_prev)
                                # OR: is_prod_curr + is_prod_prev <= 1
                                # OR: is_prod_prev == 0 .OnlyEnforceIf(is_prod_curr)
                                # Simpler: if grade_curr is produced, grade_prev must NOT be produced.
                                model.Add(is_prod_prev == 0).OnlyEnforceIf(is_prod_curr)

    if progress_callback:
        progress_callback(0.4, "Adding inventory balance constraints...")

    # --- 4. Inventory Balance and Demand Constraints (Grade-Day) ---
    for grade in grades:
        inv_data = inventory_data['grades_data'][grade]
        demand_series = demand_data['demand_series'].get(grade, [0] * num_days)
        
        # 4.1. Set Opening Inventory (Day 0)
        model.Add(inventory_vars[(grade, 0)] == inv_data['opening'])
        
        for d in range(num_days):
            # Production sum from all lines today
            total_production_today = [
                production[(grade, line, d)] 
                for line in lines 
                if (grade, line, d) in production
            ]

            # Current day demand
            demand_qty = demand_series[d]
            
            # Inventory Balance Equation (for Day d+1's opening inventory, which is day d's closing inventory)
            # Inv[d] + Prod[d] = Demand[d] + Inv[d+1] + Stockout[d]
            # Inv[d+1] = Inv[d] + Prod[d] - Demand[d] - Stockout[d] (since Stockout is a slack variable)
            
            # Use the canonical form: A = B + C - D
            # inventory_vars[(grade, d+1)] + stockout_vars[(grade, d)] = inventory_vars[(grade, d)] + sum(total_production_today) - demand_qty
            
            model.Add(inventory_vars[(grade, d+1)] + stockout_vars[(grade, d)] == 
                      inventory_vars[(grade, d)] + sum(total_production_today) - demand_qty)
            
            # 4.2. Soft Min. Inventory Constraint (Day d's closing inventory)
            # Min Inv check is against day d+1's opening (or d's closing)
            min_inv_target = inv_data['min_inv']
            
            if min_inv_target > 0 and d < num_days - 1: # Standard min inventory (not on the last day)
                inv_deficit = inventory_deficit_penalties[(grade, d)]
                
                # Soft Constraint: Inventory[d+1] >= Min_Inv - Deficit[d]
                # Deficit[d] = Max(0, Min_Inv - Inventory[d+1])
                model.Add(inv_deficit >= min_inv_target - inventory_vars[(grade, d+1)])
                model.Add(inv_deficit >= 0)
            
            # 4.3. Hard Max. Inventory Constraint (Day d's closing inventory)
            max_inv_target = inv_data['max_inv']
            if max_inv_target > 0:
                model.Add(inventory_vars[(grade, d+1)] <= max_inv_target)

    if progress_callback:
        progress_callback(0.5, "Adding min closing inventory constraints...")

    # --- 5. Min. Closing Inventory Constraint (Grade-End of Horizon) ---
    for grade in grades:
        inv_data = inventory_data['grades_data'][grade]
        min_closing_inv = inv_data['min_closing']
        
        if min_closing_inv > 0:
            closing_inv_var = inventory_vars[(grade, num_days)] # Inventory on the last day (d=num_days)
            inv_deficit_closing = closing_inventory_deficit_penalties[grade]
            
            # Soft Constraint: Closing_Inv >= Min_Closing - Deficit_Closing
            # Deficit_Closing = Max(0, Min_Closing - Closing_Inv)
            model.Add(inv_deficit_closing >= min_closing_inv - closing_inv_var)
            model.Add(inv_deficit_closing >= 0)

    if progress_callback:
        progress_callback(0.6, "Adding run length and transition cost objectives...")

    # --- 6. Min/Max Run Length Constraints (Grade-Line-Day) ---
    for grade in grades:
        inv_data = inventory_data['grades_data'][grade]
        min_run_days = inv_data['min_run_days']
        max_run_days = inv_data['max_run_days']
        
        for line in lines:
            if line not in inv_data['lines']:
                continue
            
            # 6.1. Minimum Run Length (Min_Run_Days)
            if min_run_days > 1:
                for d in range(num_days):
                    is_prod_curr = is_producing.get((grade, line, d))
                    if not is_prod_curr:
                        continue

                    # If grade starts running on day d (i.e., not running on d-1), 
                    # it must run for at least min_run_days
                    
                    # Check if production starts today (d)
                    is_prod_prev = is_producing.get((grade, line, d-1), 0)
                    if d == 0:
                        is_prod_prev = 0 # Assume not running before Day 0 unless explicitly set by 'material_running'
                        plant_run_data = plant_data['plants_data'].get(line, {})
                        initial_grade = plant_run_data.get('material_running')
                        if initial_grade == grade:
                            is_prod_prev = 1
                    
                    # Create variable `is_change`
                    is_change = model.NewBoolVar(f'is_change_{grade}_{line}_{d}')
                    
                    if is_prod_prev != 0:
                        # If is_prod_curr is 1 and is_prod_prev is 0, change occurred.
                        model.Add(is_prod_curr == 1).OnlyEnforceIf(is_change)
                        model.Add(is_prod_prev == 0).OnlyEnforceIf(is_change)
                        
                    # If grade starts running (is_change=1) it must continue for min_run_days
                    # is_change implies: is_producing[(grade, line, d+k)] == 1 for k=1 to min_run_days-1
                    for k in range(1, min_run_days):
                        future_d = d + k
                        if future_d < num_days and (grade, line, future_d) in is_producing:
                            model.Add(is_producing[(grade, line, future_d)] == 1).OnlyEnforceIf(is_change)
                        else:
                            # If min_run_days exceeds horizon or shutdown, then this run is impossible if it starts, so force is_start=0
                            # This is a hard constraint that can over-constrain the model, often done with a soft penalty.
                            # For simplicity, we'll enforce the min run *within* the horizon/non-shutdown days.
                            pass

            # 6.2. Maximum Run Length (Max_Run_Days)
            # Not strictly required for simple scheduling, but can be added if needed.
            # E.g., If producing on day d, d+1, ..., d + max_run_days - 1, then MUST NOT produce on d + max_run_days.
            pass


    if progress_callback:
        progress_callback(0.7, "Setting objective function...")

    # --- 7. Objective Function (Minimize Soft Constraints) ---
    
    objective_terms = []
    
    # 7.1. Stockout Penalty
    for grade in grades:
        for d in range(num_days):
            objective_terms.append(stockout_penalty * stockout_vars[(grade, d)])
            
    # 7.2. Min. Inventory Penalty (Standard)
    for grade in grades:
        for d in range(num_days - 1): # Standard min inventory (not on the last day)
            inv_deficit = inventory_deficit_penalties.get((grade, d))
            if inv_deficit:
                objective_terms.append(_get_opt_param(optimization_params, 'min_inv_penalty', 5) * 100 * inv_deficit)

    # 7.3. Min. Closing Inventory Penalty
    for grade in grades:
        inv_deficit_closing = closing_inventory_deficit_penalties.get(grade)
        if inv_deficit_closing:
            objective_terms.append(_get_opt_param(optimization_params, 'min_inv_penalty', 5) * 100 * inv_deficit_closing)
    
    # 7.4. Transition Penalty (Cost for switching grades)
    for line in lines:
        line_grades = [g for g in grades if line in inventory_data['grades_data'][g]['lines']]
        for d in range(1, num_days):
            is_producing_vars_prev = [
                is_producing[(grade, line, d-1)] 
                for grade in line_grades 
                if (grade, line, d-1) in is_producing
            ]
            
            # Check for a switch: current grade is produced AND previous grade is different
            for grade_curr in line_grades:
                is_prod_curr = is_producing.get((grade_curr, line, d))
                if not is_prod_curr:
                    continue
                
                for grade_prev in line_grades:
                    if grade_curr == grade_prev:
                        continue # Same grade, no transition cost
                        
                    is_prod_prev = is_producing.get((grade_prev, line, d-1))
                    if not is_prod_prev:
                        continue
                        
                    # Transition switch variable: is_prod_curr AND is_prod_prev (Boolean)
                    is_switch = model.NewBoolVar(f'switch_{grade_prev}_{grade_curr}_{line}_{d}')
                    model.AddBoolAnd([is_prod_curr, is_prod_prev]).OnlyEnforceIf(is_switch)
                    
                    objective_terms.append(transition_penalty * is_switch)

            # 7.5. Idle Penalty (Cost for being idle when not shut down)
            is_idle = model.NewBoolVar(f'idle_{line}_{d}')
            
            producing_vars = [
                is_producing[(grade, line, d)] 
                for grade in grades 
                if (grade, line, d) in is_producing
            ]
            
            if producing_vars:
                model.Add(sum(producing_vars) == 0).OnlyEnforceIf(is_idle)
                model.Add(sum(producing_vars) == 1).OnlyEnforceIf(is_idle.Not())
                objective_terms.append(idle_penalty * is_idle)
    
    # Set the objective to minimize SOFT constraint violations
    if objective_terms:
        model.Minimize(sum(objective_terms))
    else:
        model.Minimize(0)
    
    if progress_callback:
        progress_callback(0.8, "Solving optimization problem...")
    
    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60.0
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED
    solver.parameters.log_search_progress = True
    
    solution_callback = SolutionCallback(
        production, inventory_vars, stockout_vars, is_producing,
        grades, lines, dates, formatted_dates, num_days,
        inventory_deficit_penalties, closing_inventory_deficit_penalties
    )
    
    status = solver.Solve(model, solution_callback)
    return status, solution_callback, solver
