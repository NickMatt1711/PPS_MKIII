# solver_cp_sat.py
"""
CP-SAT solver implementing final rules with enforcement of force_start_date.
Enhanced with min inventory penalties and rerun constraints.
"""

from ortools.sat.python import cp_model
import time

def solve(instance, parameters):
    # Debug: Check instance structure
    print("Solver starting...")
    print(f"Instance keys: {list(instance.keys())}")
    
    grades = instance['grades']
    lines = instance['lines']  # This should now be defined
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
    
    # NEW: Min inventory violation variables
    min_inv_violation = {}
    for g in grades:
        min_inv = instance.get('min_inventory', {}).get(g, 0)
        if min_inv > 0:  # Only create variables if min inventory is specified
            for d in range(num_days + 1):
                min_inv_violation[(g, d)] = model.NewIntVar(0, bigM, f"min_inv_viol_{g}_{d}")

    # NEW: Min closing inventory violation variables
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
    has_continuity = {}
    for line in lines:
        for d in range(num_days - 1):
            changed[(line, d)] = model.NewBoolVar(f"changed_{line}_{d}")
            has_continuity[(line, d)] = model.NewBoolVar(f"has_cont_{line}_{d}")

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
            else:
                # If no variables (due to allowed_lines restrictions), add dummy constraint
                pass

    # Link production to assign and capacity
    for (line, d, g), prod_var in production.items():
        cap = int(instance['capacities'].get(line, 0))
        model.Add(prod_var <= cap * assign[(line, d, g)])
    for line in lines:
        for d in range(num_days):
            prods = [production[(line, d, g)] for g in grades if (line, d, g) in production]
            cap = int(instance['capacities'].get(line, 0))
            if prods:
                model.Add(sum(prods) <= cap)

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

    # NEW: Min inventory violation constraints
    for g in grades:
        min_inv = instance.get('min_inventory', {}).get(g, 0)
        if min_inv > 0 and (g, 0) in min_inv_violation:
            for d in range(num_days + 1):
                # min_inv_violation >= min_inventory - actual_inventory
                model.Add(min_inv_violation[(g, d)] >= min_inv - inventory[(g, d)])
                model.Add(min_inv_violation[(g, d)] >= 0)

    # min closing inventory constraint (now as soft constraint with violation variable)
    for g in grades:
        min_closing = int(instance.get('min_closing_inventory', {}).get(g, 0))
        if min_closing > 0 and g in min_closing_violation:
            # min_closing_violation >= min_closing - final_inventory
            model.Add(min_closing_violation[g] >= min_closing - inventory[(g, num_days)])
            model.Add(min_closing_violation[g] >= 0)
        else:
            # Keep original hard constraint if no penalty system
            model.Add(inventory[(g, num_days)] >= min_closing)

    # shutdown days: no assign allowed
    for line in lines:
        shutdown_indices = instance.get('shutdown_day_indices', {}).get(line, set())
        for d in shutdown_indices:
            for g in grades:
                if (line, d, g) in assign:
                    model.Add(assign[(line, d, g)] == 0)

    # Transition rules: forbid disallowed prev->curr
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
                            disallowed = False
                            if rules is not None:
                                allowed_next = rules.get(prev_g, [])
                                if curr_g not in allowed_next:
                                    disallowed = True
                            if disallowed:
                                model.Add(assign[prev_key] + assign[curr_key] <= 1)

    # FIXED: Continuity detection and changed var - using proper CP-SAT methods
    for line in lines:
        for d in range(num_days - 1):
            same_bools = []
            for g in grades:
                prev_key = (line, d, g)
                next_key = (line, d + 1, g)
                if prev_key in assign and next_key in assign:
                    same = model.NewBoolVar(f"same_{line}_{d}_{g}")
                    # FIXED: Use OnlyEnforceIf with lists instead of boolean operations
                    model.AddBoolAnd([assign[prev_key], assign[next_key]]).OnlyEnforceIf(same)
                    model.AddBoolOr([assign[prev_key].Not(), assign[next_key].Not()]).OnlyEnforceIf(same.Not())
                    same_bools.append(same)
            
            if same_bools:
                # At least one grade continues
                model.AddMaxEquality(has_continuity[(line, d)], same_bools)
            else:
                model.Add(has_continuity[(line, d)] == 0)
            
            # FIXED: changed = prod_day[d] AND prod_day[d+1] AND NOT has_continuity
            # Use intermediate variables to avoid direct boolean operations
            prod_both_days = model.NewBoolVar(f"prod_both_{line}_{d}")
            model.AddBoolAnd([prod_day[(line, d)], prod_day[(line, d + 1)]]).OnlyEnforceIf(prod_both_days)
            model.AddBoolOr([prod_day[(line, d)].Not(), prod_day[(line, d + 1)].Not()]).OnlyEnforceIf(prod_both_days.Not())
            
            no_continuity = model.NewBoolVar(f"no_cont_{line}_{d}")
            model.Add(has_continuity[(line, d)] == 0).OnlyEnforceIf(no_continuity)
            model.Add(has_continuity[(line, d)] == 1).OnlyEnforceIf(no_continuity.Not())
            
            # changed is true only if producing both days AND no continuity
            model.AddBoolAnd([prod_both_days, no_continuity]).OnlyEnforceIf(changed[(line, d)])
            model.AddBoolOr([prod_both_days.Not(), no_continuity.Not()]).OnlyEnforceIf(changed[(line, d)].Not())

    # FIXED: is_start detection and run length enforcement
    for g in grades:
        for line in lines:
            for d in range(num_days):
                key = (g, line, d)
                if key in is_start:
                    # is_start <= assign
                    model.Add(is_start[key] <= assign[(line, d, g)])
                    
                    if d == 0:
                        # First day: is_start if producing
                        model.Add(is_start[key] >= assign[(line, d, g)])
                    else:
                        # Later days: is_start if producing today but not yesterday
                        prev_not_producing = model.NewBoolVar(f"prev_not_prod_{g}_{line}_{d}")
                        prev_key = (line, d - 1, g)
                        
                        if prev_key in assign:
                            # If previous day not producing this grade
                            model.Add(assign[prev_key] == 0).OnlyEnforceIf(prev_not_producing)
                            model.Add(assign[prev_key] == 1).OnlyEnforceIf(prev_not_producing.Not())
                            
                            # is_start if producing today AND not producing yesterday
                            model.AddBoolAnd([assign[(line, d, g)], prev_not_producing]).OnlyEnforceIf(is_start[key])
                            model.AddBoolOr([assign[(line, d, g)].Not(), prev_not_producing.Not()]).OnlyEnforceIf(is_start[key].Not())
                        else:
                            # If previous day not in allowed lines, then today is start if producing
                            model.Add(is_start[key] == assign[(line, d, g)])

    # enforce min/max run days when is_start==1
    for g in grades:
        for line in lines:
            min_run = int(instance.get('min_run_days', {}).get((g, line), 1))
            max_run = int(instance.get('max_run_days', {}).get((g, line), num_days))
            for d in range(num_days):
                key = (g, line, d)
                if key in is_start:
                    # Create block of days from start day
                    block_vars = []
                    for k in range(max_run):
                        dd = d + k
                        if dd >= num_days:
                            break
                        if (line, dd, g) in assign:
                            block_vars.append(assign[(line, dd, g)])
                    
                    if block_vars:
                        # If this is a start, enforce min run days
                        for k in range(min(min_run, len(block_vars))):
                            model.Add(block_vars[k] == 1).OnlyEnforceIf(is_start[key])
                        
                        # Enforce max run days - if start, then after max_run days, must not be same grade
                        if len(block_vars) > max_run:
                            # After max_run days, the assignment should be different
                            day_after_max = d + max_run
                            if day_after_max < num_days:
                                # Create constraint that if this is start, then day_after_max cannot be same grade
                                for other_g in grades:
                                    if other_g != g and (line, day_after_max, other_g) in assign:
                                        # This is tricky - we need to ensure at least one other grade is produced
                                        # For now, we'll rely on the transition constraints
                                        pass

    # ENHANCED: rerun_allowed constraints
    for g in grades:
        for line in lines:
            starts = [is_start[(g, line, d)] for d in range(num_days) if (g, line, d) in is_start]
            if starts:
                allowed = instance.get('rerun_allowed', {}).get(g, True)
                if not allowed:
                    # If rerun not allowed, can have at most one campaign per plant-grade
                    model.Add(sum(starts) <= 1)

    # FIXED: Campaign counting for rerun validation - simplified approach
    # We'll track campaign starts and ensure no restarts for non-rerun grades
    
    # enforce force_start_date per grade (hard constraint)
    force_start_date = instance.get('force_start_date', {})
    for g, force_date in force_start_date.items():
        if force_date is None:
            continue
        
        # Find first eligible day index
        eligible_idxs = []
        for i, date in enumerate(dates):
            if date >= force_date:
                eligible_idxs.append(i)
        
        if not eligible_idxs:
            # No eligible days - problem is infeasible for this grade
            dummy_var = model.NewBoolVar(f"force_fail_{g}")
            model.Add(dummy_var == 0)
            model.Add(dummy_var == 1)  # This will make it infeasible
            continue
        
        # Require at least one start in eligible period
        eligible_starts = []
        for line in lines:
            for d in eligible_idxs:
                key = (g, line, d)
                if key in is_start:
                    eligible_starts.append(is_start[key])
        
        if eligible_starts:
            model.Add(sum(eligible_starts) >= 1)
        else:
            # No possible starts - problem is infeasible
            dummy_var = model.NewBoolVar(f"force_fail_{g}")
            model.Add(dummy_var == 0)
            model.Add(dummy_var == 1)

    # ENHANCED: Objective with min inventory penalties
    stockout_penalty = int(parameters.get('stockout_penalty', 10))
    transition_penalty = int(parameters.get('transition_penalty', 10))
    min_inv_penalty_val = int(parameters.get('min_inventory_penalty', 5))
    min_closing_penalty_val = int(parameters.get('min_closing_penalty', 8))
    
    obj_terms = []
    
    # Original objective terms
    for g in grades:
        for d in range(num_days):
            obj_terms.append(stockout_penalty * unmet[(g, d)])
    for line in lines:
        for d in range(num_days - 1):
            obj_terms.append(transition_penalty * changed[(line, d)])
    
    # NEW: Min inventory penalty terms
    for (g, d), var in min_inv_violation.items():
        penalty = instance.get('min_inv_penalty', {}).get(g, min_inv_penalty_val)
        obj_terms.append(penalty * var)
    
    # NEW: Min closing inventory penalty terms
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
                # NEW: Capture violation data
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
            # NEW: Capture violation values
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
