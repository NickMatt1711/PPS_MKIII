"""
CP-SAT core solver.
This version restores the full feasibility behavior of the original
'Old Logic with Sidebar.py' solver EXCEPT the continuity-bonus
objective term, which is intentionally removed per requirements.
"""

from ortools.sat.python import cp_model
from typing import Dict, Any, Callable, List, Tuple
import time


# ------------------------------------------------------------
#  Solution Collector
# ------------------------------------------------------------
class SolutionCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self,
                 production,
                 inventory,
                 stockout,
                 is_prod,
                 grades,
                 lines,
                 dates,
                 fdates,
                 num_days):
        super().__init__()
        self.production = production
        self.inventory = inventory
        self.stockout = stockout
        self.is_prod = is_prod
        self.grades = grades
        self.lines = lines
        self.dates = dates
        self.fdates = fdates
        self.num_days = num_days

        self.solutions = []
        self.start_time = time.time()

    def on_solution_callback(self):
        sol = {
            "objective": self.ObjectiveValue(),
            "time": time.time() - self.start_time,
            "production": {},
            "inventory": {},
            "stockout": {},
            "is_producing": {},
            "transitions": {}
        }

        # Production
        for g in self.grades:
            sol["production"][g] = {}
            for d in range(self.num_days):
                total = 0
                for l in self.lines:
                    v = self.Value(self.production[(g, l, d)])
                    if v > 0:
                        total += v
                if total > 0:
                    sol["production"][g][self.fdates[d]] = total

        # Inventory
        for g in self.grades:
            sol["inventory"][g] = {}
            for d in range(self.num_days + 1):
                sol["inventory"][g][
                    self.fdates[d] if d < self.num_days else "final"
                ] = self.Value(self.inventory[(g, d)])

        # Stockout
        for g in self.grades:
            sol["stockout"][g] = {}
            for d in range(self.num_days):
                v = self.Value(self.stockout[(g, d)])
                if v > 0:
                    sol["stockout"][g][self.fdates[d]] = v

        # Schedule
        for l in self.lines:
            sol["is_producing"][l] = {}
            for d in range(self.num_days):
                sol["is_producing"][l][self.fdates[d]] = None
                for g in self.grades:
                    if self.Value(self.is_prod[(g, l, d)]) == 1:
                        sol["is_producing"][l][self.fdates[d]] = g
                        break

        # Transitions count
        transitions = {}
        for l in self.lines:
            transitions[l] = 0
            last = None
            for d in range(self.num_days):
                cur = None
                for g in self.grades:
                    if self.Value(self.is_prod[(g, l, d)]) == 1:
                        cur = g
                        break
                if last is not None and cur is not None and cur != last:
                    transitions[l] += 1
                if cur is not None:
                    last = cur

        sol["transitions"] = {
            "per_line": transitions,
            "total": sum(transitions.values())
        }

        self.solutions.append(sol)


# ------------------------------------------------------------
#  Main Solve Function
# ------------------------------------------------------------
def solve_schedule(inputs: Dict[str, Any],
                   params: Dict[str, Any],
                   on_progress: Callable[[int, str], None] = None) -> Dict[str, Any]:
    grades = inputs["grades"]
    lines = inputs["lines"]
    dates = inputs["dates"]
    fdates = inputs["formatted_dates"]
    num_days = inputs["num_days"]

    capacities = inputs["capacities"]
    allowed = inputs["allowed_lines"]
    demand = inputs["demand_data"]
    initial_inv = inputs["initial_inventory"]
    min_inv = inputs["min_inventory"]
    max_inv = inputs["max_inventory"]
    min_close = inputs["min_closing_inventory"]
    min_run = inputs["min_run_days"]
    max_run = inputs["max_run_days"]
    force_start = inputs["force_start_date"]
    rerun_allowed = inputs["rerun_allowed"]
    matinfo = inputs["material_running_info"]
    shutdowns = inputs["shutdown_periods"]
    transitions_allowed = inputs["transition_rules"]

    buffer_days = params.get("buffer_days", 3)
    time_limit = params.get("time_limit_min", 10)
    stockout_penalty = params.get("stockout_penalty", 1000)
    transition_penalty = params.get("transition_penalty", 100)
    holding_cost = params.get("holding_cost", 1)

    model = cp_model.CpModel()

    # --------------------------------------------------------
    # Variables
    # --------------------------------------------------------
    is_prod = {}
    production = {}

    for g in grades:
        for l in lines:
            for d in range(num_days):
                key = (g, l, d)
                is_prod[key] = model.NewBoolVar(f"is_{g}_{l}_{d}")

                p = model.NewIntVar(0, capacities[l], f"prod_{g}_{l}_{d}")
                production[key] = p

                # Original solver logic: NEVER force == capacity
                # Only restrict to <= capacity.
                model.Add(p <= capacities[l] * is_prod[key])

    # Disallow forbidden grade-line combos
    for g in grades:
        for l in lines:
            if l not in allowed.get(g, []):
                for d in range(num_days):
                    model.Add(is_prod[(g, l, d)] == 0)
                    model.Add(production[(g, l, d)] == 0)

    # --------------------------------------------------------
    # Capacity per day per line
    # --------------------------------------------------------
    for l in lines:
        for d in range(num_days):
            day_prods = [production[(g, l, d)] for g in grades]

            if l in shutdowns and d in shutdowns[l]:
                model.Add(sum(day_prods) == 0)
                for g in grades:
                    model.Add(is_prod[(g, l, d)] == 0)
            else:
                # Original behavior: <= capacity ALWAYS
                model.Add(sum(day_prods) <= capacities[l])

    # --------------------------------------------------------
    # One grade max per day per line
    # --------------------------------------------------------
    for l in lines:
        for d in range(num_days):
            model.Add(sum(is_prod[(g, l, d)] for g in grades) <= 1)

    # --------------------------------------------------------
    # Material running enforcement
    # --------------------------------------------------------
    for plant, tup in matinfo.items():
        material, exp = tup
        for d in range(min(exp, num_days)):
            if (material, plant, d) in is_prod:
                model.Add(is_prod[(material, plant, d)] == 1)
                # force all other grades off
                for g in grades:
                    if g != material and (g, plant, d) in is_prod:
                        model.Add(is_prod[(g, plant, d)] == 0)

    # --------------------------------------------------------
    # Inventory
    # --------------------------------------------------------
    inventory = {}
    stockout = {}

    for g in grades:
        for d in range(num_days + 1):
            inventory[(g, d)] = model.NewIntVar(0, 10**7, f"inv_{g}_{d}")
        for d in range(num_days):
            stockout[(g, d)] = model.NewIntVar(0, 10**7, f"so_{g}_{d}")

        model.Add(inventory[(g, 0)] == initial_inv.get(g, 0))

        for d in range(num_days):
            produced_today = sum(production[(g, l, d)] for l in lines)
            dem = int(demand[g].get(dates[d], 0))

            supplied = model.NewIntVar(0, 10**7, f"supp_{g}_{d}")
            model.Add(supplied <= inventory[(g, d)] + produced_today)
            model.Add(supplied <= dem)

            model.Add(stockout[(g, d)] == dem - supplied)
            model.Add(inventory[(g, d + 1)]
                      == inventory[(g, d)] + produced_today - supplied)
            model.Add(inventory[(g, d + 1)] >= 0)

    # --------------------------------------------------------
    # Soft min inventory and soft closing inventory
    # --------------------------------------------------------
    deficit_terms = []
    for g in grades:
        for d in range(num_days):
            mi = int(min_inv.get(g, 0))
            if mi > 0:
                defv = model.NewIntVar(0, 10**7, f"def_{g}_{d}")
                model.Add(defv >= mi - inventory[(g, d + 1)])
                deficit_terms.append((defv, stockout_penalty))

    close_terms = []
    for g in grades:
        cl = int(min_close.get(g, 0))
        if cl > 0:
            inv = inventory[(g, num_days - buffer_days)]
            c = model.NewIntVar(0, 10**7, f"clos_{g}")
            model.Add(c >= cl - inv)
            close_terms.append((c, stockout_penalty * 3))

    # --------------------------------------------------------
    # Forced start
    # --------------------------------------------------------
    for (g, l), dt in force_start.items():
        if dt:
            try:
                idx = dates.index(dt)
                if (g, l, idx) in is_prod:
                    model.Add(is_prod[(g, l, idx)] == 1)
            except ValueError:
                pass

    # --------------------------------------------------------
    # Run-length constraints (restored to original behavior)
    # --------------------------------------------------------
    start = {}
    for g in grades:
        for l in lines:
            for d in range(num_days):
                if (g, l, d) not in is_prod:
                    continue

                s = model.NewBoolVar(f"start_{g}_{l}_{d}")
                start[(g, l, d)] = s

                if d == 0:
                    model.Add(s == is_prod[(g, l, d)])
                else:
                    model.AddBoolAnd([
                        is_prod[(g, l, d)],
                        is_prod[(g, l, d - 1)].Not()
                    ]).OnlyEnforceIf(s)
                    model.AddBoolOr([
                        is_prod[(g, l, d)].Not(),
                        is_prod[(g, l, d - 1)]
                    ]).OnlyEnforceIf(s.Not())

    # Original run-length semantics
    for g in grades:
        for l in allowed.get(g, []):
            key = (g, l)
            mn = min_run.get(key, 1)
            mx = max_run.get(key, 10**6)

            if mn <= 1 and mx >= 10**6:
                continue

            for d in range(num_days):
                if (g, l, d) not in start:
                    continue

                s_var = start[(g, l, d)]

                # min run
                if mn > 1:
                    seq = []
                    for k in range(d, min(num_days, d + mn)):
                        if not (l in shutdowns and k in shutdowns[l]):
                            seq.append(is_prod[(g, l, k)])
                    if len(seq) >= mn:
                        model.Add(sum(seq) >= mn).OnlyEnforceIf(s_var)

                # max run
                if mx < 10**6:
                    seq = []
                    for k in range(d, min(num_days, d + mx + 1)):
                        if not (l in shutdowns and k in shutdowns[l]):
                            seq.append(is_prod[(g, l, k)])
                    if seq:
                        model.Add(sum(seq) <= mx).OnlyEnforceIf(s_var)

    # --------------------------------------------------------
    # No rerun if disabled
    # --------------------------------------------------------
    for (g, l), allow in rerun_allowed.items():
        if not allow:
            starts = [start[k] for k in start if k[0] == g and k[1] == l]
            if starts:
                model.Add(sum(starts) <= 1)

    # --------------------------------------------------------
    # Transitions (original logic restored)
    # --------------------------------------------------------
    transition_vars = []

    for l in lines:
        for d in range(num_days - 1):
            t = model.NewBoolVar(f"trans_{l}_{d}")
            transition_vars.append(t)

            # detect different grades
            eqs = []
            for g in grades:
                g1 = is_prod[(g, l, d)]
                g2 = is_prod[(g, l, d + 1)]

                # track same-grade cases
                same = model.NewBoolVar(f"same_{g}_{l}_{d}")
                model.AddBoolAnd([g1, g2]).OnlyEnforceIf(same)
                model.AddBoolOr([g1.Not(), g2.Not()]).OnlyEnforceIf(same.Not())
                eqs.append(same)

            # If ALL eqs = 0 and both days have production → transition
            has_same = model.NewBoolVar(f"s_{l}_{d}")
            model.AddMaxEquality(has_same, eqs)

            prod_d = model.NewBoolVar(f"pd_{l}_{d}")
            prod_d1 = model.NewBoolVar(f"pd1_{l}_{d}")
            model.AddMaxEquality(prod_d, [is_prod[(g, l, d)] for g in grades])
            model.AddMaxEquality(prod_d1, [is_prod[(g, l, d + 1)] for g in grades])

            model.AddBoolAnd([prod_d, prod_d1, has_same.Not()]).OnlyEnforceIf(t)
            model.AddBoolOr([prod_d.Not(), prod_d1.Not(), has_same]).OnlyEnforceIf(t.Not())

            # Respect transition matrix (only forbid explicitly forbidden pairs)
            rules = transitions_allowed.get(l, {})
            for g1 in grades:
                for g2 in grades:
                    if g1 == g2:
                        continue
                    if g1 in rules and g2 not in rules[g1]:
                        # forbid g1 -> g2
                        model.Add(is_prod[(g1, l, d)] +
                                  is_prod[(g2, l, d + 1)] <= 1)

    # --------------------------------------------------------
    # Objective (continuity bonus removed)
    # --------------------------------------------------------
    obj = []

    # stockout + holding
    for g in grades:
        for d in range(num_days):
            obj.append(stockout_penalty * stockout[(g, d)])
            obj.append(holding_cost * inventory[(g, d)])

    # deficits & closing
    for val, wt in deficit_terms:
        obj.append(wt * val)
    for val, wt in close_terms:
        obj.append(wt * val)

    # transitions penalty
    for t in transition_vars:
        obj.append(transition_penalty * t)

    model.Minimize(sum(obj))

    # --------------------------------------------------------
    # Solve
    # --------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(1, time_limit * 60)
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 42
    solver.parameters.log_search_progress = False

    cb = SolutionCallback(production, inventory, stockout,
                          is_prod, grades, lines, dates, fdates, num_days)

    status = solver.Solve(model, cb)

    result = {"status": status,
              "solutions": cb.solutions,
              "final": {}}

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        prod_res = {}
        inv_res = {}
        so_res = {}
        sched = {}

        for g in grades:
            prod_res[g] = {}
            inv_res[g] = {}
            so_res[g] = {}
            for d in range(num_days):
                # production sums
                total = sum(solver.Value(production[(g, l, d)])
                            for l in lines)
                if total > 0:
                    prod_res[g][fdates[d]] = total

                inv_res[g][fdates[d]] = solver.Value(inventory[(g, d)])
                so_res[g][fdates[d]] = solver.Value(stockout[(g, d)])

            inv_res[g]["final"] = solver.Value(inventory[(g, num_days)])

        for l in lines:
            sched[l] = {}
            for d in range(num_days):
                sched[l][fdates[d]] = None
                for g in grades:
                    if solver.Value(is_prod[(g, l, d)]) == 1:
                        sched[l][fdates[d]] = g
                        break

        result["final"] = {
            "production": prod_res,
            "inventory": inv_res,
            "stockout": so_res,
            "schedule": sched,
            "objective": solver.ObjectiveValue()
        }

    return result
