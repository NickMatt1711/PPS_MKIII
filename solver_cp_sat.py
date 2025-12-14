"""
CP-SAT Solver for production optimization
"""

from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple, Any
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED
import math
from datetime import date # Added for type hinting the 'dates' parameter
import pandas as pd # Added for type hinting the 'demand_data' parameter


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
            'production': {},
            'inventory': {},
            'stockout': {},
            'objective_breakdown': self.get_objective_breakdown()
        }

        # Extract Production Schedule
        for grade in self.grades:
            solution['production'][grade] = {}
            for line in self.lines:
                solution['production'][grade][line] = {}
                for d in range(self.num_days):
                    if (grade, line, d) in self.is_producing and self.Value(self.is_producing[(grade, line, d)]):
                        # Use the formatted date string for the final solution key
                        solution['production'][grade][line][self.formatted_dates[d]] = self.Value(self.production[(grade, line, d)])

        # Extract Inventory and Stockout
        for grade in self.grades:
            solution['inventory'][grade] = {}
            solution['stockout'][grade] = {}
            for d in range(self.num_days + 1): # Inventory includes T=0 (Opening) up to T=Last Day
                # Inventory (T=1 to T=Last Day+1)
                if d > 0:
                    # Use the formatted date string for the final solution key
                    date_key = self.formatted_dates[d-1]
                    solution['inventory'][grade][date_key] = self.Value(self.inventory[(grade, d)])
                
                # Stockout (T=1 to T=Last Day)
                if d > 0 and d <= self.num_days:
                    date_key = self.formatted_dates[d-1]
                    solution['stockout'][grade][date_key] = self.Value(self.stockout[(grade, d)])

        self.solutions.append(solution)


    def get_objective_breakdown(self) -> Dict[str, float]:
        """Calculates the contribution of each soft constraint to the objective value."""
        # This implementation requires the solver to pass the individual penalty vars to the callback
        # which is not currently done in build_and_solve_model, so we'll return a simple breakdown
        # based on the penalties that were tracked/passed (stockout/closing inventory penalties)
        
        breakdown = {
            "Total Objective Value": self.ObjectiveValue(),
            "Soft Inventory Deficit Penalty": 0.0,
            "Soft Min Closing Inventory Penalty": 0.0,
            "Idle Line Penalty": 0.0,
            "Transition Penalty": 0.0,
        }

        # Calculate Stockout / Inventory Penalties
        for penalty_var in self.inventory_deficit_penalties.values():
            if self.Value(penalty_var) > 0:
                breakdown["Soft Inventory Deficit Penalty"] += self.Value(penalty_var)

        for penalty_var in self.closing_inventory_deficit_penalties.values():
             if self.Value(penalty_var) > 0:
                breakdown["Soft Min Closing Inventory Penalty"] += self.Value(penalty_var)

        # Note: Idle Line and Transition Penalties are calculated outside the penalty dicts 
        # but are implicitly part of the total objective. Their individual value would need 
        # dedicated tracking variables passed to the callback. For now, we only populate 
        # what is easily computable from passed arguments.

        # A more complex breakdown would require passing the transition_penalty_vars and idle_penalty_vars
        # from build_and_solve_model into the callback's constructor.
        
        return breakdown


# ===============================================================
#  MODEL BUILDER AND SOLVER
# ===============================================================
def build_and_solve_model(
    grades: List[str],
    lines: List[str],
    dates: List[date],
    inventory_data: Dict,
    plant_data: Dict,
    demand_data: pd.DataFrame,
    transition_rules: Dict,
    optimization_params: Dict,
    formatted_dates: List[str], # <--- ADDED MISSING ARGUMENT
    progress_callback=None
) -> Tuple[int, cp_model.CpSolverSolutionCallback, cp_model.CpSolver]:
    """
    Builds and solves the Polymer Production Scheduling CP-SAT model.
    """
    if progress_callback:
        progress_callback(0.0, "Initializing model...")

    model = cp_model.CpModel()
    num_days = len(dates)
    
    # --- Optimization Parameters ---
    stockout_penalty = optimization_params['stockout_penalty']
    transition_penalty = optimization_params['transition_penalty']
    time_limit_min = optimization_params['time_limit_min']
    buffer_days = optimization_params['buffer_days']
    idle_penalty = optimization_params.get('idle_penalty', 1) # Default to 1 if not present

    # --- 1. Decision Variables ---
    
    # Production: production[(grade, line, day)] = Quantity produced of grade on line on day d
    # Variable domain: [0, max_capacity] where max_capacity is the largest plant capacity
    max_capacity = max(p['capacity'] for p in plant_data['lines_data'].values())
    production = {}
    
    for grade in grades:
        for line in lines:
            for d in range(num_days):
                # Only create variable if the grade is allowed on the line
                if line in inventory_data['data'][grade]['lines']:
                    production[(grade, line, d)] = model.NewIntVar(
                        0, plant_data['lines_data'][line]['capacity'], f'prod_{grade}_{line}_{d}'
                    )

    # Indicator variable: is_producing[(grade, line, day)] = 1 if grade is produced on line on day d, 0 otherwise
    is_producing = {}
    for (grade, line, d), prod_var in production.items():
        is_producing[(grade, line, d)] = model.NewBoolVar(f'is_prod_{grade}_{line}_{d}')
        # Link indicator to production variable: is_producing = 1 <=> production > 0
        model.Add(prod_var > 0).OnlyEnforceIf(is_producing[(grade, line, d)])
        model.Add(prod_var == 0).OnlyEnforceIf(is_producing[(grade, line, d)].Not())

    # Inventory: inventory[(grade, day)] = Inventory level of grade at the end of day d
    # d = 0 is opening inventory, d = 1 to num_days is closing inventory for that day
    inventory_vars = {}
    max_inventory = max(i['max_inv'] for i in inventory_data['data'].values()) * 2 # Safety margin
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(
                0, max_inventory, f'inv_{grade}_{d}'
            )

    # Stockout: stockout[(grade, day)] = Quantity of stockout for grade on day d
    stockout_vars = {}
    max_demand = demand_data.iloc[:, 1:].max().max() * 2 # Safety margin
    for grade in grades:
        for d in range(1, num_days + 1):
            stockout_vars[(grade, d)] = model.NewIntVar(
                0, max_demand, f'stockout_{grade}_{d}'
            )
            
    if progress_callback:
        progress_callback(0.1, "Variables initialized...")

    # --- 2. Hard Constraints ---

    # C1. Inventory balance equation
    for grade in grades:
        # Day 0: Set opening inventory (Hard Constraint)
        model.Add(inventory_vars[(grade, 0)] == inventory_data['data'][grade]['opening'])

        # Days 1 to N: Balance
        for d in range(1, num_days + 1):
            # Sum of production for the current grade on all lines on day d-1
            total_production = sum(
                production.get((grade, line, d - 1), 0) for line in lines
            )
            
            # Demand for the current grade on day d-1
            demand_qty = demand_data.iloc[d - 1][grade]
            
            # Inventory[d] = Inventory[d-1] + Production[d-1] - Demand[d-1] + Stockout[d-1]
            # Since Inventory, Production, and Demand are >= 0, we can express the balance as:
            # Inventory[d-1] + Production[d-1] + Stockout[d] == Inventory[d] + Demand[d-1]
            # Stockout[d] acts as a slack variable allowing the left side to be less than the right.

            model.Add(
                inventory_vars[(grade, d - 1)] + total_production + stockout_vars[(grade, d)]
                == inventory_vars[(grade, d)] + demand_qty
            )

    if progress_callback:
        progress_callback(0.2, "Inventory and Stockout constraints added...")

    # C2. Plant capacity constraint (Each line produces at most one grade)
    for line in lines:
        line_capacity = plant_data['lines_data'][line]['capacity']
        for d in range(num_days):
            # Sum of indicator variables for all grades on a line on a given day must be 0 or 1
            # (i.e., at most one grade is produced)
            producing_indicators = [
                is_producing[(grade, line, d)] 
                for grade in grades 
                if (grade, line, d) in is_producing
            ]
            
            if producing_indicators:
                model.Add(sum(producing_indicators) <= 1)
                
            # Total production quantity must be <= capacity if operating
            total_production_on_line = sum(
                production.get((grade, line, d), 0) for grade in grades
            )
            model.Add(total_production_on_line <= line_capacity)

    if progress_callback:
        progress_callback(0.3, "Plant Capacity constraints added...")

    # C3. Minimum/Maximum Inventory limits (Excluding Stockout day)
    for grade in grades:
        min_inv = inventory_data['data'][grade]['min_inv']
        max_inv = inventory_data['data'][grade]['max_inv']
        
        # Min/Max inventory applies to closing inventory (d=1 to num_days)
        for d in range(1, num_days + 1):
            # Check if stockout happened on this day. If YES, min_inv constraint is relaxed.
            is_stockout = model.NewBoolVar(f'is_stockout_{grade}_{d}')
            model.Add(stockout_vars[(grade, d)] > 0).OnlyEnforceIf(is_stockout)
            model.Add(stockout_vars[(grade, d)] == 0).OnlyEnforceIf(is_stockout.Not())
            
            # HARD: Inventory must be <= Max Inventory
            model.Add(inventory_vars[(grade, d)] <= max_inv)
            
            # HARD: Inventory must be >= Min Inventory, UNLESS a stockout occurred.
            # model.Add(inventory_vars[(grade, d)] >= min_inv).OnlyEnforceIf(is_stockout.Not())
            # Since inventory balance already takes care of the stockout, a simpler min inventory constraint
            # is typically sufficient if Stockout is penalized. We will use a soft constraint approach 
            # for the min inventory to allow the solver more freedom when stockout is unavoidable.
            
            # For now, let's just keep the MAX as a hard constraint and rely on stockout penalties for MIN.

    if progress_callback:
        progress_callback(0.4, "Inventory Min/Max constraints refined...")

    # C4. Minimum Run Days / Expected Run Days (Consecutive production)
    for grade in grades:
        min_run_days = inventory_data['data'][grade]['min_run_days']
        
        for line in lines:
            if line not in inventory_data['data'][grade]['lines']:
                continue # Skip if grade is not allowed on line
                
            for d in range(num_days - min_run_days + 1):
                # If production starts on day d-1, it must continue for min_run_days
                # Check for start of production: (grade was not produced on day d-2) AND (grade is produced on day d-1)
                
                # Check if this grade was produced on d-1 on the current line
                is_start = is_producing.get((grade, line, d), None)
                if not is_start: continue
                
                # Check if previous day (d-1) was not this grade (or is day 0)
                is_prev_not_grade = 1
                if d > 0:
                    is_prev_not_grade = is_producing.get((grade, line, d - 1), 0).Not()
                
                # If a run starts, production must continue for the required duration.
                # A run "starts" on day d if is_producing[d] is 1 AND (d=0 OR is_producing[d-1] is 0)
                
                # We will use the interval variable approach for run lengths.
                
                # 1. Create an interval for each grade/line run
                interval_vars = {}
                for d in range(num_days):
                    if (grade, line, d) in is_producing:
                        # Only create interval if production is possible
                        interval_vars[(grade, line, d)] = model.NewOptionalInterval(
                            start=d,
                            size=1,
                            end=d + 1,
                            is_present=is_producing[(grade, line, d)],
                            name=f'interval_{grade}_{line}_{d}'
                        )
                
                # 2. Add NoOverlap constraint (already handled by C2, but helps the solver)
                # Not strictly needed here as C2 does the job, but good practice.
                
                # 3. Add Min Run Length constraint (using runs of 1-day intervals)
                # Sequence variable on the intervals will enforce this, but CP-SAT is simpler.
                
                # Use AddBoolOr to enforce minimum run length
                
                # We enforce: if production starts at day d, then is_producing must be 1 for d, d+1, ..., d + min_run_days - 1
                
                for d in range(num_days):
                    is_prod_d = is_producing.get((grade, line, d), None)
                    if not is_prod_d: continue # skip if grade is not on line

                    # Define 'was_running_yesterday'
                    if d == 0:
                        # Production is deemed to start on day 0 if it is the planned startup material
                        initial_grade = plant_data['lines_data'][line]['material_running']
                        was_running_yesterday = (initial_grade == grade)
                    else:
                        was_running_yesterday = is_producing.get((grade, line, d-1), 0)
                    
                    # Define 'is_run_start_d' = is_producing[d] AND NOT was_running_yesterday
                    is_run_start_d = model.NewBoolVar(f'run_start_{grade}_{line}_{d}')
                    # Constraint: is_run_start_d <=> is_prod_d AND NOT was_running_yesterday
                    
                    if d == 0:
                        if was_running_yesterday:
                            # Cannot be a start if already running
                            model.Add(is_run_start_d == 0)
                        else:
                            # Start on day 0 is just is_prod_d
                            model.Add(is_run_start_d == is_prod_d)
                    else:
                        model.AddBoolOr([is_run_start_d.Not(), is_producing[(grade, line, d)]])
                        model.AddBoolOr([is_run_start_d.Not(), is_producing[(grade, line, d-1)].Not()])
                        model.AddImplication(is_producing[(grade, line, d)], is_run_start_d.Not()).OnlyEnforceIf(is_producing[(grade, line, d-1)])
                        
                        # Simplified way:
                        # is_run_start_d will be 1 if is_producing[d] is 1 and is_producing[d-1] is 0
                        model.AddBoolOr([is_producing[(grade, line, d)].Not(), is_producing[(grade, line, d-1)], is_run_start_d.Not()])
                        model.AddImplication(is_run_start_d, is_producing[(grade, line, d)])
                        model.AddImplication(is_run_start_d, is_producing[(grade, line, d-1)].Not())

                    
                    # Enforce min_run_days: If is_run_start_d, then production must be 1 for next min_run_days-1 days
                    if min_run_days > 1:
                        # The current grade must be produced on the current line for the next min_run_days-1 days
                        for k in range(1, min_run_days):
                            if d + k < num_days:
                                # Ensure is_producing[(grade, line, d+k)] is 1
                                is_prod_next_k = is_producing.get((grade, line, d + k), None)
                                if is_prod_next_k:
                                    model.AddImplication(is_run_start_d, is_prod_next_k)
                            else:
                                # If run extends beyond planning horizon, it's not a valid start
                                model.Add(is_run_start_d == 0)

    if progress_callback:
        progress_callback(0.5, "Minimum Run Day constraints added...")


    # C5. Shutdown constraints (Hard Constraint)
    for line in lines:
        if line in plant_data['shutdown_days']:
            shutdown_days_indices = plant_data['shutdown_days'][line]
            for d in shutdown_days_indices:
                if d < num_days:
                    # Production must be zero for all grades on this line on shutdown days
                    for grade in grades:
                        if (grade, line, d) in production:
                            model.Add(production[(grade, line, d)] == 0)
                            model.Add(is_producing[(grade, line, d)] == 0)

    if progress_callback:
        progress_callback(0.6, "Shutdown constraints added...")


    # C6. Transition rules (Soft Constraint and Hard Constraints)
    objective_terms = []
    
    for line in lines:
        plant_transition_rules = transition_rules.get(line, {})

        for d in range(num_days):
            # 1. Previous grade on line
            if d == 0:
                prev_grade = plant_data['lines_data'][line]['material_running']
                # The first day's run is subject to transition from 'material_running'
            else:
                # The grade running on day d-1 is the 'previous' grade for day d
                # We need a variable for the grade running on day d-1
                prev_grade_var = model.NewIntVar(0, len(grades), f'prev_grade_idx_{line}_{d}')
                # 0 is the index for idle/no production
                
                # Map the grade index to the grade running on day d-1
                # The grade index is based on the grades list (for simplicity, we use the grade name as key)
                
                # Check all grades for production on d-1
                was_producing_d_minus_1 = {}
                for grade in grades:
                    if (grade, line, d-1) in is_producing:
                        was_producing_d_minus_1[grade] = is_producing[(grade, line, d-1)]
                
                # Enforce that prev_grade_var is the index of the grade produced on day d-1
                # If was_producing[d-1] is 1, then prev_grade_var must be that grade's index.
                # Since only one grade can run, we can use a linear expression to determine the grade running.
                
                # We will simply check the transition penalty for all possible (prev_grade, current_grade) pairs
                
                for current_grade in grades:
                    is_prod_current = is_producing.get((current_grade, line, d), None)
                    if not is_prod_current: continue
                        
                    # 6a. Check transition from previous production day (d-1)
                    if d > 0:
                        for prev_grade_candidate in grades:
                            is_prod_prev = is_producing.get((prev_grade_candidate, line, d-1), None)
                            if not is_prod_prev: continue
                                
                            # Transition happens if: is_prod_prev=1 AND is_prod_current=1 AND prev_grade != current_grade
                            # Only applies if a grade change occurs.
                            if prev_grade_candidate != current_grade:
                                # Check if this transition is allowed
                                is_allowed = current_grade in plant_transition_rules.get(prev_grade_candidate, [])
                                
                                # Create a variable that is 1 if the forbidden transition occurs
                                is_forbidden_transition = model.NewBoolVar(f'forbidden_trans_{line}_{d}_{prev_grade_candidate}_{current_grade}')
                                
                                if not is_allowed:
                                    # Hard Constraint: Forbidden transition must not occur
                                    # is_prod_prev AND is_prod_current must be 0
                                    model.AddBoolOr([is_prod_prev.Not(), is_prod_current.Not()])
                                else:
                                    # Soft Constraint: Allowed transition might still incur a penalty (e.g., if re-run is not allowed)
                                    # For this problem, transition penalty only applies to a grade change.
                                    
                                    # is_transition = is_prod_prev AND is_prod_current AND (prev != current)
                                    
                                    # Check if the transition itself should incur a cost (e.g., for cleaning/setup)
                                    # We use the transition_penalty for any switch from one grade to another.
                                    is_transition_switch = model.NewBoolVar(f'trans_switch_{line}_{d}_{prev_grade_candidate}_{current_grade}')
                                    model.Add(is_transition_switch == 1).OnlyEnforceIf([is_prod_prev, is_prod_current])
                                    model.Add(is_transition_switch == 0).OnlyEnforceIf(is_prod_prev.Not())
                                    model.Add(is_transition_switch == 0).OnlyEnforceIf(is_prod_current.Not())
                                    
                                    objective_terms.append(transition_penalty * is_transition_switch)


            # 6b. Check transition from initial material running (d=0)
            if d == 0:
                prev_grade = plant_data['lines_data'][line]['material_running']
                is_prod_current = is_producing.get((current_grade, line, d), None)
                if not is_prod_current: continue
                
                if prev_grade != current_grade:
                    is_allowed = current_grade in plant_transition_rules.get(prev_grade, [])
                    
                    if not is_allowed:
                        # Hard Constraint: Forbidden transition from initial grade
                        model.Add(is_prod_current == 0)
                    else:
                        # Soft Constraint: Transition from initial grade to a different grade incurs penalty
                        is_transition_switch = model.NewBoolVar(f'trans_switch_{line}_{d}_initial_{current_grade}')
                        model.Add(is_transition_switch == is_prod_current)
                        objective_terms.append(transition_penalty * is_transition_switch)
                        
                # 6c. Check transition for Plant Restart/Pre-Shutdown Grades (Hard Constraint)
                # Plant Shutdown/Restart: Hard constraints on Pre-Shutdown/Restart Grade
                shutdown_info = plant_data['lines_data'][line]
                if d == num_days - 1 and shutdown_info['shutdown_end_date'] is not None:
                    # Constraint on pre-shutdown grade (must run the day before shutdown)
                    pre_shutdown_day = dates.index(shutdown_info['shutdown_start_date']) - 1
                    pre_shutdown_grade = shutdown_info['pre_shutdown_grade']
                    if d == pre_shutdown_day and pre_shutdown_grade:
                        if pre_shutdown_grade == current_grade:
                            # Must run this grade
                            model.Add(is_prod_current == 1)
                        else:
                            # Must not run other grades
                            model.Add(is_prod_current == 0)
                
                if d == 0 and shutdown_info['shutdown_start_date'] is not None:
                    # Constraint on restart grade (must run the day of restart)
                    restart_day = dates.index(shutdown_info['shutdown_end_date']) + 1
                    restart_grade = shutdown_info['restart_grade']
                    if d == restart_day and restart_grade:
                        if restart_grade == current_grade:
                            # Must run this grade
                            model.Add(is_prod_current == 1)
                        else:
                            # Must not run other grades
                            model.Add(is_prod_current == 0)


    if progress_callback:
        progress_callback(0.7, "Transition constraints added...")


    # --- 3. Soft Constraints (Objective Function) ---

    # Stockout Penalty (Soft Constraint)
    # The stockout variables are already defined. We just add the weighted sum to the objective.
    stockout_penalty_terms = []
    for grade in grades:
        for d in range(1, num_days + 1):
            stockout_penalty_terms.append(stockout_vars[(grade, d)] * stockout_penalty)
            
    objective_terms.extend(stockout_penalty_terms)


    # Minimum Closing Inventory Penalty (Soft Constraint)
    inventory_deficit_penalties = {}
    closing_inventory_deficit_penalties = {}
    
    for grade in grades:
        min_closing_inv = inventory_data['data'][grade]['min_closing_inv']
        
        # Min Closing Inventory (applies to the very last day)
        last_day = num_days
        deficit_var = model.NewIntVar(0, min_closing_inv, f'deficit_{grade}_closing')
        closing_inventory_deficit_penalties[grade] = deficit_var
        
        # Deficit = max(0, min_closing_inv - inventory_vars[(grade, last_day)])
        # min_closing_inv = inventory_vars[(grade, last_day)] + deficit_var
        model.Add(inventory_vars[(grade, last_day)] + deficit_var == min_closing_inv).OnlyEnforceIf(inventory_vars[(grade, last_day)] < min_closing_inv)
        model.Add(deficit_var == 0).OnlyEnforceIf(inventory_vars[(grade, last_day)] >= min_closing_inv)

        objective_terms.append(deficit_var * stockout_penalty) # Use stockout penalty for min closing inventory


    # Idle Line Penalty (Soft Constraint)
    for line in lines:
        for d in range(num_days):
            is_idle = model.NewBoolVar(f'idle_{line}_{d}')
            
            producing_vars = [
                is_producing[(grade, line, d)] 
                for grade in grades 
                if (grade, line, d) in is_producing
            ]
            
            if producing_vars:
                # Idle if none of the producing vars are 1
                model.Add(sum(producing_vars) == 0).OnlyEnforceIf(is_idle)
                model.Add(sum(producing_vars) >= 1).OnlyEnforceIf(is_idle.Not()) # If sum is 1, not idle
                
                # Check if the line is not in shutdown (already handled by C5, but as a double check)
                if d in plant_data['shutdown_days'].get(line, []):
                    model.Add(is_idle == 0) # Line is forced idle by shutdown, don't penalize
                else:
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
    
    # Pass all variables and parameters to the callback
    solution_callback = SolutionCallback(
        production, inventory_vars, stockout_vars, is_producing,
        grades, lines, dates, formatted_dates, num_days,
        inventory_deficit_penalties, closing_inventory_deficit_penalties
    )
    
    status = solver.Solve(model, solution_callback)
    
    if progress_callback:
        progress_callback(1.0, "Optimization complete!")
    
    return status, solution_callback, solver
