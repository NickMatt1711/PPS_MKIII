"""
CP-SAT Solver for production optimization
"""

from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED


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
            'time': current_time,
            'production': {},
            'inventory': {},
            'stockout': {},
            'is_producing': {}
        }

        # Store production data
        for grade in self.grades:
            solution['production'][grade] = {}
            for line in self.lines:
                for d in range(self.num_days):
                    key = (grade, line, d)
                    if key in self.production:
                        value = self.Value(self.production[key])
                        if value > 0:
                            date_key = self.formatted_dates[d]
                            if date_key not in solution['production'][grade]:
                                solution['production'][grade][date_key] = 0
                            solution['production'][grade][date_key] += value
        
        # Store inventory data - OPENING inventory for each day
        for grade in self.grades:
            solution['inventory'][grade] = {}
            
            # First date gets initial inventory
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.inventory:
                    # Map inventory at day d to the date for day d
                    # inventory_vars[(grade, d)] = opening inventory for day d
                    solution['inventory'][grade][self.formatted_dates[d]] = self.Value(self.inventory[key])
            
            # Store final closing inventory separately
            final_key = (grade, self.num_days)
            if final_key in self.inventory:
                solution['inventory'][grade]['final'] = self.Value(self.inventory[final_key])
        
        # Store stockout data
        for grade in self.grades:
            solution['stockout'][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.stockout:
                    value = self.Value(self.stockout[key])
                    if value > 0:
                        solution['stockout'][grade][self.formatted_dates[d]] = value
        
        # Store production schedule
        for line in self.lines:
            solution['is_producing'][line] = {}
            for d in range(self.num_days):
                date_key = self.formatted_dates[d]
                solution['is_producing'][line][date_key] = None
                for grade in self.grades:
                    key = (grade, line, d)
                    if key in self.is_producing and self.Value(self.is_producing[key]) == 1:
                        solution['is_producing'][line][date_key] = grade
                        break

        # Count transitions
        transition_count_per_line = {line: 0 for line in self.lines}
        total_transitions = 0

        for line in self.lines:
            last_grade = None
            for d in range(self.num_days):
                current_grade = None
                for grade in self.grades:
                    key = (grade, line, d)
                    if key in self.is_producing and self.Value(self.is_producing[key]) == 1:
                        current_grade = grade
                        break
                
                if current_grade is not None:
                    if last_grade is not None and current_grade != last_grade:
                        transition_count_per_line[line] += 1
                        total_transitions += 1
                    last_grade = current_grade

        solution['transitions'] = {
            'per_line': transition_count_per_line,
            'total': total_transitions
        }
        
        # Calculate objective breakdown
        breakdown = self.calculate_objective_breakdown(current_obj)
        solution['objective_breakdown'] = breakdown
        self.objective_breakdowns.append(breakdown)

        self.solutions.append(solution)

    def calculate_objective_breakdown(self, solver_objective):
        """Calculate detailed breakdown of the objective value"""
        breakdown = {
            'stockout': 0,
            'transitions': 0,
            'solver_objective': solver_objective,
            'calculated_total': 0
        }
        return breakdown

    def num_solutions(self):
        return len(self.solutions)


def build_and_solve_model(
    grades: List[str],
    lines: List[str],
    dates: List,
    formatted_dates: List[str],
    num_days: int,
    capacities: Dict,
    initial_inventory: Dict,
    min_inventory: Dict,
    max_inventory: Dict,
    min_closing_inventory: Dict,
    demand_data: Dict,
    allowed_lines: Dict,
    min_run_days: Dict,
    max_run_days: Dict,
    force_start_date: Dict,
    rerun_allowed: Dict,
    material_running_info: Dict,
    shutdown_periods: Dict,
    transition_rules: Dict,
    buffer_days: int,
    stockout_penalty: int,
    transition_penalty: int,
    continuity_bonus: int,
    time_limit_min: int,
    progress_callback=None
) -> Tuple[int, SolutionCallback, cp_model.CpSolver]:
    """Build and solve the optimization model"""
    
    if progress_callback:
        progress_callback(0.0, "Building optimization model...")
    
    model = cp_model.CpModel()
    
    # Decision variables
    is_producing = {}
    production = {}
    
    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])
    
    # Create production variables
    for grade in grades:
        for line in allowed_lines[grade]:
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                
                # Always enforce full capacity or zero (HARD CONSTRAINT)
                production_value = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                model.Add(production_value == capacities[line]).OnlyEnforceIf(is_producing[key])
                model.Add(production_value == 0).OnlyEnforceIf(is_producing[key].Not())
                production[key] = production_value
    
    # Helper functions
    def get_production_var(grade, line, d):
        key = (grade, line, d)
        return production.get(key, 0)
    
    def get_is_producing_var(grade, line, d):
        key = (grade, line, d)
        return is_producing.get(key)
    
    if progress_callback:
        progress_callback(0.1, "Adding hard constraints...")
    
    # ========== HARD CONSTRAINTS ==========
    
    # 1. Shutdown constraints (HARD)
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        key = (grade, line, d)
                        if key in is_producing:
                            model.Add(is_producing[key] == 0)
                            model.Add(production[key] == 0)
    
    # 2. One grade per line per day (HARD)
    for line in lines:
        for d in range(num_days):
            producing_vars = []
            for grade in grades:
                if is_allowed_combination(grade, line):
                    var = get_is_producing_var(grade, line, d)
                    if var is not None:
                        producing_vars.append(var)
            if producing_vars:
                model.Add(sum(producing_vars) <= 1)
    
    # 3. Material running constraints (HARD)
    # Track which lines have initial forced running
    initial_running_info = {}
    for plant, (material, expected_days) in material_running_info.items():
        initial_running_info[plant] = {
            'material': material,
            'expected_days': expected_days
        }
        for d in range(min(expected_days, num_days)):
            if is_allowed_combination(material, plant):
                model.Add(get_is_producing_var(material, plant, d) == 1)
                for other_material in grades:
                    if other_material != material and is_allowed_combination(other_material, plant):
                        model.Add(get_is_producing_var(other_material, plant, d) == 0)
    
    if progress_callback:
        progress_callback(0.2, "Adding inventory constraints...")
    
    # Inventory variables
    inventory_vars = {}
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 100000, f'inventory_{grade}_{d}')
    
    stockout_vars = {}
    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 100000, f'stockout_{grade}_{d}')
    
    # Inventory balance (HARD - must satisfy)
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == initial_inventory[grade])
    
    for grade in grades:
        for d in range(num_days):
            produced_today = sum(
                get_production_var(grade, line, d) 
                for line in allowed_lines[grade]
            )
            demand_today = demand_data[grade].get(dates[d], 0)
            
            supplied = model.NewIntVar(0, 100000, f'supplied_{grade}_{d}')
            model.Add(supplied <= inventory_vars[(grade, d)] + produced_today)
            model.Add(supplied <= demand_today)
            
            model.Add(stockout_vars[(grade, d)] == demand_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)
    
    # Maximum inventory (HARD)
    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= max_inventory[grade])
    
    if progress_callback:
        progress_callback(0.3, "Adding capacity constraints...")
    
    # 4. Full capacity utilization (HARD - except shutdown days)
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            production_vars = [
                get_production_var(grade, line, d) 
                for grade in grades 
                if is_allowed_combination(grade, line)
            ]
            if production_vars:
                # Line must produce at full capacity
                model.Add(sum(production_vars) == capacities[line])
    
    if progress_callback:
        progress_callback(0.4, "Adding run constraints...")
    
    # 5. Force start date constraints (HARD)
    for grade_plant_key, start_date in force_start_date.items():
        if start_date:
            grade, plant = grade_plant_key
            try:
                start_day_index = dates.index(start_date)
                var = get_is_producing_var(grade, plant, start_day_index)
                if var is not None:
                    model.Add(var == 1)
            except ValueError:
                pass
    
    # ========== CORRECTED MIN/MAX RUN DAYS LOGIC ==========
    
    for grade in grades:
        for line in allowed_lines[grade]:
            grade_plant_key = (grade, line)
            min_run = min_run_days.get(grade_plant_key, 1)
            max_run = max_run_days.get(grade_plant_key, 9999)
            
            # Check if this line has initial forced running
            is_initial_running = (line in initial_running_info and 
                                 initial_running_info[line]['material'] == grade)
            initial_run_days = initial_running_info[line]['expected_days'] if is_initial_running else 0
            
            # Create run start and end indicators
            run_starts = []
            run_ends = []
            
            # ========== SIMPLE BUT EFFECTIVE MIN-RUN CONSTRAINT ==========
            # For each day, if we're producing, check forward to ensure min-run days
            
            for start_day in range(num_days):
                # Skip if beyond the planning horizon for min_run check
                if start_day + min_run > num_days:
                    continue
                
                # Check if this could be the start of a new run
                # A run starts if:
                # 1. We're producing this grade on start_day
                # 2. Either start_day == 0 OR we're not producing this grade on start_day-1
                
                # But wait - if this is within initial forced running period,
                # it's not a "new start", it's a continuation
                
                is_possible_start = True
                if is_initial_running:
                    # If we're in the initial forced running period, this is not a new start
                    if start_day < initial_run_days:
                        is_possible_start = False
                    # Also, the day after initial forced running ends could be a start
                    # if we continue with the same grade
                    elif start_day == initial_run_days:
                        # Check if we were producing yesterday (last day of initial run)
                        if start_day > 0:
                            prev_var = get_is_producing_var(grade, line, start_day - 1)
                            if prev_var is not None:
                                # If we were producing yesterday, this is continuation, not start
                                is_possible_start = False
                
                if not is_possible_start:
                    continue
                
                # Create a variable that indicates a run starts at start_day
                run_starts_at = model.NewBoolVar(f'run_starts_{grade}_{line}_{start_day}')
                run_starts.append(run_starts_at)
                
                # Link run_starts_at to production variables:
                # run_starts_at = 1 if:
                # 1. Producing at start_day
                # 2. AND (start_day == 0 OR not producing at start_day-1)
                
                prod_at_start = get_is_producing_var(grade, line, start_day)
                if prod_at_start is None:
                    continue
                
                # Condition 1: Must be producing at start_day
                model.Add(run_starts_at <= prod_at_start)
                
                # Condition 2: If start_day > 0, must NOT be producing at start_day-1
                if start_day > 0:
                    prod_before = get_is_producing_var(grade, line, start_day - 1)
                    if prod_before is not None:
                        model.Add(run_starts_at <= 1 - prod_before)
                
                # Condition 3: If run_starts_at = 1, then we must produce for min_run days
                # Collect production variables for the next min_run days
                run_days_vars = []
                valid_for_min_run = True
                
                for offset in range(min_run):
                    day_idx = start_day + offset
                    if day_idx >= num_days:
                        valid_for_min_run = False
                        break
                    
                    # Skip shutdown days (they break the run)
                    if line in shutdown_periods and day_idx in shutdown_periods[line]:
                        valid_for_min_run = False
                        break
                    
                    prod_var = get_is_producing_var(grade, line, day_idx)
                    if prod_var is not None:
                        run_days_vars.append(prod_var)
                    else:
                        valid_for_min_run = False
                        break
                
                # If we have enough valid days, enforce min-run constraint
                if valid_for_min_run and len(run_days_vars) == min_run:
                    # If this is a start, all run_days_vars must be 1
                    for prod_var in run_days_vars:
                        model.Add(prod_var == 1).OnlyEnforceIf(run_starts_at)
            
            # ========== MAX RUN DAYS CONSTRAINT ==========
            # Cannot produce same grade for more than max_run consecutive days
            for start_day in range(num_days - max_run):
                # Check sequence of max_run + 1 days
                consecutive_vars = []
                valid_sequence = True
                
                for offset in range(max_run + 1):
                    day_idx = start_day + offset
                    if day_idx >= num_days:
                        valid_sequence = False
                        break
                    
                    # Shutdown days break the sequence
                    if line in shutdown_periods and day_idx in shutdown_periods[line]:
                        valid_sequence = False
                        break
                    
                    prod_var = get_is_producing_var(grade, line, day_idx)
                    if prod_var is not None:
                        consecutive_vars.append(prod_var)
                    else:
                        valid_sequence = False
                        break
                
                if valid_sequence and len(consecutive_vars) == max_run + 1:
                    # Cannot have all max_run+1 days as 1
                    model.Add(sum(consecutive_vars) <= max_run)
            
            # ========== RERUN ALLOWED CONSTRAINT ==========
            if not rerun_allowed.get(grade_plant_key, True):
                # Count how many times this grade starts a run
                # But exclude initial forced running from the count
                count_starts = []
                for start_day in range(num_days):
                    # Skip if this is within initial forced running
                    if is_initial_running and start_day < initial_run_days:
                        continue
                    
                    # Check if this could be a start
                    if start_day >= num_days:
                        continue
                    
                    # Create a start indicator
                    start_indicator = model.NewBoolVar(f'rerun_start_{grade}_{line}_{start_day}')
                    
                    prod_today = get_is_producing_var(grade, line, start_day)
                    if prod_today is None:
                        continue
                    
                    # Condition: start if producing today AND (day 0 OR not producing yesterday)
                    if start_day == 0:
                        model.Add(start_indicator == prod_today)
                    else:
                        prod_yesterday = get_is_producing_var(grade, line, start_day - 1)
                        if prod_yesterday is not None:
                            # start_indicator = prod_today AND NOT prod_yesterday
                            model.Add(start_indicator <= prod_today)
                            model.Add(start_indicator <= 1 - prod_yesterday)
                            model.Add(start_indicator >= prod_today - prod_yesterday)
                    
                    count_starts.append(start_indicator)
                
                if count_starts:
                    # Can start at most once (excluding initial forced running)
                    model.Add(sum(count_starts) <= 1)
    
    if progress_callback:
        progress_callback(0.5, "Adding transition constraints...")
    
    # 6. Forbidden transitions (HARD)
    for line in lines:
        if transition_rules.get(line):
            for d in range(num_days - 1):
                for prev_grade in grades:
                    if prev_grade in transition_rules[line] and is_allowed_combination(prev_grade, line):
                        allowed_next = transition_rules[line][prev_grade]
                        for current_grade in grades:
                            if (current_grade != prev_grade and 
                                current_grade not in allowed_next and 
                                is_allowed_combination(current_grade, line)):
                                
                                prev_var = get_is_producing_var(prev_grade, line, d)
                                current_var = get_is_producing_var(current_grade, line, d + 1)
                                
                                if prev_var is not None and current_var is not None:
                                    # HARD CONSTRAINT: Cannot have forbidden transition
                                    model.Add(prev_var + current_var <= 1)
    
    if progress_callback:
        progress_callback(0.6, "Adding soft constraints...")
    
    # ========== SOFT CONSTRAINTS ==========
    # These go into the objective function with penalties
    
    # Create explicit penalty variables for SOFT constraints
    inventory_deficit_penalties = {}
    closing_inventory_deficit_penalties = {}
    
    # 1. Minimum inventory (SOFT)
    for grade in grades:
        for d in range(num_days):
            if min_inventory[grade] > 0:
                min_inv_value = int(min_inventory[grade])
                inventory_tomorrow = inventory_vars[(grade, d + 1)]
                
                deficit_var = model.NewIntVar(0, 100000, f'inv_deficit_{grade}_{d}')
                model.Add(deficit_var >= min_inv_value - inventory_tomorrow)
                model.Add(deficit_var >= 0)
                
                inventory_deficit_penalties[(grade, d)] = deficit_var
        
        # Minimum closing inventory (SOFT)
        if min_closing_inventory[grade] > 0 and buffer_days > 0:
            closing_inventory = inventory_vars[(grade, num_days - buffer_days)]
            min_closing = min_closing_inventory[grade]
            
            closing_deficit_var = model.NewIntVar(0, 100000, f'closing_deficit_{grade}')
            model.Add(closing_deficit_var >= min_closing - closing_inventory)
            model.Add(closing_deficit_var >= 0)
            
            closing_inventory_deficit_penalties[grade] = closing_deficit_var
    
    if progress_callback:
        progress_callback(0.7, "Building objective function...")
    
    # ========== OBJECTIVE FUNCTION ==========
    # Only contains SOFT constraints with penalties
    
    objective_terms = []
    
    # 1. Stockout penalties (SOFT)
    for grade in grades:
        for d in range(num_days):
            if (grade, d) in stockout_vars:
                objective_terms.append(stockout_penalty * stockout_vars[(grade, d)])
    
    # 2. Inventory deficit penalties (SOFT)
    for (grade, d), deficit_var in inventory_deficit_penalties.items():
        objective_terms.append(stockout_penalty * deficit_var)
    
    # 3. Closing inventory deficit penalties (SOFT)
    for grade, closing_deficit_var in closing_inventory_deficit_penalties.items():
        objective_terms.append(stockout_penalty * closing_deficit_var * 3)
    
    # 4. Transition penalties (SOFT - for ALLOWED transitions only)
    # Forbidden transitions are already prevented by HARD constraints
    for line in lines:
        for d in range(num_days - 1):
            for grade1 in grades:
                if line not in allowed_lines[grade1]:
                    continue
                for grade2 in grades:
                    if line not in allowed_lines[grade2] or grade1 == grade2:
                        continue
                    
                    # Skip if this is a forbidden transition (already handled as HARD)
                    if (transition_rules.get(line) and 
                        grade1 in transition_rules[line] and 
                        grade2 not in transition_rules[line][grade1]):
                        continue
                    
                    # Only penalize ALLOWED transitions
                    trans_var = model.NewBoolVar(f'trans_{line}_{d}_{grade1}_to_{grade2}')
                    
                    # Link transition variable to production decisions
                    model.Add(trans_var <= is_producing[(grade1, line, d)])
                    model.Add(trans_var <= is_producing[(grade2, line, d + 1)])
                    model.Add(trans_var >= is_producing[(grade1, line, d)] + 
                              is_producing[(grade2, line, d + 1)] - 1)
                    
                    objective_terms.append(transition_penalty * trans_var)
    
    # 5. Idle line penalty (SOFT - to minimize gaps, but not required)
    idle_penalty = 500  # Lower than transition penalty to prioritize min runs
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
                
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
    
    if progress_callback:
        progress_callback(1.0, "Optimization complete!")
    
    return status, solution_callback, solver
