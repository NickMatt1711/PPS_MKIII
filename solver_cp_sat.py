"""
CP-SAT core solver. Preserves all constraints from the old logic with one key change:
continuity bonus logic removed from the objective (per requirements).
"""

from ortools.sat.python import cp_model
import time
from typing import Dict, Any, Callable, Tuple, List

class SolutionCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, production, inventory, stockout, is_producing, grades, lines, dates, formatted_dates, num_days):
        super().__init__()
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
        self.start_time = time.time()

    def on_solution_callback(self):
        # capture succinct snapshot
        sol = {"objective": self.ObjectiveValue(), "time": time.time()-self.start_time,
               "production": {}, "is_producing": {}, "inventory": {}, "stockout": {}}
        for g in self.grades:
            sol["production"][g] = {}
            sol["inventory"][g] = {}
            sol["stockout"][g] = {}
            for l in self.lines:
                for d in range(self.num_days):
                    k = (g, l, d)
                    if k in self.production:
                        val = self.Value(self.production[k])
                        if val:
                            sol["production"][g].setdefault(self.formatted_dates[d], 0)
                            sol["production"][g][self.formatted_dates[d]] += val
        for l in self.lines:
            sol["is_producing"][l] = {}
            for d in range(self.num_days):
                sol["is_producing"][l][self.formatted_dates[d]] = None
                for g in self.grades:
                    k = (g, l, d)
                    if k in self.is_producing and self.Value(self.is_producing[k]) == 1:
                        sol["is_producing"][l][self.formatted_dates[d]] = g
                        break
        for g in self.grades:
            for d in range(self.num_days+1):
                k = (g, d)
                if k in self.inventory:
                    sol["inventory"][g][self.formatted_dates[d] if d < self.num_days else "final"] = self.Value(self.inventory[k])
        for g in self.grades:
            for d in range(self.num_days):
                k = (g, d)
                if k in self.stockout:
                    sv = self.Value(self.stockout[k])
                    if sv > 0:
                        sol["stockout"][g][self.formatted_dates[d]] = sv
        # count transitions
        trans_per_line = {l: 0 for l in self.lines}
        total_t = 0
        for l in self.lines:
            last = None
            for d in range(self.num_days):
                curg = None
                for g in self.grades:
                    k = (g, l, d)
                    if k in self.is_producing and self.Value(self.is_producing[k]) == 1:
                        curg = g
                        break
                if curg is not None and last is not None and curg != last:
                    trans_per_line[l] += 1
                    total_t += 1
                if curg is not None:
                    last = curg
        sol["transitions"] = {"per_line": trans_per_line, "total": total_t}
        self.solutions.append(sol)

    def num_solutions(self):
        return len(self.solutions)

def solve_schedule(inputs: Dict[str, Any], params: Dict[str, Any], on_progress: Callable[[int, str], None] = None) -> Dict[str, Any]:
    """
    inputs: dict returned by data_loader.parse_input_excel
    params: solver params (time_limit_min, buffer_days, penalties)
    on_progress: optional callback(progress_percent:int, message:str)
    returns: solution dict with last solution and callback history
    """
    # unpack
    grades = inputs["grades"]
    lines = inputs["lines"]
    dates = inputs["dates"]
    formatted_dates = inputs["formatted_dates"]
    num_days = inputs["num_days"]
    capacities = inputs["capacities"]
    allowed_lines = inputs["allowed_lines"] if "allowed_lines" in inputs else None
    demand_data = inputs["demand_data"]
    initial_inventory = inputs["initial_inventory"]
    min_inventory = inputs["min_inventory"]
    max_inventory = inputs["max_inventory"]
    min_closing_inventory = inputs["min_closing_inventory"]
    min_run_days = inputs["min_run_days"]
    max_run_days = inputs["max_run_days"]
    force_start_date = inputs["force_start_date"]
    rerun_allowed = inputs["rerun_allowed"]
    material_running_info = inputs["material_running_info"]
    shutdown_periods = inputs["shutdown_periods"]
    transition_rules = inputs["transition_rules"]
    buffer_days = params.get("buffer_days", 3)
    time_limit_min = params.get("time_limit_min", 10)
    stockout_penalty = params.get("stockout_penalty", 1000)
    transition_penalty = params.get("transition_penalty", 100)
    holding_cost = params.get("holding_cost", 1)

    model = cp_model.CpModel()

    # Variables
    is_producing = {}
    production = {}
    for g in grades:
        for l in lines:
            for d in range(num_days):
                key = (g, l, d)
                is_producing[key] = model.NewBoolVar(f"is_{g}_{l}_{d}")
                # production amount
                prod = model.NewIntVar(0, capacities[l], f"prod_{g}_{l}_{d}")
                # usual enforcement: exact capacity when not in buffer days, <= otherwise
                if d < num_days - buffer_days:
                    model.Add(prod == capacities[l]).OnlyEnforceIf(is_producing[key])
                    model.Add(prod == 0).OnlyEnforceIf(is_producing[key].Not())
                else:
                    model.Add(prod <= capacities[l] * is_producing[key])
                production[key] = prod
    # forbid not-allowed combinations
    for g in grades:
        for l in lines:
            if l not in inputs["allowed_lines"].get(g, []):
                for d in range(num_days):
                    model.Add(is_producing[(g, l, d)] == 0)
                    model.Add(production[(g, l, d)] == 0)

    # inventory & stockout
    inventory = {}
    stockout = {}
    for g in grades:
        for d in range(num_days + 1):
            inventory[(g, d)] = model.NewIntVar(0, 10**7, f"inv_{g}_{d}")
        for d in range(num_days):
            stockout[(g, d)] = model.NewIntVar(0, 10**7, f"stockout_{g}_{d}")

    # capacity per line per day
    for l in lines:
        for d in range(num_days):
            prods = [production[(g, l, d)] for g in grades]
            if l in shutdown_periods and d in shutdown_periods[l]:
                # zero production
                model.Add(sum(prods) == 0)
                for g in grades:
                    model.Add(is_producing[(g, l, d)] == 0)
            elif d < num_days - buffer_days:
                model.Add(sum(prods) == capacities[l])
            else:
                model.Add(sum(prods) <= capacities[l])

    # only one grade per line per day
    for l in lines:
        for d in range(num_days):
            model.Add(sum(is_producing[(g, l, d)] for g in grades) <= 1)

    # material running info enforcement
    for plant, tup in material_running_info.items():
        material, exp_days = tup
        for d in range(min(exp_days, num_days)):
            if (material, plant, d) in is_producing:
                model.Add(is_producing[(material, plant, d)] == 1)
                for other in grades:
                    if other != material and (other, plant, d) in is_producing:
                        model.Add(is_producing[(other, plant, d)] == 0)

    # inventory balance and stockout logic
    for g in grades:
        model.Add(inventory[(g, 0)] == initial_inventory.get(g, 0))
        for d in range(num_days):
            produced_today = sum(production[(g, l, d)] for l in lines)
            demand_today = int(demand_data[g].get(dates[d], 0))
            # supplied <= inventory + produced and <= demand
            supplied = model.NewIntVar(0, 10**7, f"supplied_{g}_{d}")
            model.Add(supplied <= inventory[(g, d)] + produced_today)
            model.Add(supplied <= demand_today)
            # stockout = demand - supplied
            model.Add(stockout[(g, d)] == demand_today - supplied)
            # inventory tomorrow
            model.Add(inventory[(g, d+1)] == inventory[(g, d)] + produced_today - supplied)
            model.Add(inventory[(g, d+1)] >= 0)
    # min/max inventory constraints (soft via deficits)
    deficits = []
    for g in grades:
        for d in range(num_days):
            mi = int(min_inventory.get(g, 0))
            if mi > 0:
                deficit = model.NewIntVar(0, 10**7, f"deficit_{g}_{d}")
                model.Add(deficit >= mi - inventory[(g, d+1)])
                model.Add(deficit >= 0)
                deficits.append((deficit, stockout_penalty))
    # closing inventory soft
    closing_defs = []
    for g in grades:
        min_cl = int(min_closing_inventory.get(g, 0))
        if min_cl > 0:
            closing_inv = inventory[(g, num_days - buffer_days)]
            cd = model.NewIntVar(0, 10**7, f"closing_def_{g}")
            model.Add(cd >= min_cl - closing_inv)
            model.Add(cd >= 0)
            closing_defs.append((cd, stockout_penalty * 3))

    # force start
    for (g, p), dt in force_start_date.items():
        if dt:
            try:
                day_index = inputs["dates"].index(dt)
                if (g, p, day_index) in is_producing:
                    model.Add(is_producing[(g, p, day_index)] == 1)
            except ValueError:
                # start date outside horizon — ignore but could warn upstream
                pass

    # min/max run days (accounting for shutdown interruptions).
    # Define start indicators and run-length counters per run segment.
    is_start = {}
    is_end = {}
    for g in grades:
        for l in lines:
            for d in range(num_days):
                if (g, l, d) not in is_producing:
                    continue
                s = model.NewBoolVar(f"start_{g}_{l}_{d}")
                e = model.NewBoolVar(f"end_{g}_{l}_{d}")
                is_start[(g, l, d)] = s
                is_end[(g, l, d)] = e
                if d == 0:
                    model.Add(s == is_producing[(g, l, d)])
                else:
                    model.AddBoolAnd([is_producing[(g, l, d)], is_producing[(g, l, d-1)].Not()]).OnlyEnforceIf(s)
                    model.AddBoolOr([is_producing[(g, l, d)].Not(), is_producing[(g, l, d-1)]]).OnlyEnforceIf(s.Not())
                if d == num_days - 1:
                    model.Add(e == is_producing[(g, l, d)])
                else:
                    model.AddBoolAnd([is_producing[(g, l, d)], is_producing[(g, l, d+1)].Not()]).OnlyEnforceIf(e)
                    model.AddBoolOr([is_producing[(g, l, d)].Not(), is_producing[(g, l, d+1)]]).OnlyEnforceIf(e.Not())

    # Enforce min/max run days by linking starts to following run length windows ignoring shutdown days
    for g in grades:
        for l in inputs["allowed_lines"].get(g, []):
            key = (g, l)
            minr = min_run_days.get(key, 1)
            maxr = max_run_days.get(key, 10**6)
            if minr <= 1 and maxr >= 10**6:
                continue
            for d in range(num_days):
                if (g, l, d) not in is_start:
                    continue
                s_var = is_start[(g, l, d)]
                # For min run: if start at d then sum(is_producing over next minr days excluding shutdown) >= minr if possible
                days_considered = []
                idx = d
                counted = 0
                # collect next minr production days (skipping shutdowns)
                while idx < num_days and counted < minr:
                    if not (l in shutdown_periods and idx in shutdown_periods[l]):
                        if (g, l, idx) in is_producing:
                            days_considered.append(is_producing[(g, l, idx)])
                            counted += 1
                    idx += 1
                if counted == minr and days_considered:
                    model.Add(sum(days_considered) >= minr).OnlyEnforceIf(s_var)
                # max run: limit how many consecutive production days following start can be true
                if maxr < 10**6:
                    days_considered_max = []
                    idx = d
                    counted = 0
                    while idx < num_days and counted < maxr:
                        if not (l in shutdown_periods and idx in shutdown_periods[l]):
                            if (g, l, idx) in is_producing:
                                days_considered_max.append(is_producing[(g, l, idx)])
                                counted += 1
                        idx += 1
                    if days_considered_max:
                        model.Add(sum(days_considered_max) <= maxr).OnlyEnforceIf(s_var)

    # no rerun allowed -> at most one start
    for (g, l), allowed in rerun_allowed.items():
        if not allowed:
            starts = [v for k, v in is_start.items() if k[0] == g and k[1] == l]
            if starts:
                model.Add(sum(starts) <= 1)

    # transitions: create indicator for changeover between day d and d+1
    transition_vars = []
    for l in lines:
        for d in range(num_days - 1):
            trans = model.NewBoolVar(f"trans_{l}_{d}")
            # If production on both days and grade differs then trans=1
            # Build indicator pairs
            # prod_on_d and prod_on_d1
            prod_d = model.NewBoolVar(f"prod_{l}_{d}")
            prod_d1 = model.NewBoolVar(f"prod_{l}_{d+1}")
            model.AddMaxEquality(prod_d, [is_producing[(g, l, d)] for g in grades])
            model.AddMaxEquality(prod_d1, [is_producing[(g, l, d+1)] for g in grades])
            # create pairwise same-grade indicators, then if any same-grade then no transition
            same_indicators = []
            for g in grades:
                # only if g allowed on l
                if l in inputs["allowed_lines"].get(g, []):
                    same = model.NewBoolVar(f"same_{g}_{l}_{d}")
                    model.AddBoolAnd([is_producing[(g, l, d)], is_producing[(g, l, d+1)]]).OnlyEnforceIf(same)
                    # If not both true, same==0
                    model.AddBoolOr([is_producing[(g, l, d)].Not(), is_producing[(g, l, d+1)].Not()]).OnlyEnforceIf(same.Not())
                    same_indicators.append(same)
            has_same = model.NewBoolVar(f"has_same_{l}_{d}")
            if same_indicators:
                model.AddMaxEquality(has_same, same_indicators)
            else:
                model.Add(has_same == 0)
            # transition if production on both days and NOT has_same
            model.AddBoolAnd([prod_d, prod_d1, has_same.Not()]).OnlyEnforceIf(trans)
            model.AddBoolOr([prod_d.Not(), prod_d1.Not(), has_same]).OnlyEnforceIf(trans.Not())
            # respect transition matrix: if specific prev->next is forbidden, disallow the pair by forcing trans=0 for that pair.
            # Simpler: penalize trans only if allowed by transition_rules; if disallowed, forbid the specific combination.
            # We'll forbid disallowed prev->next pairs
            for g1 in grades:
                for g2 in grades:
                    if g1 == g2: 
                        continue
                    if l in transition_rules and transition_rules.get(l):
                        rules = transition_rules[l]
                        if g1 in rules and g2 not in rules[g1]:
                            # forbid combination: can't have g1 at d and g2 at d+1
                            model.AddBoolAnd([is_producing[(g1, l, d)], is_producing[(g2, l, d+1)]]).OnlyEnforceIf(model.NewBoolVar("forbidden_tmp").Not())
                            # Simpler robust approach: directly forbid
                            model.Add(is_producing[(g1, l, d)] + is_producing[(g2, l, d+1)] <= 1)

            transition_vars.append(trans)

    # Objective
    obj_terms = []
    for g in grades:
        for d in range(num_days):
            obj_terms.append(stockout_penalty * stockout[(g, d)])
            obj_terms.append(holding_cost * inventory[(g, d)])
    # closing deficits
    for cd, wt in closing_defs:
        obj_terms.append(wt * cd)
    # deficits
    for df, wt in deficits:
        obj_terms.append(wt * df)
    # transitions penalty
    for t in transition_vars:
        obj_terms.append(transition_penalty * t)

    model.Minimize(sum(obj_terms))

    # solver and solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(1.0, time_limit_min * 60.0)
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 42
    solver.parameters.log_search_progress = False

    callback = SolutionCallback(production, inventory, stockout, is_producing, grades, lines, dates, formatted_dates, num_days)
    status = solver.Solve(model, callback)

    # build final solution structure (extract only if feasible/optimal)
    result = {"status": status, "solutions": callback.solutions, "final": {}}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # extract arrays
        production_res = {}
        inventory_res = {}
        schedule = {}
        stockout_res = {}
        for g in grades:
            production_res[g] = {}
            inventory_res[g] = {}
            stockout_res[g] = {}
            for d in range(num_days):
                for l in lines:
                    val = solver.Value(production[(g, l, d)])
                    if val:
                        production_res[g].setdefault(formatted_dates[d], 0)
                        production_res[g][formatted_dates[d]] += val
                inventory_res[g][formatted_dates[d]] = solver.Value(inventory[(g, d)])
                stockout_res[g][formatted_dates[d]] = solver.Value(stockout[(g, d)])
            # final inventory
            inventory_res[g]["final"] = solver.Value(inventory[(g, num_days)])
        # schedule per line
        for l in lines:
            schedule[l] = {}
            for d in range(num_days):
                schedule[l][formatted_dates[d]] = None
                for g in grades:
                    if (g, l, d) in is_producing and solver.Value(is_producing[(g, l, d)]) == 1:
                        schedule[l][formatted_dates[d]] = g
                        break
        result["final"] = {
            "production": production_res,
            "inventory": inventory_res,
            "stockout": stockout_res,
            "schedule": schedule,
            "objective": solver.ObjectiveValue() if status == cp_model.OPTIMAL else None
        }
    return result
