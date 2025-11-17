# solver_cp_sat.py
"""
CP-SAT solver with simplified constraints and better feasibility handling.
"""

from ortools.sat.python import cp_model
import time

def solve(instance, parameters):
    print("Solver starting with simplified constraints...")
    
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = len(dates)
    
    print(f"Grades: {grades}")
    print(f"Lines: {lines}")
    print(f"Number of days: {num_days}")

    model = cp_model.CpModel()

    # 1. BASIC VARIABLES - Start simple
    assign = {}
    for line in lines:
        for d in range(num_days):
            for g in grades:
                if line in instance['allowed_lines'].get(g, []):
                    assign[(line, d, g)] = model.NewBoolVar(f"assign_{line}_{d}_{g}")

    print(f"Created {len(assign)} assignment variables")

    # Production variables
    production = {}
    for (line, d, g) in assign:
        cap = int(instance['capacities'].get(line, 0))
        production[(line, d, g)] = model.NewIntVar(0, cap, f"prod_{line}_{d}_{g}")

    # Inventory variables
    inventory = {}
    for g in grades:
        for d in range(num_days + 1):
            inventory[(g, d)] = model.NewIntVar(0, 100000, f"inv_{g}_{d}")

    # Unmet demand variables
    unmet = {}
    for g in grades:
        for d in range(num_days):
            unmet[(g, d)] = model.NewIntVar(0, 100000, f"unmet_{g}_{d}")

    # 2. CORE CONSTRAINTS - Start with minimal feasible set

    # Constraint 1: Exactly one grade per line per day
    for line in lines:
        for d in range(num_days):
            vars_here = [assign[(line, d, g)] for g in grades if (line, d, g) in assign]
            if vars_here:
                model.Add(sum(vars_here) == 1)
                print(f"Line {line} day {d}: {len(vars_here)} grade options")

    # Constraint 2: Production linked to assignment
    for (line, d, g), prod_var in production.items():
        cap = int(instance['capacities'].get(line, 0))
        model.Add(prod_var <= cap * assign[(line, d, g)])

    # Constraint 3: Inventory balance
    for g in grades:
        init_inv = int(instance.get('initial_inventory', {}).get(g, 0))
        model.Add(inventory[(g, 0)] == init_inv)
        
        for d in range(num_days):
            # Calculate total production for this grade-day
            prod_vars = [production[(line, d, g)] for line in lines if (line, d, g) in production]
            if prod_vars:
                total_prod = model.NewIntVar(0, 100000, f"total_prod_{g}_{d}")
                model.Add(total_prod == sum(prod_vars))
            else:
                total_prod = 0
            
            demand_val = int(instance['demand'].get((g, d), 0))
            
            # Inventory balance: inv[t+1] = inv[t] + production - demand + unmet
            model.Add(
                inventory[(g, d + 1)] == 
                inventory[(g, d)] + total_prod - demand_val + unmet[(g, d)]
            )
            
            # Unmet demand must cover any shortfall
            model.Add(unmet[(g, d)] >= demand_val - (inventory[(g, d)] + total_prod))
            model.Add(unmet[(g, d)] >= 0)
            
            # Max inventory constraint
            max_inv = int(instance.get('max_inventory', {}).get(g, 100000))
            model.Add(inventory[(g, d + 1)] <= max_inv)

    # Constraint 4: Shutdown periods
    shutdown_constraints = 0
    for line in lines:
        shutdown_indices = instance.get('shutdown_day_indices', {}).get(line, set())
        for d in shutdown_indices:
            for g in grades:
                if (line, d, g) in assign:
                    model.Add(assign[(line, d, g)] == 0)
                    shutdown_constraints += 1
    print(f"Added {shutdown_constraints} shutdown constraints")

    # 3. GRADUALLY ADD COMPLEX CONSTRAINTS with feasibility checks

    # Constraint 5: Min closing inventory (as soft constraint)
    min_closing_violation = {}
    for g in grades:
        min_closing = int(instance.get('min_closing_inventory', {}).get(g, 0))
        if min_closing > 0:
            min_closing_violation[g] = model.NewIntVar(0, 100000, f"min_closing_viol_{g}")
            model.Add(min_closing_violation[g] >= min_closing - inventory[(g, num_days)])
            model.Add(min_closing_violation[g] >= 0)
        else:
            # Hard constraint if no penalty system
            model.Add(inventory[(g, num_days)] >= min_closing)

    # Constraint 6: Min inventory violations (soft constraints)
    min_inv_violation = {}
    for g in grades:
        min_inv = instance.get('min_inventory', {}).get(g, 0)
        if min_inv > 0:
            for d in range(num_days + 1):
                min_inv_violation[(g, d)] = model.NewIntVar(0, 100000, f"min_inv_viol_{g}_{d}")
                model.Add(min_inv_violation[(g, d)] >= min_inv - inventory[(g, d)])
                model.Add(min_inv_violation[(g, d)] >= 0)

    # Constraint 7: Basic transition rules (only critical ones)
    transition_constraints = 0
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
                                # This transition is forbidden
                                model.Add(assign[prev_key] + assign[curr_key] <= 1)
                                transition_constraints += 1
    print(f"Added {transition_constraints} transition constraints")

    # Constraint 8: SIMPLIFIED run length constraints
    run_constraints = 0
    for g in grades:
        for line in lines:
            min_run = int(instance.get('min_run_days', {}).get((g, line), 1))
            
            # Simple min run constraint: if you start, you must run for at least min_run days
            for start_d in range(num_days - min_run + 1):
                # Check if this could be a start day
                start_possible = True
                for offset in range(min_run):
                    day_idx = start_d + offset
                    if day_idx >= num_days or (line, day_idx, g) not in assign:
                        start_possible = False
                        break
                
                if start_possible:
                    # If producing on start day but not the day before, must continue for min_run days
                    if start_d > 0:
                        prev_day_key = (line, start_d - 1, g)
                        if prev_day_key in assign:
                            # If today is g but yesterday wasn't, then this is a start
                            start_condition = model.NewBoolVar(f"start_cond_{g}_{line}_{start_d}")
                            model.Add(assign[(line, start_d, g)] == 1).OnlyEnforceIf(start_condition)
                            model.Add(assign[prev_day_key] == 0).OnlyEnforceIf(start_condition)
                            
                            # If it's a start, enforce min run
                            for offset in range(min_run):
                                day_idx = start_d + offset
                                day_key = (line, day_idx, g)
                                if day_key in assign:
                                    model.Add(assign[day_key] == 1).OnlyEnforceIf(start_condition)
                                    run_constraints += 1
                    else:
                        # Day 0: if producing, must continue for min_run days
                        start_condition = model.NewBoolVar(f"start_cond_{g}_{line}_0")
                        model.Add(assign[(line, 0, g)] == 1).OnlyEnforceIf(start_condition)
                        
                        for offset in range(min_run):
                            day_idx = offset
                            day_key = (line, day_idx, g)
                            if day_key in assign:
                                model.Add(assign[day_key] == 1).OnlyEnforceIf(start_condition)
                                run_constraints += 1
    print(f"Added {run_constraints} run length constraints")

    # Constraint 9: SIMPLIFIED rerun constraints
    rerun_constraints = 0
    for g in grades:
        allowed = instance.get('rerun_allowed', {}).get(g, True)
        if not allowed:
            # For non-rerun grades, use a simple approach: count distinct campaigns
            for line in lines:
                # Count how many times we switch to this grade
                switches = []
                for d in range(1, num_days):
                    prev_day_producing = model.NewBoolVar(f"prev_prod_{g}_{line}_{d}")
                    today_producing = model.NewBoolVar(f"today_prod_{g}_{line}_{d}")
                    
                    prev_key = (line, d-1, g)
                    today_key = (line, d, g)
                    
                    if prev_key in assign:
                        model.Add(assign[prev_key] == 1).OnlyEnforceIf(prev_day_producing)
                        model.Add(assign[prev_key] == 0).OnlyEnforceIf(prev_day_producing.Not())
                    
                    if today_key in assign:
                        model.Add(assign[today_key] == 1).OnlyEnforceIf(today_producing)
                        model.Add(assign[today_key] == 0).OnlyEnforceIf(today_producing.Not())
                        
                        # Switch: not producing yesterday but producing today
                        switch = model.NewBoolVar(f"switch_{g}_{line}_{d}")
                        model.AddBoolAnd([prev_day_producing.Not(), today_producing]).OnlyEnforceIf(switch)
                        model.AddBoolOr([prev_day_producing, today_producing.Not()]).OnlyEnforceIf(switch.Not())
                        switches.append(switch)
                
                # For non-rerun grades, allow at most 1 switch (meaning 1 campaign)
                if switches:
                    model.Add(sum(switches) <= 1)
                    rerun_constraints += len(switches)
    
    print(f"Added {rerun_constraints} rerun constraints")

    # 4. OBJECTIVE FUNCTION with penalties

    stockout_penalty = int(parameters.get('stockout_penalty', 10))
    transition_penalty = int(parameters.get('transition_penalty', 5))  # Reduced for feasibility
    min_inv_penalty_val = int(parameters.get('min_inventory_penalty', 3))  # Reduced
    min_closing_penalty_val = int(parameters.get('min_closing_penalty', 5))  # Reduced

    obj_terms = []

    # Stockout cost
    for g in grades:
        for d in range(num_days):
            obj_terms.append(stockout_penalty * unmet[(g, d)])

    # Simplified transition cost (count grade changes)
    transition_cost_vars = []
    for line in lines:
        for d in range(num_days - 1):
            change_var = model.NewBoolVar(f"change_{line}_{d}")
            
            # Change occurs if different grades on consecutive days
            different_grades = []
            for g1 in grades:
                for g2 in grades:
                    if g1 != g2:
                        key1 = (line, d, g1)
                        key2 = (line, d + 1, g2)
                        if key1 in assign and key2 in assign:
                            both_assigned = model.NewBoolVar(f"both_{line}_{d}_{g1}_{g2}")
                            model.AddBoolAnd([assign[key1], assign[key2]]).OnlyEnforceIf(both_assigned)
                            model.AddBoolOr([assign[key1].Not(), assign[key2].Not()]).OnlyEnforceIf(both_assigned.Not())
                            different_grades.append(both_assigned)
            
            if different_grades:
                model.AddMaxEquality(change_var, different_grades)
                transition_cost_vars.append(change_var)
    
    for change_var in transition_cost_vars:
        obj_terms.append(transition_penalty * change_var)

    # Min inventory violation costs
    for (g, d), var in min_inv_violation.items():
        penalty = instance.get('min_inv_penalty', {}).get(g, min_inv_penalty_val)
        obj_terms.append(penalty * var)

    # Min closing inventory violation costs
    for g, var in min_closing_violation.items():
        penalty = instance.get('min_closing_penalty', {}).get(g, min_closing_penalty_val)
        obj_terms.append(penalty * var)

    model.Minimize(sum(obj_terms))

    # 5. SOLVE with better parameters
    solver = cp_model.CpSolver()
    
    # More lenient parameters for feasibility
    time_limit = parameters.get('time_limit_min', 10)
    solver.parameters.max_time_in_seconds = time_limit * 60.0
    solver.parameters.num_search_workers = parameters.get('num_search_workers', 4)  # Reduced
    solver.parameters.random_seed = 42
    solver.parameters.log_search_progress = True
    
    # Enable more aggressive feasibility search
    solver.parameters.search_branching = cp_model.FIXED_SEARCH
    solver.parameters.linearization_level = 1
    solver.parameters.cp_model_presolve = True

    print(f"Starting solver with {len(obj_terms)} objective terms...")
    print(f"Time limit: {time_limit} minutes")

    class SolutionCollector(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.solutions = []
            self.solution_count = 0
            self.start_time = time.time()

        def on_solution_callback(self):
            self.solution_count += 1
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
            
            # Collect basic solution data
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
            
            # Collect violation data if available
            if min_inv_violation:
                for (g, d), var in min_inv_violation.items():
                    val = self.Value(var)
                    if val > 0:
                        sol['min_inv_violations'][(g, d)] = val
            
            if min_closing_violation:
                for g, var in min_closing_violation.items():
                    val = self.Value(var)
                    if val > 0:
                        sol['min_closing_violations'][g] = val
            
            self.solutions.append(sol)
            print(f"Solution {self.solution_count} found with objective: {self.ObjectiveValue()}")

    collector = SolutionCollector()
    
    try:
        status = solver.SolveWithSolutionCallback(model, collector)
        status_name = solver.StatusName(status)
        print(f"Solver finished with status: {status_name}")
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            print(f"Best solution objective: {solver.ObjectiveValue()}")
            print(f"Number of solutions found: {collector.solution_count}")
        else:
            print("No feasible solution found")
            print(f"Solver status: {status_name}")
            print(f"Solver reason: {solver.ResponseStats()}")
            
    except Exception as e:
        print(f"Solver error: {e}")
        status_name = "ERROR"

    result = {
        'status': status_name,
        'solver': solver,
        'solutions': collector.solutions,
        'best': collector.solutions[-1] if collector.solutions else None
    }
    return result
