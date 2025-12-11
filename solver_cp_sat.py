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
    """Build and solve the CP-SAT model (enhanced).

    Behaviour highlights:
      - material_running_info: dict[line] = (grade, expected_days) or grade (no days)
      - expected_days > 0: force days [0..expected_days-1] then mandatory changeover on day expected_days
      - expected_days == 0 or None: only day 0 is forced, solver may extend
      - rerun_allowed[(grade,line)] == False: grade can start at most once on that line (forced block counts as start)
      - penalty_method: "Standard" or "Ensure All Grades' Production"
    """
    if progress_callback:
        progress_callback(0.0, "Building optimization model...")

    model = cp_model.CpModel()

    # ---- Decision variables ----
    is_producing = {}
    production = {}

    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])

    # Create variables (only for allowed grade-line combos)
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                production_value = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                model.Add(production_value == capacities[line]).OnlyEnforceIf(is_producing[key])
                model.Add(production_value == 0).OnlyEnforceIf(is_producing[key].Not())
                production[key] = production_value

    def get_production_var(grade, line, d):
        return production.get((grade, line, d), 0)

    def get_is_producing_var(grade, line, d):
        return is_producing.get((grade, line, d), None)

    if progress_callback:
        progress_callback(0.1, "Adding hard constraints...")

    # --------------------------
    # HARD CONSTRAINTS
    # --------------------------

    # 1) Shutdown: no production on shutdown days
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        key = (grade, line, d)
                        if key in is_producing:
                            model.Add(is_producing[key] == 0)
                            model.Add(production[key] == 0)

    # 2) At most one grade per line per day
    for line in lines:
        for d in range(num_days):
            producing_vars = []
            for grade in grades:
                if is_allowed_combination(grade, line):
                    var = get_is_producing_var(grade, line, d)
                    if var is not None:
                        producing_vars.append(var)
            if producing_vars:
                model.Add(sum(producing_vars) <= 1)

    # 3) Material running handling (force day 0 and optionally a forced block)
    # Build material_running_map: line -> {'material': grade, 'expected_days': k}
    material_running_map = {}
    for plant, info in material_running_info.items():
        try:
            material, expected_days = info
        except Exception:
            material = info if isinstance(info, str) else None
            expected_days = None

        if material is None:
            continue

        # Force day 0 if allowed
        if is_allowed_combination(material, plant):
            v0 = get_is_producing_var(material, plant, 0)
            if v0 is not None:
                model.Add(v0 == 1)
            # force others 0 on day 0
            for other in grades:
                if other != material and is_allowed_combination(other, plant):
                    ov = get_is_producing_var(other, plant, 0)
                    if ov is not None:
                        model.Add(ov == 0)

        # If expected_days is positive integer, force days [0..expected_days-1]
        forced_days = 0
        if expected_days is not None and isinstance(expected_days, int) and expected_days > 0:
            forced_days = min(expected_days, num_days)
            for d in range(1, forced_days):
                if d < num_days and is_allowed_combination(material, plant):
                    v = get_is_producing_var(material, plant, d)
                    if v is not None:
                        model.Add(v == 1)
                    # force other grades 0 on those days
                    for other in grades:
                        if other != material and is_allowed_combination(other, plant):
                            ov = get_is_producing_var(other, plant, d)
                            if ov is not None:
                                model.Add(ov == 0)

            # mandatory changeover on day forced_days (if within horizon)
            if forced_days < num_days:
                # forbid same material on day forced_days
                next_var = get_is_producing_var(material, plant, forced_days)
                if next_var is not None:
                    model.Add(next_var == 0)
                # if possible, require at least one alternative grade on that day (avoid leaving capacity unfilled)
                alternatives = []
                for other in grades:
                    if other != material and is_allowed_combination(other, plant):
                        alt_v = get_is_producing_var(other, plant, forced_days)
                        if alt_v is not None:
                            alternatives.append(alt_v)
                if alternatives:
                    model.Add(sum(alternatives) >= 1)
            material_running_map[plant] = {'material': material, 'expected_days': forced_days}
        else:
            # expected_days is 0/None -> only day 0 forced; mark expected_days = 0
            material_running_map[plant] = {'material': material, 'expected_days': 0}

    # 4) Pre-shutdown (day before must produce specific grade) & restart (day after)
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            shutdown_days = shutdown_periods[line]
            if line in pre_shutdown_grades and pre_shutdown_grades[line]:
                pre_g = pre_shutdown_grades[line]
                if pre_g in grades and is_allowed_combination(pre_g, line):
                    day_before = shutdown_days[0] - 1
                    if day_before >= 0:
                        v = get_is_producing_var(pre_g, line, day_before)
                        if v is not None:
                            model.Add(v == 1)
                        for other in grades:
                            if other != pre_g and is_allowed_combination(other, line):
                                ov = get_is_producing_var(other, line, day_before)
                                if ov is not None:
                                    model.Add(ov == 0)
            if line in restart_grades and restart_grades[line]:
                restart_g = restart_grades[line]
                if restart_g in grades and is_allowed_combination(restart_g, line):
                    day_after = shutdown_days[-1] + 1
                    if day_after < num_days:
                        v = get_is_producing_var(restart_g, line, day_after)
                        if v is not None:
                            model.Add(v == 1)
                        for other in grades:
                            if other != restart_g and is_allowed_combination(other, line):
                                ov = get_is_producing_var(other, line, day_after)
                                if ov is not None:
                                    model.Add(ov == 0)

    if progress_callback:
        progress_callback(0.2, "Adding inventory constraints...")

    # --------------------------
    # INVENTORY / STOCKOUT VARIABLES & BALANCE
    # --------------------------
    inventory_vars = {}
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 1000000, f'inventory_{grade}_{d}')

    stockout_vars = {}
    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 1000000, f'stockout_{grade}_{d}')

    # initial inventory (opening inventory) is hard constraint
    for grade in grades:
        init_val = int(initial_inventory.get(grade, 0))
        model.Add(inventory_vars[(grade, 0)] == init_val)

    # daily inventory balance
    for grade in grades:
        for d in range(num_days):
            produced_today = sum(get_production_var(grade, line, d) for line in allowed_lines.get(grade, []))
            demand_today = int(demand_data[grade].get(dates[d], 0))
            available = model.NewIntVar(0, 1000000, f'available_{grade}_{d}')
            model.Add(available == inventory_vars[(grade, d)] + produced_today)

            supplied = model.NewIntVar(0, 1000000, f'supplied_{grade}_{d}')
            enough_inventory = model.NewBoolVar(f'enough_{grade}_{d}')

            model.Add(available >= demand_today).OnlyEnforceIf(enough_inventory)
            model.Add(available < demand_today).OnlyEnforceIf(enough_inventory.Not())

            model.Add(supplied == demand_today).OnlyEnforceIf(enough_inventory)
            model.Add(supplied == available).OnlyEnforceIf(enough_inventory.Not())

            stockout = stockout_vars[(grade, d)]
            model.Add(stockout == demand_today - supplied)

            # update inventory next day
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)

    # 5) max inventory hard constraint
    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= int(max_inventory.get(grade, 1_000_000)))

    if progress_callback:
        progress_callback(0.3, "Adding capacity & run constraints...")

    # 6) Full capacity utilization (hard) except shutdown days
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            production_vars = [get_production_var(g, line, d) for g in grades if is_allowed_combination(g, line)]
            if production_vars:
                model.Add(sum(production_vars) == capacities[line])

    # 7) Force start date (hard)
    for (grade, plant), start_date in force_start_date.items():
        if start_date:
            try:
                start_idx = dates.index(start_date)
                var = get_is_producing_var(grade, plant, start_idx)
                if var is not None:
                    model.Add(var == 1)
            except ValueError:
                # ignore if date outside horizon
                pass

    # 8) Min/Max run days
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            key = (grade, line)
            min_run = int(min_run_days.get(key, 1))
            max_run = int(max_run_days.get(key, 9999))

            # Ensure expected_run_days does not violate max_run (validation)
            if line in material_running_map:
                mat_info = material_running_map[line]
                if mat_info['material'] == grade and mat_info['expected_days'] > max_run:
                    # Strictly: this is inconsistent input — prefer to raise early (but here we add a safeguard)
                    # Force the expected block but still enforce max_run thereafter; solver may be infeasible if contradictory.
                    pass

            # MIN RUN DAYS: applies to new runs (excluding continuation of forced material block)
            for d in range(num_days):
                # skip days inside forced material block for this grade/line
                in_material_block = False
                if line in material_running_map:
                    mat = material_running_map[line]
                    if mat['material'] == grade and d < mat['expected_days']:
                        in_material_block = True
                if in_material_block:
                    continue

                prod_today = get_is_producing_var(grade, line, d)
                if prod_today is None:
                    continue

                # define start indicator
                if d == 0:
                    # if day 0 forced material and that material=grade, treat it as a start (so rerun logic counts it)
                    if line in material_running_map and material_running_map[line]['material'] == grade:
                        starts_new_run = prod_today  # day 0 forced block counts as start
                    else:
                        starts_new_run = prod_today
                else:
                    prod_yesterday = get_is_producing_var(grade, line, d - 1)
                    if prod_yesterday is None:
                        continue
                    starts_new_run = model.NewBoolVar(f'starts_{grade}_{line}_{d}')
                    model.Add(starts_new_run <= prod_today)
                    model.Add(starts_new_run <= 1 - prod_yesterday)
                    model.Add(starts_new_run >= prod_today - prod_yesterday)

                # enforce min_run: if starts_new_run == 1 then next min_run days must be producing (unless out of horizon or shutdown)
                if isinstance(starts_new_run, cp_model.IntVar) or isinstance(starts_new_run, cp_model.BoolVar):
                    valid = True
                    run_vars = []
                    for off in range(min_run):
                        day_idx = d + off
                        if day_idx >= num_days:
                            valid = False
                            break
                        if line in shutdown_periods and day_idx in shutdown_periods[line]:
                            valid = False
                            break
                        v = get_is_producing_var(grade, line, day_idx)
                        if v is None:
                            valid = False
                            break
                        run_vars.append(v)
                    if valid and run_vars:
                        for v in run_vars:
                            model.Add(v == 1).OnlyEnforceIf(starts_new_run)

            # MAX RUN: cannot have max_run+1 consecutive days producing same grade
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
                        v = get_is_producing_var(grade, line, idx)
                        if v is None:
                            ok = False
                            break
                        seq.append(v)
                    if ok and len(seq) == max_run + 1:
                        model.Add(sum(seq) <= max_run)

    if progress_callback:
        progress_callback(0.5, "Adding transition & rerun constraints...")

    # 9) Forbidden transitions (hard)
    for line in lines:
        if transition_rules.get(line):
            for d in range(num_days - 1):
                for prev_g in grades:
                    if prev_g in transition_rules[line] and is_allowed_combination(prev_g, line):
                        allowed_next = transition_rules[line][prev_g]
                        for curr_g in grades:
                            if curr_g != prev_g and curr_g not in allowed_next and is_allowed_combination(curr_g, line):
                                prev_var = get_is_producing_var(prev_g, line, d)
                                curr_var = get_is_producing_var(curr_g, line, d + 1)
                                if prev_var is not None and curr_var is not None:
                                    model.Add(prev_var + curr_var <= 1)

    # 10) Rerun allowed constraints (hard)
    # If rerun_allowed[(grade,line)] == False: grade may start at most once on that line.
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            key = (grade, line)
            if not rerun_allowed.get(key, True):
                start_indicators = []
                # day 0: if produced on day0 -> it counts as start (including forced material block)
                v0 = get_is_producing_var(grade, line, 0)
                if v0 is not None:
                    start_indicators.append(v0)
                for d in range(1, num_days):
                    # don't skip forced block days: they are valid starts (we already counted day0)
                    py = get_is_producing_var(grade, line, d - 1)
                    pt = get_is_producing_var(grade, line, d)
                    if py is None or pt is None:
                        continue
                    start = model.NewBoolVar(f'rerun_start_{grade}_{line}_{d}')
                    model.Add(start <= pt)
                    model.Add(start <= 1 - py)
                    model.Add(start >= pt - py)
                    start_indicators.append(start)
                if start_indicators:
                    # allow at most 1 start (this enforces "produced at most once")
                    model.Add(sum(start_indicators) <= 1)

                # Extra tight enforcement: if grade had a forced block at start and rerun is False,
                # ban the grade for all days after the forced block:
                if line in material_running_map:
                    mat = material_running_map[line]
                    if mat['material'] == grade and mat['expected_days'] > 0:
                        for d in range(mat['expected_days'], num_days):
                            v = get_is_producing_var(grade, line, d)
                            if v is not None:
                                model.Add(v == 0)

    if progress_callback:
        progress_callback(0.6, "Adding soft constraints & objective...")

    # --------------------------
    # SOFT CONSTRAINTS -> Objective
    # --------------------------
    objective_terms = []
    demand_days = max(0, num_days - buffer_days)

    # Precompute grade demand stats
    total_demand_per_grade = {}
    for g in grades:
        total_demand_per_grade[g] = sum(demand_data[g].get(dates[d], 0) for d in range(num_days))
    global_total_demand = sum(total_demand_per_grade.values()) if total_demand_per_grade else 0.0
    max_grade_demand = max((v for v in total_demand_per_grade.values() if v > 0), default=1.0)

    # STOCKOUT penalties
    if penalty_method == "Ensure All Grades' Production":
        # fairness_scale = global_total / grade_total
        for g in grades:
            gd = total_demand_per_grade.get(g, 0)
            if gd <= 0:
                continue
            fairness_scale = (global_total_demand / gd) if gd > 0 else 1.0
            per_unit_pen = max(1, int(stockout_penalty * fairness_scale))
            for d in range(num_days):
                if (g, d) in stockout_vars:
                    objective_terms.append(per_unit_pen * stockout_vars[(g, d)])
    else:
        # STANDARD mode: dynamic urgency + day-weighting
        urgency_multiplier = 2.0
        for g in grades:
            total = total_demand_per_grade.get(g, 0)
            inv = max(1.0, float(initial_inventory.get(g, 0)))
            urgency = max(1.0, (total / inv))  # >=1.0
            for d in range(num_days):
                if (g, d) not in stockout_vars:
                    continue
                day_weight = 1.0 + urgency_multiplier * ((num_days - 1 - d) / max(1, num_days - 1))
                per_unit = max(1, int(stockout_penalty * urgency * day_weight))
                objective_terms.append(per_unit * stockout_vars[(g, d)])

    # MINIMUM DAILY / CLOSING INVENTORY penalties (soft)
    for (g, d), deficit_var in {}.items():  # placeholder: we build below
        pass
    # Build inventory deficit penalty variables earlier (we already had them in previous version),
    # but for clarity: compute them here by reusing variables created earlier in original code.
    # Inventory deficit variables were already created as inventory_deficit_penalties and closing_inventory_deficit_penalties.
    # If not present, create them now:
    inventory_deficit_penalties = {}
    closing_inventory_deficit_penalties = {}

    # min inventory per day (soft)
    for g in grades:
        for d in range(num_days):
            min_inv = int(min_inventory.get(g, 0))
            if min_inv > 0:
                inv_tom = inventory_vars[(g, d + 1)]
                deficit = model.NewIntVar(0, 1000000, f'inv_deficit_{g}_{d}')
                model.Add(deficit >= min_inv - inv_tom)
                model.Add(deficit >= 0)
                inventory_deficit_penalties[(g, d)] = deficit
                # penalty coefficient: use stockout_penalty as base
                if penalty_method == "Ensure All Grades' Production":
                    # scale by demand proportion
                    daily_d = demand_data[g].get(dates[d], 0)
                    scale = (global_total_demand / daily_d) if daily_d > 0 else 1.0
                    coeff = max(1, int(stockout_penalty * 1 * scale))
                else:
                    coeff = stockout_penalty
                objective_terms.append(coeff * deficit)

        # closing inventory (soft)
        if int(min_closing_inventory.get(g, 0)) > 0 and buffer_days > 0:
            closing_day_idx = max(0, num_days - buffer_days)
            closing_inv = inventory_vars[(g, closing_day_idx)]
            closing_def = model.NewIntVar(0, 1000000, f'closing_def_{g}')
            model.Add(closing_def >= int(min_closing_inventory[g]) - closing_inv)
            model.Add(closing_def >= 0)
            closing_inventory_deficit_penalties[g] = closing_def
            coeff = stockout_penalty * 3
            objective_terms.append(coeff * closing_def)

    # TRANSITION penalties (soft, adaptive)
    # We'll create explicit transition variables and tie them to production variables.
    # Build a dictionary transition_vars[(line,d,g1,g2)] = BoolVar
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
                        # adaptive penalty: scale by average demand of the two grades
                        d1 = total_demand_per_grade.get(g1, 0)
                        d2 = total_demand_per_grade.get(g2, 0)
                        avg_d = (d1 + d2) / 2.0 if (d1 + d2) > 0 else 1.0
                        scale = 1.0 + 5.0 * (avg_d / max_grade_demand)  # 1x..6x roughly
                        scaled_pen = max(1, int(transition_penalty * scale))
                        objective_terms.append(scaled_pen * tvar)

    # Idle line penalty (not generally reachable because of full-capacity constraint); kept low
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

    # Finalize objective
    if objective_terms:
        model.Minimize(sum(objective_terms))
    else:
        model.Minimize(0)

    if progress_callback:
        progress_callback(0.8, "Solving optimization problem...")

    # Solve (with callback that collects solutions)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(1.0, float(time_limit_min) * 60.0)
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED
    # log_search_progress is useful for debug; keep True for traceability
    solver.parameters.log_search_progress = True

    # build SolutionCallback with penalty maps for reporting
    solution_callback = SolutionCallback(
        production, inventory_vars, stockout_vars, is_producing,
        grades, lines, dates, formatted_dates, num_days,
        inventory_deficit_penalties, closing_inventory_deficit_penalties,
        buffer_days=buffer_days
    )

    status = solver.Solve(model, solution_callback)

    if progress_callback:
        progress_callback(1.0, "Optimization complete!")

    return status, solution_callback, solver
