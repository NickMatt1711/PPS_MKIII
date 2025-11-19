# solver_debug.py
# Drop into your repo and run in the same environment as the app.
# Prints a short report identifying which constraint group causes infeasibility.

from ortools.sat.python import cp_model
from typing import Dict, Any, List, Tuple
import time
import copy
import traceback

# Import your existing solver function names if needed:
# from solver_cp_sat import solve_schedule  # not required for debug runs

def quick_feasibility_test(build_model_fn, time_limit_sec=5):
    """
    build_model_fn() -> (model, aux) where model is cp_model.CpModel and aux is dict for variable references
    Returns True if solver returns FEASIBLE/OPTIMAL within time_limit_sec, else False, and the status.
    """
    try:
        model, aux = build_model_fn()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max(1, time_limit_sec)
        solver.parameters.num_search_workers = 8
        status = solver.Solve(model)
        ok = status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
        return ok, status
    except Exception as e:
        return False, f"exception: {e}\n{traceback.format_exc()}"

def validate_inputs_simple(inputs: Dict[str, Any]) -> List[str]:
    issues = []
    grades = inputs.get("grades", [])
    lines = inputs.get("lines", [])
    dates = inputs.get("dates", [])
    num_days = inputs.get("num_days", 0)
    capacities = inputs.get("capacities", {})
    demand = inputs.get("demand_data", {})

    # 1) Check total capacity vs total demand
    total_capacity = sum(capacities.get(l, 0) for l in lines) * num_days
    total_demand = 0
    for g in grades:
        for d in range(num_days):
            total_demand += int(demand.get(g, {}).get(dates[d], 0))
    if total_demand > total_capacity:
        issues.append(f"TOTAL_DEMAND ({total_demand}) > TOTAL_CAPACITY ({total_capacity})")

    # 2) Per-day capacity check: any day demand > sum line capacities?
    for d in range(num_days):
        day_demand = sum(int(demand.get(g, {}).get(dates[d], 0)) for g in grades)
        day_capacity = sum(capacities.get(l, 0) for l in lines)
        if day_demand > day_capacity:
            issues.append(f"DAY_{d}_DEMAND ({day_demand}) > DAY_CAPACITY ({day_capacity})")

    # 3) Min-run > feasible blocks: check if any (grade,line) has min_run greater than available non-shutdown days in horizon
    shutdowns = inputs.get("shutdown_periods", {})
    min_run = inputs.get("min_run_days", {})
    for (g,l), mn in min_run.items():
        # count non-shutdown days
        available = sum(1 for d in range(num_days) if not (l in shutdowns and d in shutdowns[l]))
        if mn > available:
            issues.append(f"MIN_RUN_TOO_BIG for {(g,l)}: min_run {mn} > available non-shutdown days {available}")

    # 4) Force start on shutdown or outside horizon
    force = inputs.get("force_start_date", {})
    for (g,l), dt in force.items():
        if dt:
            if dt not in dates:
                issues.append(f"FORCE_START_OUTSIDE_HORIZON {(g,l)} -> {dt}")
            else:
                idx = dates.index(dt)
                if l in shutdowns and idx in shutdowns[l]:
                    issues.append(f"FORCE_START_ON_SHUTDOWN {(g,l)} -> day {idx}")

    # 5) allowed_lines empty for any required grade
    allowed = inputs.get("allowed_lines", {})
    for g in grades:
        if g not in allowed or len(allowed.get(g, [])) == 0:
            issues.append(f"NO_ALLOWED_LINES_FOR_GRADE {g}")

    # 6) Transition matrix causing isolation: if for a grade and line every possible successor is forbidden for all lines/days
    trans = inputs.get("transition_rules", {})
    for l, rules in trans.items():
        for g1, succs in rules.items():
            # if succs empty means no successor allowed after g1 on this line
            if isinstance(succs, (list, tuple, set)) and len(succs) == 0:
                issues.append(f"TRANSITION_NO_SUCCESSORS on line {l} after grade {g1}")

    return issues

def make_builder_with_flags(inputs: Dict[str, Any], params: Dict[str, Any],
                            disable_transitions=False,
                            disable_minrun=False,
                            disable_force_start=False,
                            disable_material_running=False,
                            disable_shutdowns=False):
    """
    Returns a callable that constructs a simplified model using your same inputs,
    but with certain constraint groups disabled for isolation testing.
    The model is intentionally light (bool production only, simplified inventory)
    to make tests fast.
    """
    def builder():
        grades = inputs["grades"]
        lines = inputs["lines"]
        dates = inputs["dates"]
        num_days = inputs["num_days"]
        capacities = inputs["capacities"]
        demand = inputs["demand_data"]
        initial_inv = inputs.get("initial_inventory", {})
        min_run = inputs.get("min_run_days", {})
        force_start = inputs.get("force_start_date", {})
        shutdowns = inputs.get("shutdown_periods", {})
        transitions_allowed = inputs.get("transition_rules", {})
        matinfo = inputs.get("material_running_info", {})

        model = cp_model.CpModel()
        # simplified variables: is_prod only
        is_prod = {}
        for g in grades:
            for l in lines:
                for d in range(num_days):
                    is_prod[(g,l,d)] = model.NewBoolVar(f"is_{g}_{l}_{d}")

        # enforce allowed_lines
        allowed = inputs.get("allowed_lines", {})
        for g in grades:
            for l in lines:
                if l not in allowed.get(g, []):
                    for d in range(num_days):
                        model.Add(is_prod[(g,l,d)] == 0)

        # capacity: at most one grade per line per day and sum of production existence <= number of lines producing
        for l in lines:
            for d in range(num_days):
                # one grade per line
                model.Add(sum(is_prod[(g,l,d)] for g in grades) <= 1)
                # if shutdowns disabled => ignore, else forbid all if shutdown day
                if (not disable_shutdowns) and (l in shutdowns and d in shutdowns[l]):
                    for g in grades:
                        model.Add(is_prod[(g,l,d)] == 0)

        # force_start
        if not disable_force_start:
            for (g,l), dt in force_start.items():
                if dt and dt in dates:
                    idx = dates.index(dt)
                    if (g,l,idx) in is_prod:
                        model.Add(is_prod[(g,l,idx)] == 1)

        # material running
        if not disable_material_running:
            for plant, tup in matinfo.items():
                material, exp = tup
                for d in range(min(exp, num_days)):
                    if (material, plant, d) in is_prod:
                        model.Add(is_prod[(material, plant, d)] == 1)
                        for other in grades:
                            if other != material and (other, plant, d) in is_prod:
                                model.Add(is_prod[(other, plant, d)] == 0)

        # min run enforcement simplified: if start then next min_run days must be true
        if not disable_minrun:
            # create simple start definition
            for g in grades:
                for l in lines:
                    for d in range(num_days):
                        if (g,l,d) not in is_prod:
                            continue
                        # start if prod now and not previous
                        if d == 0:
                            is_start = is_prod[(g,l,d)]
                        else:
                            is_start = model.NewBoolVar(f"start_{g}_{l}_{d}")
                            model.AddBoolAnd([is_prod[(g,l,d)], is_prod[(g,l,d-1)].Not()]).OnlyEnforceIf(is_start)
                            model.AddBoolOr([is_prod[(g,l,d)].Not(), is_prod[(g,l,d-1)]]).OnlyEnforceIf(is_start.Not())
                        mn = min_run.get((g,l), 1)
                        if mn > 1:
                            seq = []
                            for k in range(d, min(num_days, d + mn)):
                                if not (l in shutdowns and k in shutdowns[l]):
                                    seq.append(is_prod[(g,l,k)])
                            if len(seq) >= mn:
                                model.Add(sum(seq) >= mn).OnlyEnforceIf(is_start)

        # transitions
        if not disable_transitions:
            for l in lines:
                for d in range(num_days - 1):
                    # forbid explicitly disallowed pairs
                    rules = transitions_allowed.get(l, {})
                    for g1 in grades:
                        for g2 in grades:
                            if g1 == g2: 
                                continue
                            if g1 in rules and g2 not in rules[g1]:
                                model.Add(is_prod[(g1,l,d)] + is_prod[(g2,l,d+1)] <= 1)

        # Very simplified demand constraint: ensure per-grade demand can be produced across all lines and days
        # We'll enforce that for each grade, sum(is_prod over lines and days) >= 0 if demand > 0
        # (We avoid complicated production quantities for speed; this is only a feasibility probe)
        for g in grades:
            total_required = sum(int(demand.get(g, {}).get(dates[d], 0)) for d in range(num_days))
            if total_required > 0:
                # require at least one boolean (this is a weak check; we leave quantity logic to full solver)
                model.Add(sum(is_prod[(g,l,d)] for l in lines for d in range(num_days)) >= 0)

        return model, {"is_prod": is_prod}

    return builder

def debug_find_cause(inputs: Dict[str,Any], params: Dict[str,Any]):
    print("Running input validation checks...")
    issues = validate_inputs_simple(inputs)
    if issues:
        print("Pre-check issues found:")
        for it in issues:
            print(" -", it)
    else:
        print("No obvious pre-check issues found.")

    tests = [
        ("base", {}),
        ("no_transitions", {"disable_transitions": True}),
        ("no_minrun", {"disable_minrun": True}),
        ("no_force_start", {"disable_force_start": True}),
        ("no_material_running", {"disable_material_running": True}),
        ("no_shutdowns", {"disable_shutdowns": True}),
        ("disable_transitions_and_minrun", {"disable_transitions": True, "disable_minrun": True}),
    ]

    results = {}
    for name, flags in tests:
        print(f"\nTest: {name}  — flags={flags}")
        builder = make_builder_with_flags(inputs, params, **flags)
        ok, status = quick_feasibility_test(builder, time_limit_sec=5)
        results[name] = (ok, status)
        print(f" -> Feasible? {ok}  status={status}")

    print("\nSummary of tests:")
    for k,v in results.items():
        print(f" {k}: Feasible={v[0]}, status={v[1]}")

    print("\nInterpretation hints:")
    print(" - If disabling transitions makes it feasible, transition_rules are over-restrictive.")
    print(" - If disabling minrun makes it feasible, min_run windows are too strict (or min_run > available non-shutdown days).")
    print(" - If disabling force_start makes it feasible, a forced start conflicts with shutdowns/allowed lines.")
    print(" - If disabling material running makes it feasible, material_running_info imposes impossible fixed production days.")
    print(" - If disabling shutdowns makes it feasible, shutdown placement conflicts with run-length or forced starts.")

    return results

# If you want to test locally:
# from solver_debug import debug_find_cause
# res = debug_find_cause(inputs, params)
# print(res)
