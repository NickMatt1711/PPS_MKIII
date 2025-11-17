# solver_cp_sat.py
"""
CP-SAT solver implementing robust constraints from old logic (without continuity bonus).
"""

from ortools.sat.python import cp_model
import time
import pandas as pd
from datetime import timedelta

class SolutionCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, production, inventory, stockout, is_producing, grades, lines, dates, formatted_dates, num_days):
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
        self.solutions = []
        self.solution_times = []
        self.start_time = time.time()

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

        # Collect production data
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
        
        # Collect inventory data
        for grade in self.grades:
            solution['inventory'][grade] = {}
            for d in range(self.num_days + 1):
                key = (grade, d)
                if key in self.inventory:
                    if d < self.num_days:
                        solution['inventory'][grade][self.formatted_dates[d] if d > 0 else 'initial'] = self.Value(self.inventory[key])
                    else:
                        solution['inventory'][grade]['final'] = self.Value(self.inventory[key])
        
        # Collect stockout data
        for grade in self.grades:
            solution['stockout'][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.stockout:
                    value = self.Value(self.stockout[key])
                    if value > 0:
                        solution['stockout'][grade][self.formatted_dates[d]] = value
        
        # Collect production assignments
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

        self.solutions.append(solution)

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

    def num_solutions(self):
        return len(self.solutions)

def solve(instance, parameters):
    # Extract data from instance
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    capacities = instance['capacities']
    initial_inventory = instance['initial_inventory']
    min_inventory = instance.get('min_inventory', {})
    max_inventory = instance.get('max_inventory', {})
    min_closing_inventory = instance.get('min_closing_inventory', {})
    demand_data = instance['demand']
    allowed_lines = instance['allowed_lines']
    min_run_days = instance.get('min_run_days', {})
    max_run_days = instance.get('max_run_days', {})
    force_start_date = instance.get('force_start_date', {})
    rerun_allowed = instance.get('rerun_allowed', {})
    shutdown_periods = instance.get('shutdown_day_indices', {})
    transition_rules = instance.get('transition_rules', {})
    material_running_info = instance.get('material_running_info', {})
    
    # Extract parameters
    time_limit_min = parameters.get('time_limit_min', 10)
    stockout_penalty = parameters.get('stockout_penalty', 10)
    transition_penalty = parameters.get('transition_penalty', 10)
    buffer_days = parameters.get('buffer_days', 3)
    num_search_workers = parameters.get('num_search_workers', 8)
    
    num_days = len(dates)
    formatted_dates = [date.strftime('%d-%b-%y') for date in dates]
    
    model = cp_model.CpModel()
    
    # Variables
    is_producing = {}
    production = {}
    
    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])
    
    # Create production and assignment variables
    for grade in grades:
        for line in allowed_lines[grade]:
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                
                # Different capacity constraints for buffer days
                if d < num_days - buffer_days:
                    production_value = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                    model.Add(production_value == capacities[line]).OnlyEnforceIf(is_producing[key])
                    model.Add(production_value == 0).OnlyEnforceIf(is_producing[key].Not())
                else:
                    production_value = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                    model.Add(production_value <= capacities[line] * is_producing[key])
                
                production[key] = production_value
    
    def get_production_var(grade, line, d):
        key = (grade, line, d)
        return production.get(key, 0)
    
    def get_is_producing_var(grade, line, d):
        key = (grade, line, d)
        return is_producing.get(key, None)
    
    # SHUTDOWN CONSTRAINTS: No production during shutdown periods
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        key = (grade, line, d)
                        if key in is_producing:
                            model.Add(is_producing[key] == 0)
                            model.Add(production[key] == 0)
    
    # One grade per line per day
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
    
    # Material running constraints
    for plant, (material, expected_days) in material_running_info.items():
        for d in range(min(expected_days, num_days)):
            if is_allowed_combination(material, plant):
                model.Add(get_is_producing_var(material, plant, d) == 1)
                for other_material in grades:
                    if other_material != material and is_allowed_combination(other_material, plant):
                        model.Add(get_is_producing_var(other_material, plant, d) == 0)
    
    # Inventory and stockout variables
    inventory_vars = {}
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 1000000, f'inventory_{grade}_{d}')
    
    stockout_vars = {}
    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 1000000, f'stockout_{grade}_{d}')
    
    # Initialize inventory
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == initial_inventory.get(grade, 0))
    
    # INVENTORY BALANCE with proper stockout handling (from old logic)
    for grade in grades:
        for d in range(num_days):
            produced_today = sum(
                get_production_var(grade, line, d) 
                for line in allowed_lines[grade]
            )
            demand_today = demand_data.get((grade, d), 0)
            
            # Sophisticated inventory balance
            supplied = model.NewIntVar(0, 1000000, f'supplied_{grade}_{d}')
            model.Add(supplied <= inventory_vars[(grade, d)] + produced_today)
            model.Add(supplied <= demand_today)
            
            # Stockout calculation
            model.Add(stockout_vars[(grade, d)] == demand_today - supplied)
            
            # Inventory update
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)
    
    # OBJECTIVE FUNCTION
    objective = 0
    
    # Stockout penalties
    for grade in grades:
        for d in range(num_days):
            objective += stockout_penalty * stockout_vars[(grade, d)]
    
    # Minimum inventory soft constraints (as penalties)
    for grade in grades:
        for d in range(num_days):
            if min_inventory.get(grade, 0) > 0:
                min_inv_value = int(min_inventory[grade])
                inventory_tomorrow = inventory_vars[(grade, d + 1)]
                
                deficit = model.NewIntVar(0, 1000000, f'deficit_{grade}_{d}')
                model.Add(deficit >= min_inv_value - inventory_tomorrow)
                model.Add(deficit >= 0)
                objective += stockout_penalty * deficit
    
    # Minimum Closing Inventory constraint (soft)
    for grade in grades:
        closing_inventory = inventory_vars[(grade, num_days - buffer_days)]
        min_closing = min_closing_inventory.get(grade, 0)
        
        if min_closing > 0:
            closing_deficit = model.NewIntVar(0, 1000000, f'closing_deficit_{grade}')
            model.Add(closing_deficit >= min_closing - closing_inventory)
            model.Add(closing_deficit >= 0)
            objective += stockout_penalty * closing_deficit * 3  # Higher penalty
    
    # Maximum inventory constraints
    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= max_inventory.get(grade, 1000000))
    
    # Capacity constraints with buffer day relaxation
    for line in lines:
        for d in range(num_days - buffer_days):
            # Skip shutdown days for full capacity requirement
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            production_vars = [
                get_production_var(grade, line, d) 
                for grade in grades 
                if is_allowed_combination(grade, line)
            ]
            if production_vars:
                model.Add(sum(production_vars) == capacities[line])
        
        for d in range(num_days - buffer_days, num_days):
            production_vars = [
                get_production_var(grade, line, d) 
                for grade in grades 
                if is_allowed_combination(grade, line)
            ]
            if production_vars:
                model.Add(sum(production_vars) <= capacities[line])
    
    # Force Start Date constraints
    for grade_plant_key, start_date in force_start_date.items():
        if start_date:
            grade, plant = grade_plant_key
            try:
                start_day_index = dates.index(start_date)
                var = get_is_producing_var(grade, plant, start_day_index)
                if var is not None:
                    model.Add(var == 1)
            except ValueError:
                pass  # Force date not in planning horizon
    
    # Run length constraints with shutdown awareness
    is_start_vars = {}
    run_end_vars = {}
    
    for grade in grades:
        for line in allowed_lines[grade]:
            grade_plant_key = (grade, line)
            min_run = min_run_days.get(grade_plant_key, 1)
            max_run = max_run_days.get(grade_plant_key, 9999)
            
            # Create start and end variables
            for d in range(num_days):
                is_start = model.NewBoolVar(f'start_{grade}_{line}_{d}')
                is_start_vars[(grade, line, d)] = is_start
                
                is_end = model.NewBoolVar(f'end_{grade}_{line}_{d}')
                run_end_vars[(grade, line, d)] = is_end
                
                current_prod = get_is_producing_var(grade, line, d)
                
                # Start definition
                if d > 0:
                    prev_prod = get_is_producing_var(grade, line, d - 1)
                    if current_prod is not None and prev_prod is not None:
                        model.AddBoolAnd([current_prod, prev_prod.Not()]).OnlyEnforceIf(is_start)
                        model.AddBoolOr([current_prod.Not(), prev_prod]).OnlyEnforceIf(is_start.Not())
                else:
                    if current_prod is not None:
                        model.Add(current_prod == 1).OnlyEnforceIf(is_start)
                        model.Add(is_start == 1).OnlyEnforceIf(current_prod)
                
                # End definition
                if d < num_days - 1:
                    next_prod = get_is_producing_var(grade, line, d + 1)
                    if current_prod is not None and next_prod is not None:
                        model.AddBoolAnd([current_prod, next_prod.Not()]).OnlyEnforceIf(is_end)
                        model.AddBoolOr([current_prod.Not(), next_prod]).OnlyEnforceIf(is_end.Not())
                else:
                    if current_prod is not None:
                        model.Add(current_prod == 1).OnlyEnforceIf(is_end)
                        model.Add(is_end == 1).OnlyEnforceIf(current_prod)
            
            # MINIMUM RUN DAYS with shutdown awareness
            for d in range(num_days):
                is_start = is_start_vars[(grade, line, d)]
                
                # Check consecutive non-shutdown days
                max_possible_run = 0
                for k in range(min_run):
                    if d + k < num_days:
                        if line in shutdown_periods and (d + k) in shutdown_periods[line]:
                            break
                        max_possible_run += 1
                
                if max_possible_run >= min_run:
                    for k in range(min_run):
                        if d + k < num_days:
                            if line in shutdown_periods and (d + k) in shutdown_periods[line]:
                                continue
                            future_prod = get_is_producing_var(grade, line, d + k)
                            if future_prod is not None:
                                model.Add(future_prod == 1).OnlyEnforceIf(is_start)
            
            # MAXIMUM RUN DAYS
            for d in range(num_days - max_run):
                consecutive_days = []
                for k in range(max_run + 1):
                    if d + k < num_days:
                        if line in shutdown_periods and (d + k) in shutdown_periods[line]:
                            break
                        prod_var = get_is_producing_var(grade, line, d + k)
                        if prod_var is not None:
                            consecutive_days.append(prod_var)
                
                if len(consecutive_days) == max_run + 1:
                    model.Add(sum(consecutive_days) <= max_run)
    
    # Transition constraints
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
                                    model.Add(prev_var + current_var <= 1)
    
    # Transition penalties in objective
    for line in lines:
        for d in range(num_days - 1):
            transition_vars = []
            for grade1 in grades:
                if line not in allowed_lines[grade1]:
                    continue
                for grade2 in grades:
                    if line not in allowed_lines[grade2] or grade1 == grade2:
                        continue
                    if transition_rules.get(line) and grade1 in transition_rules[line] and grade2 not in transition_rules[line][grade1]:
                        continue
                    trans_var = model.NewBoolVar(f'trans_{line}_{d}_{grade1}_to_{grade2}')
                    model.AddBoolAnd([is_producing[(grade1, line, d)], is_producing[(grade2, line, d + 1)]]).OnlyEnforceIf(trans_var)
                    model.Add(trans_var == 0).OnlyEnforceIf(is_producing[(grade1, line, d)].Not())
                    model.Add(trans_var == 0).OnlyEnforceIf(is_producing[(grade2, line, d + 1)].Not())
                    transition_vars.append(trans_var)
                    objective += transition_penalty * trans_var
    
    # Rerun Allowed Constraints
    for grade in grades:
        for line in allowed_lines[grade]:
            grade_plant_key = (grade, line)
            if not rerun_allowed.get(grade_plant_key, True):
                starts = [is_start_vars[(grade, line, d)] for d in range(num_days) 
                         if (grade, line, d) in is_start_vars]
                if starts:
                    model.Add(sum(starts) <= 1)
    
    # Set objective
    model.Minimize(objective)
    
    # Solve with callback
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60.0
    solver.parameters.num_search_workers = num_search_workers
    solver.parameters.random_seed = 42
    
    solution_callback = SolutionCallback(production, inventory_vars, stockout_vars, is_producing, grades, lines, dates, formatted_dates, num_days)
    
    start_time = time.time()
    status = solver.Solve(model, solution_callback)
    
    # Prepare result
    status_name = solver.StatusName(status)
    
    result = {
        'status': status_name,
        'solver': solver,
        'solutions': solution_callback.solutions,
        'best': solution_callback.solutions[-1] if solution_callback.solutions else None,
        'objective': solver.ObjectiveValue() if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else None
    }
    
    return result
