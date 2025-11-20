"""
CP-SAT Solver Module - Scalable
===============================

Solves production scheduling with:
1. Inventory & stockout constraints
2. Min/max run days
3. Force start dates
4. Shutdown periods
5. Line capacities
6. Forbidden/allowed transitions (Yes/No matrix)
7. Minimize valid transitions as objective
"""

import time
from typing import Dict, Any
from ortools.sat.python import cp_model

def solve(instance: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    CP-SAT solver for production scheduling
    """
    # Extract parameters
    buffer_days = parameters.get('buffer_days', 3)
    time_limit_min = parameters.get('time_limit_min', 10)
    stockout_penalty = parameters.get('stockout_penalty', 10)
    transition_penalty = parameters.get('transition_penalty', 50)
    
    # Extract problem data
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = instance['num_days']
    capacities = instance['capacities']
    demand_data = instance['demand_data']
    initial_inventory = instance['initial_inventory']
    min_inventory = instance['min_inventory']
    max_inventory = instance['max_inventory']
    min_closing_inventory = instance['min_closing_inventory']
    min_run_days = instance['min_run_days']
    max_run_days = instance['max_run_days']
    force_start_date = instance['force_start_date']
    allowed_lines = instance['allowed_lines']
    rerun_allowed = instance['rerun_allowed']
    shutdown_periods = instance['shutdown_periods']
    transition_rules = instance['transition_rules']  # "Yes"/"No" matrix per line
    material_running_info = instance['material_running_info']
    
    model = cp_model.CpModel()
    
    # ---------------------------
    # Variables
    # ---------------------------
    is_producing = {}
    production = {}

    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])
    
    for grade in grades:
        for line in allowed_lines[grade]:
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                
                # Production variable
                if d < num_days - buffer_days:
                    production_value = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                    model.Add(production_value == capacities[line]).OnlyEnforceIf(is_producing[key])
                    model.Add(production_value == 0).OnlyEnforceIf(is_producing[key].Not())
                else:
                    production_value = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                    model.Add(production_value <= capacities[line] * is_producing[key])
                
                production[key] = production_value
    
    def get_production_var(grade, line, d):
        return production.get((grade, line, d), 0)
    
    def get_is_producing_var(grade, line, d):
        return is_producing.get((grade, line, d), None)
    
    # ---------------------------
    # Shutdown constraints
    # ---------------------------
    for line, shutdown_days in shutdown_periods.items():
        for d in shutdown_days:
            for grade in grades:
                if is_allowed_combination(grade, line):
                    key = (grade, line, d)
                    if key in is_producing:
                        model.Add(is_producing[key] == 0)
                        model.Add(production[key] == 0)
    
    # ---------------------------
    # Inventory and stockout variables
    # ---------------------------
    inventory_vars = {}
    stockout_vars = {}
    
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 100000, f'inventory_{grade}_{d}')
    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 100000, f'stockout_{grade}_{d}')
    
    # ---------------------------
    # One grade per line constraint
    # ---------------------------
    for line in lines:
        for d in range(num_days):
            vars_today = [get_is_producing_var(g, line, d) for g in grades
                          if is_allowed_combination(g, line) and get_is_producing_var(g, line, d)]
            if vars_today:
                model.Add(sum(vars_today) <= 1)
    
    # ---------------------------
    # Material running constraints
    # ---------------------------
    for plant, (material, expected_days) in material_running_info.items():
        for d in range(min(expected_days, num_days)):
            if is_allowed_combination(material, plant):
                model.Add(get_is_producing_var(material, plant, d) == 1)
                for other in grades:
                    if other != material and is_allowed_combination(other, plant):
                        model.Add(get_is_producing_var(other, plant, d) == 0)
    
    # ---------------------------
    # Inventory balance
    # ---------------------------
    objective = 0
    
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == initial_inventory[grade])
    
    for grade in grades:
        for d in range(num_days):
            produced_today = sum(get_production_var(grade, line, d) for line in allowed_lines[grade])
            demand_today = demand_data[grade].get(dates[d], 0)
            
            supplied = model.NewIntVar(0, 100000, f'supplied_{grade}_{d}')
            model.Add(supplied <= inventory_vars[(grade, d)] + produced_today)
            model.Add(supplied <= int(demand_today))
            model.Add(stockout_vars[(grade, d)] == int(demand_today) - supplied)
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)
    
    # Minimum inventory penalties
    for grade in grades:
        for d in range(num_days):
            if min_inventory[grade] > 0:
                min_inv_val = int(min_inventory[grade])
                deficit = model.NewIntVar(0, 100000, f'deficit_{grade}_{d}')
                model.Add(deficit >= min_inv_val - inventory_vars[(grade, d + 1)])
                model.Add(deficit >= 0)
                objective += stockout_penalty * deficit
    
    # Minimum closing inventory
    for grade in grades:
        closing_inventory = inventory_vars[(grade, num_days - buffer_days)]
        min_closing = min_closing_inventory[grade]
        if min_closing > 0:
            closing_deficit = model.NewIntVar(0, 100000, f'closing_deficit_{grade}')
            model.Add(closing_deficit >= min_closing - closing_inventory)
            model.Add(closing_deficit >= 0)
            objective += stockout_penalty * closing_deficit * 3
    
    # Max inventory
    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= max_inventory[grade])
    
    # ---------------------------
    # Capacity constraints
    # ---------------------------
    for line in lines:
        # Non-buffer days
        for d in range(num_days - buffer_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            production_vars = [get_production_var(g, line, d) for g in grades if is_allowed_combination(g, line)]
            if production_vars:
                model.Add(sum(production_vars) == capacities[line])
        # Buffer days
        for d in range(num_days - buffer_days, num_days):
            production_vars = [get_production_var(g, line, d) for g in grades if is_allowed_combination(g, line)]
            if production_vars:
                model.Add(sum(production_vars) <= capacities[line])
    
    # ---------------------------
    # Force start dates
    # ---------------------------
    for (grade, line), start_date in force_start_date.items():
        if start_date:
            try:
                start_idx = dates.index(start_date)
                var = get_is_producing_var(grade, line, start_idx)
                if var is not None:
                    model.Add(var == 1)
            except ValueError:
                pass
    
    # ---------------------------
    # Run length constraints
    # ---------------------------
    is_start_vars = {}
    run_end_vars = {}
    
    for grade in grades:
        for line in allowed_lines[grade]:
            min_run = min_run_days.get((grade, line), 1)
            max_run = max_run_days.get((grade, line), 9999)
            for d in range(num_days):
                is_start = model.NewBoolVar(f'start_{grade}_{line}_{d}')
                is_start_vars[(grade, line, d)] = is_start
                is_end = model.NewBoolVar(f'end_{grade}_{line}_{d}')
                run_end_vars[(grade, line, d)] = is_end
                
                curr = get_is_producing_var(grade, line, d)
                # Start definition
                if d > 0:
                    prev = get_is_producing_var(grade, line, d - 1)
                    if curr and prev:
                        model.AddBoolAnd([curr, prev.Not()]).OnlyEnforceIf(is_start)
                        model.AddBoolOr([curr.Not(), prev]).OnlyEnforceIf(is_start.Not())
                else:
                    if curr:
                        model.Add(curr == 1).OnlyEnforceIf(is_start)
                        model.Add(is_start == 1).OnlyEnforceIf(curr)
                
                # End definition
                if d < num_days - 1:
                    nxt = get_is_producing_var(grade, line, d + 1)
                    if curr and nxt:
                        model.AddBoolAnd([curr, nxt.Not()]).OnlyEnforceIf(is_end)
                        model.AddBoolOr([curr.Not(), nxt]).OnlyEnforceIf(is_end.Not())
                else:
                    if curr:
                        model.Add(curr == 1).OnlyEnforceIf(is_end)
                        model.Add(is_end == 1).OnlyEnforceIf(curr)
            
            # Min run enforcement
            for d in range(num_days):
                is_start = is_start_vars[(grade, line, d)]
                for k in range(min_run):
                    if d + k < num_days:
                        if line in shutdown_periods and (d + k) in shutdown_periods[line]:
                            continue
                        future = get_is_producing_var(grade, line, d + k)
                        if future:
                            model.Add(future == 1).OnlyEnforceIf(is_start)
            # Max run enforcement
            for d in range(num_days - max_run):
                consecutive = []
                for k in range(max_run + 1):
                    if d + k < num_days:
                        if line in shutdown_periods and (d + k) in shutdown_periods[line]:
                            break
                        var = get_is_producing_var(grade, line, d + k)
                        if var:
                            consecutive.append(var)
                if len(consecutive) == max_run + 1:
                    model.Add(sum(consecutive) <= max_run)
    
    # ---------------------------
    # Transition constraints (Yes/No)
    # ---------------------------
    transition_vars = []
    for line in lines:
        rules = transition_rules.get(line)
        if rules is None:
            continue
        for d in range(num_days - 1):
            for prev_grade in grades:
                for next_grade in grades:
                    if prev_grade == next_grade:
                        continue
                    allowed = rules.get(prev_grade, {}).get(next_grade, "Yes")
                    if allowed == "No":
                        prev_var = get_is_producing_var(prev_grade, line, d)
                        next_var = get_is_producing_var(next_grade, line, d + 1)
                        if prev_var is not None and next_var is not None:
                            model.AddBoolOr([prev_var.Not(), next_var.Not()])
            
            # Objective: penalize valid transitions
            transition_indicator = model.NewBoolVar(f'transition_{line}_{d}')
            same_grade_continuity = []
            for grade in grades:
                if not is_allowed_combination(grade, line):
                    continue
                prev_var = get_is_producing_var(grade, line, d)
                next_var = get_is_producing_var(grade, line, d + 1)
                if prev_var and next_var:
                    cont = model.NewBoolVar(f'cont_{line}_{d}_{grade}')
                    model.AddBoolAnd([prev_var, next_var]).OnlyEnforceIf(cont)
                    model.AddBoolOr([prev_var.Not(), next_var.Not()]).OnlyEnforceIf(cont.Not())
                    same_grade_continuity.append(cont)
            if same_grade_continuity:
                has_cont = model.NewBoolVar(f'has_cont_{line}_{d}')
                model.AddMaxEquality(has_cont, same_grade_continuity)
                prod_today = model.NewBoolVar(f'prod_today_{line}_{d}')
                prod_tomorrow = model.NewBoolVar(f'prod_tomorrow_{line}_{d}')
                model.AddMaxEquality(prod_today, [get_is_producing_var(g, line, d) for g in grades if get_is_producing_var(g, line, d)])
                model.AddMaxEquality(prod_tomorrow, [get_is_producing_var(g, line, d+1) for g in grades if get_is_producing_var(g, line, d+1)])
                model.AddBoolAnd([prod_today, prod_tomorrow, has_cont.Not()]).OnlyEnforceIf(transition_indicator)
                model.AddBoolOr([prod_today.Not(), prod_tomorrow.Not(), has_cont]).OnlyEnforceIf(transition_indicator.Not())
                transition_vars.append(transition_indicator)
    
    for trans_var in transition_vars:
        objective += transition_penalty * trans_var
    
    # ---------------------------
    # Rerun constraints
    # ---------------------------
    for grade in grades:
        for line in allowed_lines[grade]:
            key = (grade, line)
            if not rerun_allowed.get(key, True):
                starts = [is_start_vars[(grade, line, d)] for d in range(num_days) if (grade, line, d) in is_start_vars]
                if starts:
                    model.Add(sum(starts) <= 1)
    
    # ---------------------------
    # Stockout penalties
    # ---------------------------
    for grade in grades:
        for d in range(num_days):
            objective += stockout_penalty * stockout_vars[(grade, d)]
    
    model.Minimize(objective)
    
    # ---------------------------
    # Solve
    # ---------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60.0
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 42
    solver.parameters.log_search_progress = True
    
    solution_callback = SolutionCallback(production, inventory_vars, stockout_vars, is_producing, grades, lines, dates, num_days)
    
    start_time = time.time()
    status = solver.Solve(model, solution_callback)
    runtime = time.time() - start_time
    
    result = {
        'status': solver.StatusName(status),
        'solver': solver,
        'solutions': solution_callback.solutions,
        'best': solution_callback.solutions[-1] if solution_callback.solutions else None,
        'runtime': runtime,
    }
    
    return result

# ---------------------------
# Solution callback
# ---------------------------
class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Extracts solution similar to original EXACT logic"""
    
    def __init__(self, production, inventory, stockout, is_producing, grades, lines, dates, num_days):
        super().__init__()
        self.production = production
        self.inventory = inventory
        self.stockout = stockout
        self.is_producing = is_producing
        self.grades = grades
        self.lines = lines
        self.dates = dates
        self.num_days = num_days
        self.solutions = []
        self.solution_times = []
        self.start_time = time.time()
        self.formatted_dates = [date.strftime('%d-%b-%y') for date in dates]

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
        for grade in self.grades:
            solution['production'][grade] = {}
            for line in self.lines:
                for d in range(self.num_days):
                    key = (grade, line, d)
                    if key in self.production:
                        val = self.Value(self.production[key])
                        if val > 0:
                            date_key = self.formatted_dates[d]
                            solution['production'][grade].setdefault(date_key, 0)
                            solution['production'][grade][date_key] += val
        for grade in self.grades:
            solution['inventory'][grade] = {}
            for d in range(self.num_days + 1):
                key = (grade, d)
                if key in self.inventory:
                    if d < self.num_days:
                        solution['inventory'][grade][self.formatted_dates[d] if d > 0 else 'initial'] = self.Value(self.inventory[key])
                    else:
                        solution['inventory'][grade]['final'] = self.Value(self.inventory[key])
        for grade in self.grades:
            solution['stockout'][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.stockout:
                    val = self.Value(self.stockout[key])
                    if val > 0:
                        solution['stockout'][grade][self.formatted_dates[d]] = val
        for line in self.lines:
            solution['is_producing'][line] = {}
            for d in range(self.num_days):
                date_key = self.formatted_dates[d]
                solution['is_producing'][line][date_key] = None
                for grade in self.grades:
                    key = (grade, line, d)
                    var = self.is_producing.get(key)
                    if var and self.Value(var) == 1:
                        solution['is_producing'][line][date_key] = grade
        self.solutions.append(solution)
