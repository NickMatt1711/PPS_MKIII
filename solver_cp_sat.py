# solver_cp_sat.py
"""
CP-SAT solver implementing final rules with enforcement of force_start_date.
Enhanced with min inventory penalties and rerun constraints.
"""

from ortools.sat.python import cp_model
import time

def solve(instance, parameters):
    print("Solver starting...")
    
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = len(dates)
    
    print(f"Grades: {grades}")
    print(f"Lines: {lines}")
    print(f"Number of days: {num_days}")

    model = cp_model.CpModel()

    # Variables: assign (line, d, g) booleans
    assign = {}
    for line in lines:
        for d in range(num_days):
            for g in grades:
                if line in instance['allowed_lines'].get(g, []):
                    assign[(line, d, g)] = model.NewBoolVar(f"assign_{line}_{d}_{g}")

    print(f"Created {len(assign)} assignment variables")

    # production per (line,d,g)
    production = {}
    for (line, d, g) in assign:
        cap = int(instance['capacities'].get(line, 0))
        production[(line, d, g)] = model.NewIntVar(0, cap, f"prod_{line}_{d}_{g}")

    bigM = 10**9
    
    # Min inventory violation variables
    min_inv_violation = {}
    for g in grades:
        min_inv = instance.get('min_inventory', {}).get(g, 0)
        if min_inv > 0:
            for d in range(num_days + 1):
                min_inv_violation[(g, d)] = model.NewIntVar(0, bigM, f"min_inv_viol_{g}_{d}")

    # Min closing inventory violation variables
    min_closing_violation = {}
    for g in grades:
        min_closing = instance.get('min_closing_inventory', {}).get(g, 0)
        if min_closing > 0:
            min_closing_violation[g] = model.NewIntVar(0, bigM, f"min_closing_viol_{g}")

    # prod_sum per grade/day
    prod_sum = {}
    for g in grades:
        for d in range(num_days):
            prod_sum[(g, d)] = model.NewIntVar(0, bigM, f"prod_sum_{g}_{d}")

    # inventory per grade (0..num_days)
    inventory = {}
    for g in grades:
        for d in range(num_days + 1):
            inventory[(g, d)] = model.NewIntVar(0, bigM, f"inv_{g}_{d}")

    # unmet demand
    unmet = {}
    for g in grades:
        for d in range(num_days):
            unmet[(g, d)] = model.NewIntVar(0, bigM, f"unmet_{g}_{d}")

    # prod_day and continuity/change detection
    prod_day = {}
    for line in lines:
        for d in range(num_days):
            prod_day[(line, d)] = model.NewBoolVar(f"prod_day_{line}_{d}")

    changed = {}
    for line in lines:
        for d in range(num_days - 1):
            changed[(line, d)] = model.NewBoolVar(f"changed_{line}_{d}")

    # is_start flags for campaigns
    is_start = {}
    for g in grades:
        for line in lines:
            for d in range(num_days):
                if (line, d, g) in assign:
                    is_start[(g, line, d)] = model.NewBoolVar(f"is_start_{g}_{line}_{d}")

    # Constraints ---------------------------------------------------------

    # Exactly one grade per line/day
    for line in lines:
        for d in range(num_days):
            vars_here = [assign[(line, d, g)] for g in grades if (line, d, g) in assign]
            if vars_here:
                model.Add(sum(vars_here) == 1)

    # Link production to assign and capacity
    for (line, d, g), prod_var in production.items():
        cap = int(instance['capacities'].get(line, 0))
        model.Add(prod_var <= cap * assign[(line, d, g)])

    # prod_day ties to assign
    for line in lines:
        for d in range(num_days):
            assigns_here = [assign[(line, d, g)] for g in grades if (line, d, g) in assign]
            if assigns_here:
                model.AddMaxEquality(prod_day[(line, d)], assigns_here)
            else:
                model.Add(prod_day[(line, d)] == 0)

    # prod_sum per grade/day = sum across lines
    for g in grades:
        for d in range(num_days):
            parts = [production[(line, d, g)] for line in lines if (line, d, g) in production]
            if parts:
                model.Add(prod_sum[(g, d)] == sum(parts))
            else:
                model.Add(prod_sum[(g, d)] == 0)

    # inventory recursion + unmet
    for g in grades:
        init = int(instance.get('initial_inventory', {}).get(g, 0))
        model.Add(inventory[(g, 0)] == init)
        for d in range(num_days):
            demand_val = int(instance['demand'].get((g, d), 0))
            model.Add(unmet[(g, d)] >= demand_val - (inventory[(g, d)] + prod_sum[(g, d)]))
            model.Add(unmet[(g, d)] >= 0)
            model.Add(inventory[(g, d + 1)] == inventory[(g, d)] + prod_sum[(g, d)] - demand_val + unmet[(g, d)])
            max_inv = int(instance.get('max_inventory', {}).get(g, 10**9))
            model.Add(inventory[(g, d + 1)] <= max_inv)

    # Min inventory violation constraints
    for g in grades:
        min_inv = instance.get('min_inventory', {}).get(g, 0)
        if min_inv > 0 and (g, 0) in min_inv_violation:
            for d in range(num_days + 1):
                model.Add(min_inv_violation[(g, d)] >= min_inv - inventory[(g, d)])
                model.Add(min_inv_violation[(g, d)] >= 0)

    # Min closing inventory constraints
    for g in grades:
        min_closing = int(instance.get('min_closing_inventory', {}).get(g, 0))
        if min_closing > 0 and g in min_closing_violation:
            model.Add(min_closing_violation[g] >= min_closing - inventory[(g, num_days)])
            model.Add(min_closing_violation[g] >= 0)
        else:
            model.Add(inventory[(g, num_days)] >= min_closing)

    # shutdown days: no assign allowed
    for line in lines:
        shutdown_indices = instance.get('shutdown_day_indices', {}).get(line, set())
        for d in shutdown_indices:
            for g in grades:
                if (line, d, g) in assign:
                    model.Add(assign[(line, d, g)] == 0)

    # Transition rules
    for line in lines:
        rules = instance.get('transition_rules', {}).get(line, None)
        if rules:
            for d in range(1, num_days):
                for prev_g in grades:
                    for curr_g in grades:
                        if prev_g == curr_g:
                            continue
                        prev_key = (line, d - 1, prev_g)
                        curr_key = (line, d, curr_g)
                        if prev_key in assign and curr_key in assign:
                            allowed_next = rules.get(prev_g, [])
                            if curr_g not in allowed_next:
                                model.Add(assign[prev_key] + assign[curr_key] <= 1)

    # SIMPLIFIED: Change detection
    for line in lines:
        for d in range(num_days - 1):
            # Changed if different grades on consecutive days
            for g1 in grades:
                for g2 in grades:
                    if g1 != g2:
                        key1 = (line, d, g1)
                        key2 = (line, d + 1, g2)
                        if key1 in assign and key2 in assign:
                            # If both assignments are true, then changed is true
                            model.AddBoolOr([
                                assign[key1].Not(),
                                assign[key2].Not(),
                                changed[(line, d)]
                            ])
            # If changed is true, then there must be different grades
            different_grade_exists = []
            for g1 in grades:
                for g2 in grades:
                    if g1 != g2:
                        key1 = (line, d, g1)
                        key2 = (line, d + 1, g2)
                        if key1 in assign and key2 in assign:
                            both_true = model.NewBoolVar(f"both_{line}_{d}_{g1}_{g2}")
                            model.AddBoolAnd([assign[key1], assign[key2]]).OnlyEnforceIf(both_true)
                            model.AddBoolOr([assign[key1].Not(), assign[key2].Not()]).OnlyEnforceIf(both_true.Not())
                            different_grade_exists.append(both_true)
            
            if different_grade_exists:
                model.AddMaxEquality(changed[(line, d)], different_grade_exists)

    # SIMPLIFIED: is_start detection
    for g in grades:
        for line in lines:
            for d in range(num_days):
                key = (g, line, d)
                if key in is_start:
                    # is_start implies assign
                    model.Add(is_start[key] <= assign[(line, d, g)])
                    
                    if d == 0:
                        # First day is always start if producing
                        model.Add(is_start[key] >= assign[(line, d, g)])
                    else:
                        # For later days, is_start if producing today but not yesterday
                        prev_key = (line, d - 1, g)
                        if prev_key in assign:
                            # is_start >= assign[today] AND NOT assign[yesterday]
                            model.Add(is_start[key] >= assign[(line, d, g)] - assign[prev_key])
                        else:
                            # If previous day not allowed, then today is start if producing
                            model.Add(is_start[key] >= assign[(line, d, g)])

    # SIMPLIFIED: Run length constraints
    for g in grades:
        for line in lines:
            min_run = int(instance.get('min_run_days', {}).get((g, line), 1))
            max_run = int(instance.get('max_run_days', {}).get((g, line), num_days))
            
            # For each possible start day
            for start_d in range(num_days):
                start_key = (g, line, start_d)
                if start_key in is_start:
                    # If this is a start, enforce min run days
                    for offset in range(min_run):
                        day_idx = start_d + offset
                        if day_idx < num_days:
                            day_key = (line, day_idx, g)
                            if day_key in assign:
                                model.Add(assign[day_key] == 1).OnlyEnforceIf(is_start[start_key])
                    
                    # Enforce max run days - after max_run, must not be same grade
                    day_after_max = start_d + max_run
                    if day_after_max < num_days:
                        # Cannot have the same grade immediately after max run
                        day_after_key = (line, day_after_max, g)
                        if day_after_key in assign:
                            model.Add(assign[day_after_key] == 0).OnlyEnforceIf(is_start[start_key])

    # Rerun constraints
    for g in grades:
        for line in lines:
            starts = [is_start[(g, line, d)] for d in range(num_days) if (g, line, d) in is_start]
            if starts:
                allowed = instance.get('rerun_allowed', {}).get(g, True)
                if not allowed:
                    model.Add(sum(starts) <= 1)

    # Force start date constraints
    force_start_date = instance.get('force_start_date', {})
    for g, force_date in force_start_date.items():
        if force_date is None:
            continue
        
        # Find eligible start days
        eligible_starts = []
        for line in lines:
            for d in range(num_days):
                if dates[d] >= force_date:
                    key = (g, line, d)
                    if key in is_start:
                        eligible_starts.append(is_start[key])
        
        if eligible_starts:
            model.Add(sum(eligible_starts) >= 1)
        else:
            # If no eligible starts, create infeasibility
            model.Add(0 == 1)

    # Objective
    stockout_penalty = int(parameters.get('stockout_penalty', 10))
    transition_penalty = int(parameters.get('transition_penalty', 10))
    min_inv_penalty_val = int(parameters.get('min_inventory_penalty', 5))
    min_closing_penalty_val = int(parameters.get('min_closing_penalty', 8))
    
    obj_terms = []
    
    # Stockout penalties
    for g in grades:
        for d in range(num_days):
            obj_terms.append(stockout_penalty * unmet[(g, d)])
    
    # Transition penalties
    for line in lines:
        for d in range(num_days - 1):
            obj_terms.append(transition_penalty * changed[(line, d)])
    
    # Min inventory penalties
    for (g, d), var in min_inv_violation.items():
        penalty = instance.get('min_inv_penalty', {}).get(g, min_inv_penalty_val)
        obj_terms.append(penalty * var)
    
    # Min closing inventory penalties
    for g, var in min_closing_violation.items():
        penalty = instance.get('min_closing_penalty', {}).get(g, min_closing_penalty_val)
        obj_terms.append(penalty * var)
    
    model.Minimize(sum(obj_terms))

    # Solve
    solver = cp_model.CpSolver()
    time_limit = parameters.get('time_limit_min', 10)
    solver.parameters.max_time_in_seconds = time_limit * 60.0
    solver.parameters.num_search_workers = parameters.get('num_search_workers', 8)
    solver.parameters.random_seed = 42

    class Collector(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.solutions = []
            self.start_time = time.time()

        def on_solution_callback(self):
            sol = {
                'time': time.time() - self.start_time,
                'objective': self.ObjectiveValue(),
                'assign': {},
                'production': {},
                'inventory': {},
                'unmet': {},
                'min_inv_violations': {},
                'min_closing_violations': {}
            }
            for (line, d, g), var in assign.items():
                if self.Value(var) == 1:
                    sol['assign'][(line, d)] = g
            for (line, d, g), var in production.items():
                val = self.Value(var)
                if val > 0:
                    sol['production'].setdefault((line, d), {})[g] = val
            for (g, d), var in inventory.items():
                sol['inventory'][(g, d)] = self.Value(var)
            for (g, d), var in unmet.items():
                val = self.Value(var)
                if val > 0:
                    sol['unmet'][(g, d)] = val
            for (g, d), var in min_inv_violation.items():
                val = self.Value(var)
                if val > 0:
                    sol['min_inv_violations'][(g, d)] = val
            for g, var in min_closing_violation.items():
                val = self.Value(var)
                if val > 0:
                    sol['min_closing_violations'][g] = val
                    
            self.solutions.append(sol)

    collector = Collector()
    print("Starting solver...")
    status = solver.SolveWithSolutionCallback(model, collector)
    status_name = solver.StatusName(status)
    print(f"Solver finished with status: {status_name}")

    result = {
        'status': status_name,
        'solver': solver,
        'solutions': collector.solutions,
        'best': collector.solutions[-1] if collector.solutions else None
    }
    return result
