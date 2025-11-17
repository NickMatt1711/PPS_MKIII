# solver_cp_sat.py
"""
CP-SAT solver implementing final rules:
- One grade per line per day
- Transition penalty when grade changes (only if allowed by transition matrix)
- Unmet demand explicit variable and penalized
- Min/Max run days enforced via start flags
- Rerun flag (from inventory) constrains multiple starts
- Inventory recursion, capacity, shutdowns
"""

from ortools.sat.python import cp_model
import time

def solve(instance, parameters):
    """
    instance: dict with keys:
      - grades: list[str]
      - lines: list[str]
      - dates: list[date]
      - capacities: dict line->int
      - demand: dict (grade, day_index) -> int
      - initial_inventory: dict grade->int
      - max_inventory: dict grade->int
      - min_closing_inventory: dict grade->int
      - min_run_days: dict (grade,line)->int
      - max_run_days: dict (grade,line)->int
      - allowed_lines: dict grade->list[line]
      - rerun_allowed: dict (grade,line)->bool
      - transition_rules: dict line -> dict(prev_grade -> list[allowed_next])
      - shutdown_day_indices: dict line -> set(day_indices)
    parameters:
      - time_limit_min, stockout_penalty, transition_penalty, num_search_workers
    Returns dict with solver status, best solution mapping, and meta.
    """
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = len(dates)

    model = cp_model.CpModel()

    # Variables
    assign = {}   # (line, d, g) -> Bool
    for line in lines:
        for d in range(num_days):
            for g in grades:
                if line in instance['allowed_lines'].get(g, []):
                    assign[(line, d, g)] = model.NewBoolVar(f"assign_{line}_{d}_{g}")

    # production amounts per (line,d,g)
    production = {}
    for (line, d, g) in assign:
        cap = int(instance['capacities'].get(line, 0))
        production[(line, d, g)] = model.NewIntVar(0, cap, f"prod_{line}_{d}_{g}")

    # prod_sum per grade/day
    prod_sum = {}
    bigM = 10**9
    for g in grades:
        for d in range(num_days):
            prod_sum[(g, d)] = model.NewIntVar(0, bigM, f"prod_sum_{g}_{d}")

    # inventory per grade per day (0..num_days)
    inventory = {}
    for g in grades:
        for d in range(num_days + 1):
            inventory[(g, d)] = model.NewIntVar(0, bigM, f"inv_{g}_{d}")

    # unmet demand
    unmet = {}
    for g in grades:
        for d in range(num_days):
            unmet[(g, d)] = model.NewIntVar(0, bigM, f"unmet_{g}_{d}")

    # prod_day (line,d) boolean indicates any production on that line/day
    prod_day = {}
    for line in lines:
        for d in range(num_days):
            prod_day[(line, d)] = model.NewBoolVar(f"prod_day_{line}_{d}")

    # changed (line,d) boolean if transition occurs between d and d+1 on that line
    changed = {}
    has_continuity = {}
    for line in lines:
        for d in range(num_days - 1):
            changed[(line, d)] = model.NewBoolVar(f"changed_{line}_{d}")
            has_continuity[(line, d)] = model.NewBoolVar(f"has_cont_{line}_{d}")

    # is_start to detect campaign start
    is_start = {}
    for g in grades:
        for line in lines:
            for d in range(num_days):
                if (line, d, g) in assign:
                    is_start[(g, line, d)] = model.NewBoolVar(f"is_start_{g}_{line}_{d}")

    # Constraints

    # Exactly one grade per line/day
    for line in lines:
        for d in range(num_days):
            vars_here = [assign[(line, d, g)] for g in grades if (line, d, g) in assign]
            if vars_here:
                model.Add(sum(vars_here) == 1)

    # Link production to assign and line capacity
    for (line, d, g), prod_var in production.items():
        cap = int(instance['capacities'].get(line, 0))
        model.Add(prod_var <= cap * assign[(line, d, g)])
    for line in lines:
        for d in range(num_days):
            prods = [production[(line, d, g)] for g in grades if (line, d, g) in production]
            cap = int(instance['capacities'].get(line, 0))
            if prods:
                model.Add(sum(prods) <= cap)
            else:
                # if there are no production variables (unlikely) skip
                pass

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

    # inventory recursion
    for g in grades:
        init = int(instance.get('initial_inventory', {}).get(g, 0))
        model.Add(inventory[(g, 0)] == init)
        for d in range(num_days):
            demand_val = int(instance['demand'].get((g, d), 0))
            # unmet >= demand - (inventory + production)
            model.Add(unmet[(g, d)] >= demand_val - (inventory[(g, d)] + prod_sum[(g, d)]))
            model.Add(unmet[(g, d)] >= 0)
            # next inventory = inv + prod - demand + unmet  (equivalent to inv + prod - (demand - unmet))
            model.Add(inventory[(g, d + 1)] == inventory[(g, d)] + prod_sum[(g, d)] - demand_val + unmet[(g, d)])
            # cap on inventory if provided
            max_inv = int(instance.get('max_inventory', {}).get(g, 10**9))
            model.Add(inventory[(g, d + 1)] <= max_inv)

    # min closing inventory
    for g in grades:
        min_closing = int(instance.get('min_closing_inventory', {}).get(g, 0))
        model.Add(inventory[(g, num_days)] >= min_closing)

    # Shutdown days: no assign allowed for that line at those indices
    for line in lines:
        shutdown_indices = instance.get('shutdown_day_indices', {}).get(line, set())
        for d in shutdown_indices:
            for g in grades:
                if (line, d, g) in assign:
                    model.Add(assign[(line, d, g)] == 0)

    # Transition rules: forbid disallowed transitions prev->curr
    for line in lines:
        rules = instance.get('transition_rules', {}).get(line, None)
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
                            allowed_next = rules.get(prev_g, None)
                            if allowed_next is not None:
                                if curr_g not in allowed_next:
                                    disallowed = True
                        if disallowed:
                            model.Add(assign[prev_key] + assign[curr_key] <= 1)

    # Continuity detection and changed var
    for line in lines:
        for d in range(num_days - 1):
            same_bools = []
            for g in grades:
                prev_key = (line, d, g)
                next_key = (line, d + 1, g)
                if prev_key in assign and next_key in assign:
                    same = model.NewBoolVar(f"same_{line}_{d}_{g}")
                    model.AddBoolAnd([assign[prev_key], assign[next_key]]).OnlyEnforceIf(same)
                    model.AddBoolOr([assign[prev_key].Not(), assign[next_key].Not()]).OnlyEnforceIf(same.Not())
                    same_bools.append(same)
            if same_bools:
                model.AddMaxEquality(has_continuity[(line, d)], same_bools)
            else:
                model.Add(has_continuity[(line, d)] == 0)
            # changed = prod_day[d] AND prod_day[d+1] AND NOT has_continuity
            model.AddBoolAnd([prod_day[(line, d)], prod_day[(line, d + 1)], has_continuity[(line, d)].Not()]).OnlyEnforceIf(changed[(line, d)])
            model.AddBoolOr([prod_day[(line, d)].Not(), prod_day[(line, d + 1)].Not(), has_continuity[(line, d)]]).OnlyEnforceIf(changed[(line, d)].Not())

    # is_start detection for min/max run days
    for g in grades:
        for line in lines:
            for d in range(num_days):
                key = (g, line, d)
                if key in is_start:
                    # is_start <= assign
                    model.Add(is_start[key] <= assign[(line, d, g)])
                    if d == 0:
                        model.Add(is_start[key] >= assign[(line, d, g)])
                    else:
                        prev_key = (line, d - 1, g)
                        if prev_key in assign:
                            model.Add(is_start[key] >= assign[(line, d, g)] - assign[prev_key])
                        else:
                            model.Add(is_start[key] >= assign[(line, d, g)])

    # enforce min/max run days when is_start==1
    for g in grades:
        for line in lines:
            min_run = int(instance.get('min_run_days', {}).get((g, line), 1))
            max_run = int(instance.get('max_run_days', {}).get((g, line), num_days))
            for d in range(num_days):
                key = (g, line, d)
                if key in is_start:
                    block = []
                    for k in range(max_run):
                        dd = d + k
                        if dd >= num_days:
                            break
                        if (line, dd, g) in assign:
                            block.append(assign[(line, dd, g)])
                    if block:
                        model.Add(sum(block) >= min_run * is_start[key])
                        # upper bound to prevent arbitrarily long runs - summing <= max_run (independent of is_start)
                        model.Add(sum(block) <= max_run)
                    else:
                        model.Add(is_start[key] == 0)

    # rerun_allowed: if False => sum(is_start for (g,line,*)) <= 1
    for g in grades:
        for line in lines:
            starts = [is_start[(g, line, d)] for d in range(num_days) if (g, line, d) in is_start]
            if starts:
                allowed = instance.get('rerun_allowed', {}).get((g, line), True)
                if not allowed:
                    model.Add(sum(starts) <= 1)

    # OBJECTIVE: minimize stockout_penalty * unmet + transition_penalty * changed
    stockout_penalty = int(parameters.get('stockout_penalty', 10))
    transition_penalty = int(parameters.get('transition_penalty', 10))
    obj_terms = []
    for g in grades:
        for d in range(num_days):
            obj_terms.append(stockout_penalty * unmet[(g, d)])
    for line in lines:
        for d in range(num_days - 1):
            obj_terms.append(transition_penalty * changed[(line, d)])
    model.Minimize(sum(obj_terms))

    # Solver
    solver = cp_model.CpSolver()
    time_limit = parameters.get('time_limit_min', 10)
    solver.parameters.max_time_in_seconds = time_limit * 60.0
    solver.parameters.num_search_workers = parameters.get('num_search_workers', 8)
    solver.parameters.random_seed = 42

    # Collect solutions via callback
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
                'unmet': {}
            }
            # collects assign
            for (line, d, g), var in assign.items():
                if self.Value(var) == 1:
                    sol['assign'][(line, d)] = g
            for (line, d, g), var in production.items():
                val = self.Value(var)
                if val:
                    sol['production'].setdefault((line, d), {})[g] = val
            for (g, d), var in inventory.items():
                sol['inventory'][(g, d)] = self.Value(var)
            for (g, d), var in unmet.items():
                val = self.Value(var)
                if val:
                    sol['unmet'][(g, d)] = val
            self.solutions.append(sol)

    collector = Collector()
    status = solver.SolveWithSolutionCallback(model, collector)

    status_name = solver.StatusName(status)
    result = {
        'status': status_name,
        'solver': solver,
        'solutions': collector.solutions,
        'best': collector.solutions[-1] if collector.solutions else None
    }
    return result
