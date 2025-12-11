""" 
Working Code of
CP-SAT Solver for production optimization
"""
from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED
import math

class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Callback to capture all solutions during search"""
    def __init__(self, production, inventory, stockout, is_producing, grades, lines, dates, formatted_dates, num_days,
                 inventory_deficit_penalties=None, closing_inventory_deficit_penalties=None, buffer_days: int = 0):
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
        self.buffer_days = max(0, buffer_days)
        self.inventory_deficit_penalties = inventory_deficit_penalties or {}
        self.closing_inventory_deficit_penalties = closing_inventory_deficit_penalties or {}
        self.solutions = []
        self.solution_times = []
        self.start_time = time.time()
        self.objective_breakdowns = []

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

        # Store production data
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

        # Store inventory data - OPENING inventory for each day
        for grade in self.grades:
            solution['inventory'][grade] = {}
            # First date gets initial inventory
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.inventory:
                    # Map inventory at day d to the date for day d
                    # inventory_vars[(grade, d)] = opening inventory for day d
                    solution['inventory'][grade][self.formatted_dates[d]] = self.Value(self.inventory[key])
            # Store final closing inventory separately
            final_key = (grade, self.num_days)
            if final_key in self.inventory:
                solution['inventory'][grade]['final'] = self.Value(self.inventory[final_key])

        # Store stockout data
        for grade in self.grades:
            solution['stockout'][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.stockout:
                    value = self.Value(self.stockout[key])
                    if value > 0:
                        solution['stockout'][grade][self.formatted_dates[d]] = value

        # Store production schedule
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

        # Count transitions (only within demand period; exclude buffer days)
        demand_days = max(0, self.num_days - self.buffer_days)
        transition_count_per_line = {line: 0 for line in self.lines}
        total_transitions = 0
        for line in self.lines:
            last_grade = None
            for d in range(demand_days):
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

        # Calculate objective breakdown
        breakdown = self.calculate_objective_breakdown(current_obj)
        solution['objective_breakdown'] = breakdown
        self.objective_breakdowns.append(breakdown)
        self.solutions.append(solution)

    def calculate_objective_breakdown(self, solver_objective):
        """Calculate detailed breakdown of the objective value"""
        breakdown = {
            'stockout': 0,
            'transitions': 0,
            'solver_objective': solver_objective,
            'calculated_total': 0
        }
        return breakdown

    def num_solutions(self):
        return len(self.solutions)


def build_and_solve_model(
    grades: List[str],
    lines: List[str],
    dates: List,
    formatted_dates: List[str],
    num_days: int,
    capacities: Dict,
    initial_inventory: Dict,
    min_inventory: Dict,
    max_inventory: Dict,
    min_closing_inventory: Dict,
    demand_data: Dict,
    allowed_lines: Dict,
    min_run_days: Dict,
    max_run_days: Dict,
    force_start_date: Dict,
    rerun_allowed: Dict,
    material_running_info: Dict,
    shutdown_periods: Dict,
    pre_shutdown_grades: Dict,
    restart_grades: Dict,
    transition_rules: Dict,
    buffer_days: int,
    stockout_penalty: int,
    transition_penalty: int,
    time_limit_min: int,
    penalty_method: str = "Standard",
    progress_callback=None
) -> Tuple[int, SolutionCallback, cp_model.CpSolver]:
    """
    Enhanced CP-SAT model builder and solver.

    Key behaviors:
    - material_running_info: dict[line] = (grade, expected_days) or dict[line] = grade
      * expected_days > 0: force days 0..expected_days-1, enforce changeover at expected_days,
        and if rerun_allowed[(grade,line)] == False, ban the grade for rest of horizon.
      * expected_days == 0 or None: only day 0 forced; solver may extend.
    - rerun_allowed[(grade,line)] == False => grade can start at most once on that line.
    - penalty_method: "Standard" or "Ensure All Grades' Production"
        * Standard: urgency/day-weighted stockout penalties.
        * Ensure All Grades' Production: minimax relative-stockout objective.
    """

    if progress_callback:
        progress_callback(0.0, "Building optimization model...")

    model = cp_model.CpModel()

    # Helper: check allowed combination
    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])

    # ---------------------
    # Decision variables
    # ---------------------
    is_producing = {}    # (grade,line,d) -> BoolVar
    production = {}      # (grade,line,d) -> IntVar

    for grade in grades:
        for line in allowed_lines.get(grade, []):
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                production[key] = model.NewIntVar(0, int(capacities[line]), f'production_{grade}_{line}_{d}')
                # full capacity or zero
                model.Add(production[key] == int(capacities[line])).OnlyEnforceIf(is_producing[key])
                model.Add(production[key] == 0).OnlyEnforceIf(is_producing[key].Not())

    def get_is_producing_var(grade, line, d):
        return is_producing.get((grade, line, d), None)

    def get_production_var(grade, line, d):
        return production.get((grade, line, d), 0)

    if progress_callback:
        progress_callback(0.1, "Adding hard constraints...")

    # ---------------------
    # HARD CONSTRAINTS
    # ---------------------

    # Shutdowns: no production on shutdown days
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        var = get_is_producing_var(grade, line, d)
                        prod_var = production.get((grade, line, d))
                        if var is not None:
                            model.Add(var == 0)
                        if prod_var is not None:
                            model.Add(prod_var == 0)

    # One grade per line per day
    for line in lines:
        for d in range(num_days):
            vars_for_day = []
            for grade in grades:
                if is_allowed_combination(grade, line):
                    v = get_is_producing_var(grade, line, d)
                    if v is not None:
                        vars_for_day.append(v)
            if vars_for_day:
                model.Add(sum(vars_for_day) <= 1)

    # Material running handling: force day 0 and optional forced block
    # Build material_running_map: line -> {'material': grade, 'expected_days': k}
    material_running_map = {}
    for plant, info in material_running_info.items():
        # accept either (grade, expected_days) or just grade
        if isinstance(info, (list, tuple)) and len(info) >= 1:
            material = info[0]
            expected_days = int(info[1]) if len(info) > 1 and info[1] is not None else None
        else:
            material = info
            expected_days = None

        if material is None:
            continue

        # Force day 0 if allowed
        if is_allowed_combination(material, plant):
            v0 = get_is_producing_var(material, plant, 0)
            if v0 is not None:
                model.Add(v0 == 1)
            # force other grades 0 on day 0
            for other in grades:
                if other != material and is_allowed_combination(other, plant):
                    ov = get_is_producing_var(other, plant, 0)
                    if ov is not None:
                        model.Add(ov == 0)

        # If expected_days > 0, force continuation for that many days (0..expected_days-1)
        forced_days = 0
        if expected_days is not None and isinstance(expected_days, int) and expected_days > 0:
            forced_days = min(expected_days, num_days)
            for d in range(1, forced_days):
                if d < num_days and is_allowed_combination(material, plant):
                    v = get_is_producing_var(material, plant, d)
                    if v is not None:
                        model.Add(v == 1)
                    # force others 0 on forced days
                    for other in grades:
                        if other != material and is_allowed_combination(other, plant):
                            ov = get_is_producing_var(other, plant, d)
                            if ov is not None:
                                model.Add(ov == 0)

            # mandatory changeover on day forced_days (if within horizon)
            if forced_days < num_days:
                next_var = get_is_producing_var(material, plant, forced_days)
                if next_var is not None:
                    model.Add(next_var == 0)
                # require at least one alternative if exists
                alt_vars = []
                for other in grades:
                    if other != material and is_allowed_combination(other, plant):
                        av = get_is_producing_var(other, plant, forced_days)
                        if av is not None:
                            alt_vars.append(av)
                if alt_vars:
                    model.Add(sum(alt_vars) >= 1)
        else:
            forced_days = 0

        material_running_map[plant] = {'material': material, 'expected_days': forced_days}

    # Pre-shutdown and restart constraints (forced grade before/after shutdown)
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            sd = shutdown_periods[line]
            # pre-shutdown
            if line in pre_shutdown_grades and pre_shutdown_grades[line]:
                pre_g = pre_shutdown_grades[line]
                day_before = sd[0] - 1
                if day_before >= 0 and pre_g in grades and is_allowed_combination(pre_g, line):
                    v = get_is_producing_var(pre_g, line, day_before)
                    if v is not None:
                        model.Add(v == 1)
                    for other in grades:
                        if other != pre_g and is_allowed_combination(other, line):
                            ov = get_is_producing_var(other, line, day_before)
                            if ov is not None:
                                model.Add(ov == 0)
            # restart
            if line in restart_grades and restart_grades[line]:
                rest_g = restart_grades[line]
                day_after = sd[-1] + 1
                if day_after < num_days and rest_g in grades and is_allowed_combination(rest_g, line):
                    v = get_is_producing_var(rest_g, line, day_after)
                    if v is not None:
                        model.Add(v == 1)
                    for other in grades:
                        if other != rest_g and is_allowed_combination(other, line):
                            ov = get_is_producing_var(other, line, day_after)
                            if ov is not None:
                                model.Add(ov == 0)

    if progress_callback:
        progress_callback(0.2, "Adding inventory constraints...")

    # ---------------------
    # INVENTORY & STOCKOUT
    # ---------------------
    inventory_vars = {}
    for g in grades:
        for d in range(num_days + 1):
            inventory_vars[(g, d)] = model.NewIntVar(0, 10**9, f'inventory_{g}_{d}')

    stockout_vars = {}
    for g in grades:
        for d in range(num_days):
            stockout_vars[(g, d)] = model.NewIntVar(0, 10**9, f'stockout_{g}_{d}')

    # Opening inventory (hard)
    for g in grades:
        init_val = int(initial_inventory.get(g, 0))
        model.Add(inventory_vars[(g, 0)] == init_val)

    # Daily balance
    for g in grades:
        for d in range(num_days):
            produced = sum(get_production_var(g, line, d) for line in allowed_lines.get(g, []))
            demand_today = int(demand_data[g].get(dates[d], 0))
            avail = model.NewIntVar(0, 10**9, f'avail_{g}_{d}')
            model.Add(avail == inventory_vars[(g, d)] + produced)

            supplied = model.NewIntVar(0, 10**9, f'supplied_{g}_{d}')
            enough = model.NewBoolVar(f'enough_{g}_{d}')
            model.Add(avail >= demand_today).OnlyEnforceIf(enough)
            model.Add(avail < demand_today).OnlyEnforceIf(enough.Not())
            model.Add(supplied == demand_today).OnlyEnforceIf(enough)
            model.Add(supplied == avail).OnlyEnforceIf(enough.Not())

            # stockout = demand - supplied
            model.Add(stockout_vars[(g, d)] == demand_today - supplied)

            # next day inventory
            model.Add(inventory_vars[(g, d + 1)] == inventory_vars[(g, d)] + produced - supplied)
            model.Add(inventory_vars[(g, d + 1)] >= 0)

    # Max inventory hard constraint
    for g in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(g, d)] <= int(max_inventory.get(g, 10**9)))

    if progress_callback:
        progress_callback(0.3, "Adding capacity & run constraints...")

    # Full capacity per line per day (except shutdown)
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            prod_vars = [get_production_var(g, line, d) for g in grades if is_allowed_combination(g, line)]
            if prod_vars:
                model.Add(sum(prod_vars) == int(capacities[line]))

    # Force start date
    for (g, plant), start in force_start_date.items():
        if start:
            try:
                idx = dates.index(start)
                v = get_is_producing_var(g, plant, idx)
                if v is not None:
                    model.Add(v == 1)
            except ValueError:
                pass  # outside horizon

    # ---------------------
    # START INDICATORS & MIN/MAX RUN DAYS (strong enforcement)
    # ---------------------
    start_indicator = {}  # (g,line,d)->BoolVar

    for g in grades:
        for line in allowed_lines.get(g, []):
            key = (g, line)
            min_run = int(min_run_days.get(key, 1))
            max_run = int(max_run_days.get(key, 9999))

            for d in range(num_days):
                prod_today = get_is_producing_var(g, line, d)
                if prod_today is None:
                    continue

                if d == 0:
                    s = model.NewBoolVar(f'start_{g}_{line}_{d}')
                    # day0: s == prod_today (counts as start if produced)
                    model.Add(s <= prod_today)
                    model.Add(s >= prod_today)
                else:
                    prev = get_is_producing_var(g, line, d - 1)
                    if prev is None:
                        continue
                    s = model.NewBoolVar(f'start_{g}_{line}_{d}')
                    model.Add(s <= prod_today)
                    model.Add(s <= 1 - prev)
                    model.Add(s >= prod_today - prev)

                start_indicator[(g, line, d)] = s

                # Enforce min_run hard: if s == 1, next min_run days must be producing (unless invalid)
                if min_run > 1:
                    run_vars = []
                    valid = True
                    for off in range(min_run):
                        idx = d + off
                        if idx >= num_days:
                            valid = False
                            break
                        if line in shutdown_periods and idx in shutdown_periods[line]:
                            valid = False
                            break
                        v = get_is_producing_var(g, line, idx)
                        if v is None:
                            valid = False
                            break
                        run_vars.append(v)
                    if valid and run_vars:
                        for v in run_vars:
                            model.Add(v == 1).OnlyEnforceIf(s)

            # MAX run enforcement: no (max_run+1) consecutive days
            if max_run is not None and max_run < 9999:
                for d in range(num_days - max_run):
                    seq = []
                    ok = True
                    for off in range(max_run + 1):
                        idx = d + off
                        if idx >= num_days:
                            ok = False
                            break
                        if line in shutdown_periods and idx in shutdown_periods[line]:
                            ok = False
                            break
                        v = get_is_producing_var(g, line, idx)
                        if v is None:
                            ok = False
                            break
                        seq.append(v)
                    if ok and len(seq) == max_run + 1:
                        model.Add(sum(seq) <= max_run)

    # Prevent insertion of other grades in min_run windows after starts
    for (g1, line, sday), s_var in list(start_indicator.items()):
        min_run_g1 = int(min_run_days.get((g1, line), 1))
        if min_run_g1 <= 1:
            continue
        for off in range(min_run_g1):
            idx = sday + off
            if idx >= num_days:
                break
            for g2 in grades:
                if g2 == g1 or not is_allowed_combination(g2, line):
                    continue
                v_other = get_is_producing_var(g2, line, idx)
                if v_other is None:
                    continue
                # if s_var == 1 => v_other == 0
                model.Add(v_other == 0).OnlyEnforceIf(s_var)

    if progress_callback:
        progress_callback(0.5, "Adding transition & rerun constraints...")

    # Forbidden transitions (hard)
    for line in lines:
        if transition_rules.get(line):
            for d in range(num_days - 1):
                for prev_g in grades:
                    if prev_g in transition_rules[line] and is_allowed_combination(prev_g, line):
                        allowed_next = transition_rules[line][prev_g]
                        for curr_g in grades:
                            if curr_g != prev_g and curr_g not in allowed_next and is_allowed_combination(curr_g, line):
                                pv = get_is_producing_var(prev_g, line, d)
                                cv = get_is_producing_var(curr_g, line, d + 1)
                                if pv is not None and cv is not None:
                                    model.Add(pv + cv <= 1)

    # Rerun allowed constraints (hard): start count <= 1 if rerun not allowed
    for g in grades:
        for line in allowed_lines.get(g, []):
            key = (g, line)
            if not rerun_allowed.get(key, True):
                starts = []
                # day0
                v0 = get_is_producing_var(g, line, 0)
                if v0 is not None:
                    starts.append(v0)
                for d in range(1, num_days):
                    prev = get_is_producing_var(g, line, d - 1)
                    cur = get_is_producing_var(g, line, d)
                    if prev is None or cur is None:
                        continue
                    s = model.NewBoolVar(f'rerun_start_{g}_{line}_{d}')
                    model.Add(s <= cur)
                    model.Add(s <= 1 - prev)
                    model.Add(s >= cur - prev)
                    starts.append(s)
                if starts:
                    model.Add(sum(starts) <= 1)

                # If material_running forced block at start and rerun disallowed:
                if line in material_running_map:
                    mat = material_running_map[line]
                    if mat['material'] == g and mat['expected_days'] > 0:
                        for d in range(mat['expected_days'], num_days):
                            v = get_is_producing_var(g, line, d)
                            if v is not None:
                                model.Add(v == 0)

    if progress_callback:
        progress_callback(0.6, "Adding soft constraints & building objective...")

    # ---------------------
    # OBJECTIVE (soft constraints)
    # ---------------------
    objective_terms = []

    # Precompute grade-level totals
    total_demand_per_grade = {}
    for g in grades:
        total_demand_per_grade[g] = sum(int(demand_data[g].get(dates[d], 0)) for d in range(num_days))
    global_total_demand = sum(v for v in total_demand_per_grade.values() if v > 0)
    max_grade_demand = max((v for v in total_demand_per_grade.values() if v > 0), default=1.0)

    demand_days = max(0, num_days - buffer_days)

    # Two objective modes
    if penalty_method == "Ensure All Grades' Production":
        # Build total stockouts per grade
        total_stockout_vars = {}
        for g in grades:
            tsum = model.NewIntVar(0, 10**12, f'total_stockout_{g}')
            model.Add(tsum == sum(stockout_vars[(g, d)] for d in range(num_days)))
            total_stockout_vars[g] = tsum

        # Minimax relative-stockout:
        SCALE = 10000  # precision
        max_rel = model.NewIntVar(0, SCALE * 1000000, 'max_relative_stockout')
        # For each grade with positive demand: total_stockout[g] * SCALE <= max_rel * demand_g
        for g in grades:
            dg = int(total_demand_per_grade.get(g, 0))
            if dg <= 0:
                continue
            model.Add(total_stockout_vars[g] * SCALE <= max_rel * dg)

        # secondary: minimize absolute total stockout
        sum_total_stockout = model.NewIntVar(0, 10**14, 'sum_total_stockout')
        model.Add(sum_total_stockout == sum(total_stockout_vars[g] for g in grades))

        # Compose lexicographic objective via big multiplier
        BIG = max(1, int((global_total_demand * SCALE) + 1))
        model.Minimize(max_rel * BIG + sum_total_stockout)

    else:
        # STANDARD mode: per-day urgency-weighted stockout penalties
        urgency_multiplier = 2.0
        for g in grades:
            total = total_demand_per_grade.get(g, 0)
            inv = max(1.0, float(initial_inventory.get(g, 0)))
            urgency = max(1.0, (total / inv))
            for d in range(num_days):
                if (g, d) not in stockout_vars:
                    continue
                day_weight = 1.0 + urgency_multiplier * ((num_days - 1 - d) / max(1, num_days - 1))
                per_unit = max(1, int(stockout_penalty * urgency * day_weight))
                objective_terms.append(per_unit * stockout_vars[(g, d)])

        # Also add sum of daily inventory deficits (min inventory) as soft penalties
        inventory_deficit_penalties = {}
        for g in grades:
            for d in range(num_days):
                min_inv = int(min_inventory.get(g, 0))
                if min_inv <= 0:
                    continue
                inv_tom = inventory_vars[(g, d + 1)]
                deficit = model.NewIntVar(0, 10**12, f'inv_def_{g}_{d}')
                model.Add(deficit >= min_inv - inv_tom)
                model.Add(deficit >= 0)
                inventory_deficit_penalties[(g, d)] = deficit
                objective_terms.append(stockout_penalty * deficit)

        # closing inventory (soft)
        for g in grades:
            min_close = int(min_closing_inventory.get(g, 0))
            if min_close > 0 and buffer_days > 0:
                closing_idx = max(0, num_days - buffer_days)
                closing_inv = inventory_vars[(g, closing_idx)]
                closing_def = model.NewIntVar(0, 10**12, f'closing_def_{g}')
                model.Add(closing_def >= min_close - closing_inv)
                model.Add(closing_def >= 0)
                objective_terms.append(stockout_penalty * 3 * closing_def)

    # TRANSITION penalties (adaptive). Create trans vars and penalties
    transition_vars = {}
    for line in lines:
        for d in range(demand_days - 1):
            for g1 in grades:
                if not is_allowed_combination(g1, line):
                    continue
                for g2 in grades:
                    if g1 == g2 or not is_allowed_combination(g2, line):
                        continue
                    # skip forbidden transitions
                    if transition_rules.get(line) and g1 in transition_rules[line] and g2 not in transition_rules[line][g1]:
                        continue
                    tvar = model.NewBoolVar(f'trans_{line}_{d}_{g1}_to_{g2}')
                    transition_vars[(line, d, g1, g2)] = tvar
                    a = get_is_producing_var(g1, line, d)
                    b = get_is_producing_var(g2, line, d + 1)
                    if a is not None and b is not None:
                        model.Add(tvar <= a)
                        model.Add(tvar <= b)
                        model.Add(tvar >= a + b - 1)
                        # adaptive scale by avg demand
                        d1 = total_demand_per_grade.get(g1, 0)
                        d2 = total_demand_per_grade.get(g2, 0)
                        avg_d = (d1 + d2) / 2.0 if (d1 + d2) > 0 else 1.0
                        scale = 1.0 + 5.0 * (avg_d / max_grade_demand)
                        scaled_pen = max(1, int(transition_penalty * scale))
                        objective_terms.append(scaled_pen * tvar)

    # Idle penalty (kept small; rarely used due to full-capacity)
    idle_penalty = max(1, int(transition_penalty * 0.2))
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            producing_vars = [get_is_producing_var(g, line, d) for g in grades if is_allowed_combination(g, line) and get_is_producing_var(g, line, d) is not None]
            if not producing_vars:
                continue
            idle = model.NewBoolVar(f'idle_{line}_{d}')
            model.Add(sum(producing_vars) == 0).OnlyEnforceIf(idle)
            model.Add(sum(producing_vars) == 1).OnlyEnforceIf(idle.Not())
            objective_terms.append(idle_penalty * idle)

    # If penalty_method was Ensure All Grades, we already set a lexicographic objective
    if penalty_method != "Ensure All Grades' Production":
        if objective_terms:
            model.Minimize(sum(objective_terms))
        else:
            model.Minimize(0)

    if progress_callback:
        progress_callback(0.8, "Solving optimization problem...")

    # ---------------------
    # SOLVE
    # ---------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(1.0, float(time_limit_min) * 60.0)
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED
    solver.parameters.log_search_progress = True

    # Prepare SolutionCallback (keep signature compatible with earlier)
    solution_callback = SolutionCallback(
        production, inventory_vars, stockout_vars, is_producing,
        grades, lines, dates, formatted_dates, num_days,
        inventory_deficit_penalties if 'inventory_deficit_penalties' in locals() else {},
        {} ,  # closing inventory penalties already handled as ad-hoc; callback doesn't need them strictly
        buffer_days=buffer_days
    )

    status = solver.Solve(model, solution_callback)

    if progress_callback:
        progress_callback(1.0, "Optimization complete!")

    return status, solution_callback, solver
