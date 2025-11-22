"""
CP-SAT Solver for production optimization
"""

from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple, Set, Any
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED


# ================================================================
#                         SOLUTION CALLBACK
# ================================================================
class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Captures all intermediate solutions."""

    def __init__(
        self,
        production,
        inventory_vars,
        stockout_vars,
        is_producing,
        grades,
        lines,
        dates,
        formatted_dates,
        num_days
    ):
        cp_model.CpSolverSolutionCallback.__init__(self)

        self.production = production
        self.inventory_vars = inventory_vars
        self.stockout_vars = stockout_vars
        self.is_producing = is_producing

        self.grades = grades
        self.lines = lines
        self.dates = dates
        self.formatted_dates = formatted_dates
        self.num_days = num_days

        self.solutions = []
        self.solution_times = []
        self.start = time.time()

    def on_solution_callback(self):
        now = time.time() - self.start
        self.solution_times.append(now)
        obj = self.ObjectiveValue()

        sol = {
            "objective": obj,
            "time": now,
            "production": {},
            "inventory": {},
            "stockout": {},
            "is_producing": {},
        }

        # Production
        for grade in self.grades:
            sol["production"][grade] = {}
            for line in self.lines:
                for d in range(self.num_days):
                    key = (grade, line, d)
                    if key in self.production:
                        v = self.Value(self.production[key])
                        if v > 0:
                            date_key = self.formatted_dates[d]
                            sol["production"][grade].setdefault(date_key, 0)
                            sol["production"][grade][date_key] += v

        # Inventory
        for grade in self.grades:
            sol["inventory"][grade] = {}
            for d in range(self.num_days + 1):
                key = (grade, d)
                v = self.Value(self.inventory_vars[key])
                if d == 0:
                    sol["inventory"][grade]["initial"] = v
                elif d == self.num_days:
                    sol["inventory"][grade]["final"] = v
                else:
                    sol["inventory"][grade][self.formatted_dates[d]] = v

        # Stockout
        for grade in self.grades:
            sol["stockout"][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                v = self.Value(self.stockout_vars[key])
                if v > 0:
                    sol["stockout"][grade][self.formatted_dates[d]] = v

        # is_producing
        for line in self.lines:
            sol["is_producing"][line] = {}
            for d in range(self.num_days):
                sol["is_producing"][line][self.formatted_dates[d]] = None
                for grade in self.grades:
                    key = (grade, line, d)
                    if key in self.is_producing and self.Value(self.is_producing[key]) == 1:
                        sol["is_producing"][line][self.formatted_dates[d]] = grade
                        break

        # Transition counts
        transitions = {l: 0 for l in self.lines}
        total = 0
        for line in self.lines:
            prev = None
            for d in range(self.num_days):
                current = None
                for grade in self.grades:
                    key = (grade, line, d)
                    if key in self.is_producing and self.Value(self.is_producing[key]) == 1:
                        current = grade
                        break
                if prev is not None and current is not None and current != prev:
                    transitions[line] += 1
                    total += 1
                if current is not None:
                    prev = current

        sol["transitions"] = {"per_line": transitions, "total": total}
        self.solutions.append(sol)

    def num_solutions(self):
        return len(self.solutions)


# ================================================================
#            NORMALIZE TRANSITION RULES ("Yes"/"No")
# ================================================================
def normalize_transition_rules(raw, grades):
    """
    Produces:
        allowed_next[line][prev_grade] = {allowed_next_grades}
    Accepts:
        - dict[prev] = [list of allowed next]
        - dict[prev] = {next: "Yes"/"No"}
    """
    allowed_next = {}

    if raw is None:
        return allowed_next

    for line, mapping in raw.items():
        allowed_next[line] = {}

        for prev in grades:
            entry = mapping.get(prev)
            if entry is None:
                # unspecified → allow all
                allowed_next[line][prev] = set(grades)
                continue

            if isinstance(entry, dict):
                s = set()
                for nxt, val in entry.items():
                    if isinstance(val, str) and val.strip().lower() == "yes":
                        s.add(nxt)
                allowed_next[line][prev] = s
            elif isinstance(entry, (list, set, tuple)):
                allowed_next[line][prev] = set(entry)
            else:
                allowed_next[line][prev] = set(grades)

    return allowed_next


# ================================================================
#                     MODEL BUILDER
# ================================================================
def build_and_solve_model(
    grades,
    lines,
    dates,
    formatted_dates,
    num_days,
    capacities,
    initial_inventory,
    min_inventory,
    max_inventory,
    min_closing_inventory,
    demand_data,
    allowed_lines,
    min_run_days,
    max_run_days,
    force_start_date,
    rerun_allowed,
    material_running_info,
    shutdown_periods,
    transition_rules,
    buffer_days,
    stockout_penalty,
    transition_penalty,
    continuity_bonus,
    time_limit_min,
    progress_callback=None
):

    if progress_callback:
        progress_callback(0.0, "Building model…")

    model = cp_model.CpModel()

    # ---------------------------------------------------------------
    # VARIABLES
    # ---------------------------------------------------------------
    is_producing = {}
    production = {}

    def allowed(grade, line):
        return line in allowed_lines.get(grade, [])

    # Production
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            cap = capacities[line]
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f"produce_{grade}_{line}_{d}")
                pv = model.NewIntVar(0, cap, f"prod_{grade}_{line}_{d}")

                if d < num_days - buffer_days:
                    model.Add(pv == cap).OnlyEnforceIf(is_producing[key])
                    model.Add(pv == 0).OnlyEnforceIf(is_producing[key].Not())
                else:
                    model.Add(pv <= cap * is_producing[key])

                production[key] = pv

    # Fast fetchers
    def get_prod(grade, line, d):
        return production.get((grade, line, d), None)

    def get_flag(grade, line, d):
        return is_producing.get((grade, line, d), None)

    # ---------------------------------------------------------------
    # SHUTDOWN
    # ---------------------------------------------------------------
    for line in lines:
        for d in shutdown_periods.get(line, []):
            for grade in grades:
                if allowed(grade, line):
                    key = (grade, line, d)
                    if key in is_producing:
                        model.Add(is_producing[key] == 0)
                        model.Add(production[key] == 0)

    # ---------------------------------------------------------------
    # ONE GRADE PER LINE PER DAY
    # ---------------------------------------------------------------
    for line in lines:
        for d in range(num_days):
            vars_today = []
            for grade in grades:
                if allowed(grade, line):
                    v = get_flag(grade, line, d)
                    if v is not None:
                        vars_today.append(v)
            if vars_today:
                model.Add(sum(vars_today) <= 1)

    # ---------------------------------------------------------------
    # MATERIAL RUNNING LOCK-IN
    # ---------------------------------------------------------------
    for plant, (material, days) in material_running_info.items():
        for d in range(min(days, num_days)):
            if allowed(material, plant):
                mv = get_flag(material, plant, d)
                if mv is not None:
                    model.Add(mv == 1)
                for other in grades:
                    if other != material and allowed(other, plant):
                        ov = get_flag(other, plant, d)
                        if ov is not None:
                            model.Add(ov == 0)

    # ---------------------------------------------------------------
    # INVENTORY & STOCKOUT
    # ---------------------------------------------------------------
    inventory_vars = {}
    stockout_vars = {}

    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 10**9, f"inv_{grade}_{d}")

    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 10**9, f"so_{grade}_{d}")

    # Initial inventory
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == int(initial_inventory.get(grade, 0)))
    
    def get_production_var(grade, line, d):
        key = (grade, line, d)
        return production.get(key, 0)
    
    def get_is_producing_var(grade, line, d):
        key = (grade, line, d)
        return is_producing.get(key)
        
    # Inventory balance
    for grade in grades:
        for d in range(num_days):
            # Sum production safely (no OR/ truthiness!)
            produced_today = sum(
                get_production_var(grade, line, d) 
                for line in allowed_lines[grade]
            )

            demand = demand_data.get(grade, {}).get(dates[d], 0)

            supplied = model.NewIntVar(0, 10**9, f"sup_{grade}_{d}")
            model.Add(supplied <= inventory_vars[(grade, d)] + produced_today)
            model.Add(supplied <= demand)

            so = stockout_vars[(grade, d)]
            model.Add(so == demand - supplied)

            model.Add(inventory_vars[(grade, d + 1)] ==
                      inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)

    # ---------------------------------------------------------------
    # MINIMUM INVENTORY (SOFT)
    # ---------------------------------------------------------------
    objective = 0

    for grade in grades:
        min_inv = min_inventory.get(grade, 0)
        if min_inv > 0:
            for d in range(num_days):
                deficit = model.NewIntVar(0, 10**9, f"mininvdef_{grade}_{d}")
                model.Add(deficit >= min_inv - inventory_vars[(grade, d + 1)])
                objective += stockout_penalty * deficit

    # Closing inventory
    for grade in grades:
        closing_day = max(0, num_days - 1 - buffer_days)
        needed = min_closing_inventory.get(grade, 0)
        if needed > 0:
            closing_def = model.NewIntVar(0, 10**9, f"close_def_{grade}")
            model.Add(closing_def >= needed - inventory_vars[(grade, closing_day)])
            objective += stockout_penalty * 3 * closing_def

    # Max inventory
    for grade in grades:
        max_inv = max_inventory.get(grade, 10**9)
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= max_inv)

    # ---------------------------------------------------------------
    # CAPACITY
    # ---------------------------------------------------------------
    for line in lines:
        cap = capacities[line]
        for d in range(num_days - buffer_days):
            # Full capacity
            prods = [
                (get_prod(g, line, d) if get_prod(g, line, d) is not None else 0)
                for g in grades if allowed(g, line)
            ]
            if prods:
                model.Add(sum(prods) == cap)

        for d in range(num_days - buffer_days, num_days):
            prods = [
                (get_prod(g, line, d) if get_prod(g, line, d) is not None else 0)
                for g in grades if allowed(g, line)
            ]
            if prods:
                model.Add(sum(prods) <= cap)

    # ---------------------------------------------------------------
    # FORCE START DATES
    # ---------------------------------------------------------------
    for (grade, plant), start_date in force_start_date.items():
        if start_date:
            if start_date in dates:
                d = dates.index(start_date)
                v = get_flag(grade, plant, d)
                if v is not None:
                    model.Add(v == 1)

    # ---------------------------------------------------------------
    # MIN/MAX RUN LOGIC
    # ---------------------------------------------------------------
    start_vars = {}
    end_vars = {}

    for grade in grades:
        for line in allowed_lines.get(grade, []):
            min_run = min_run_days.get((grade, line), 1)
            max_run = max_run_days.get((grade, line), 999999)

            for d in range(num_days):
                cur = get_flag(grade, line, d)
                start_v = model.NewBoolVar(f"start_{grade}_{line}_{d}")
                end_v = model.NewBoolVar(f"end_{grade}_{line}_{d}")
                start_vars[(grade, line, d)] = start_v
                end_vars[(grade, line, d)] = end_v

                if d > 0:
                    prev = get_flag(grade, line, d - 1)
                    if cur is not None and prev is not None:
                        model.AddBoolAnd([cur, prev.Not()]).OnlyEnforceIf(start_v)
                        model.AddBoolOr([cur.Not(), prev, start_v.Not()])
                else:
                    if cur is not None:
                        model.Add(cur == 1).OnlyEnforceIf(start_v)

                if d < num_days - 1:
                    nxt = get_flag(grade, line, d + 1)
                    if cur is not None and nxt is not None:
                        model.AddBoolAnd([cur, nxt.Not()]).OnlyEnforceIf(end_v)
                        model.AddBoolOr([cur.Not(), nxt, end_v.Not()])
                else:
                    if cur is not None:
                        model.Add(cur == 1).OnlyEnforceIf(end_v)

            # Minimum run constraint
            for d in range(num_days):
                s = start_vars[(grade, line, d)]
                for k in range(min_run):
                    if d + k < num_days:
                        if d + k in shutdown_periods.get(line, []):
                            break
                        v = get_flag(grade, line, d + k)
                        if v is not None:
                            model.Add(v == 1).OnlyEnforceIf(s)

            # Maximum run constraint
            if max_run < 999999:
                for d in range(num_days - max_run):
                    window = []
                    ok = True
                    for k in range(max_run + 1):
                        if d + k in shutdown_periods.get(line, []):
                            ok = False
                            break
                        v = get_flag(grade, line, d + k)
                        if v is not None:
                            window.append(v)
                    if ok and len(window) == max_run + 1:
                        model.Add(sum(window) <= max_run)

    # ---------------------------------------------------------------
    # TRANSITION CONSTRAINTS
    # ---------------------------------------------------------------
    allowed_next = normalize_transition_rules(transition_rules, grades)

    # HARD FORBIDDEN TRANSITIONS
    for line in lines:
        rules = allowed_next.get(line)
        if rules is None:
            continue  # everything allowed

        for d in range(num_days - 1):
            for g1 in grades:
                if not allowed(g1, line):
                    continue
                v1 = get_flag(g1, line, d)
                if v1 is None:
                    continue

                allowed_set = rules.get(g1, set(grades))

                for g2 in grades:
                    if g2 == g1:
                        continue
                    if not allowed(g2, line):
                        continue
                    v2 = get_flag(g2, line, d + 1)
                    if v2 is None:
                        continue

                    if g2 not in allowed_set:
                        model.Add(v1 + v2 <= 1)   # hard block

    # TRANSITION PENALTIES FOR ALLOWED ONES
    for line in lines:
        rules = allowed_next.get(line)

        for d in range(num_days - 1):
            # continuity bonus (same grade)
            for grade in grades:
                if not allowed(grade, line):
                    continue
                v1 = get_flag(grade, line, d)
                v2 = get_flag(grade, line, d + 1)
                if v1 is None or v2 is None:
                    continue
                cont = model.NewBoolVar(f"cont_{grade}_{line}_{d}")
                model.AddBoolAnd([v1, v2]).OnlyEnforceIf(cont)
                model.AddBoolOr([v1.Not(), v2.Not(), cont])
                objective += -continuity_bonus * cont

            # transition penalty (only for allowed transitions)
            for g1 in grades:
                if not allowed(g1, line):
                    continue
                v1 = get_flag(g1, line, d)
                if v1 is None:
                    continue

                allowed_set = rules.get(g1, set(grades)) if rules else set(grades)

                for g2 in grades:
                    if g1 == g2:
                        continue
                    if not allowed(g2, line):
                        continue

                    if g2 not in allowed_set:
                        continue  # forbidden → already blocked, no penalty

                    v2 = get_flag(g2, line, d + 1)
                    if v2 is None:
                        continue

                    t = model.NewBoolVar(f"trans_{g1}_{g2}_{line}_{d}")
                    model.AddBoolAnd([v1, v2]).OnlyEnforceIf(t)
                    model.AddBoolOr([v1.Not(), v2.Not(), t])
                    objective += transition_penalty * t

    # ---------------------------------------------------------------
    # STOCKOUT PENALTY
    # ---------------------------------------------------------------
    for grade in grades:
        for d in range(num_days):
            objective += stockout_penalty * stockout_vars[(grade, d)]

    model.Minimize(objective)

    # ---------------------------------------------------------------
    # SOLVE
    # ---------------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60.0
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED
    solver.parameters.log_search_progress = True

    callback = SolutionCallback(
        production,
        inventory_vars,
        stockout_vars,
        is_producing,
        grades,
        lines,
        dates,
        formatted_dates,
        num_days,
    )

    status = solver.Solve(model, callback)

    if progress_callback:
        progress_callback(1.0, "Optimization complete")

    return status, callback, solver
