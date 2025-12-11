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
    """Build and solve the optimization model (robust enforcement of expected behaviour)."""
    if progress_callback:
        progress_callback(0.0, "Building optimization model...")

    model = cp_model.CpModel()

    # ---------- Decision variables ----------
    is_producing = {}
    production = {}

    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])

    # production vars: full capacity or zero
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                prod_var = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                # full capacity if producing else 0
                model.Add(prod_var == capacities[line]).OnlyEnforceIf(is_producing[key])
                model.Add(prod_var == 0).OnlyEnforceIf(is_producing[key].Not())
                production[key] = prod_var

    def get_production_var(grade, line, d):
        return production.get((grade, line, d), None)

    def get_is_producing_var(grade, line, d):
        return is_producing.get((grade, line, d), None)

    if progress_callback:
        progress_callback(0.1, "Adding hard constraints...")

    # ---------- HARD: shutdown constraints ----------
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        key = (grade, line, d)
                        if key in is_producing:
                            model.Add(is_producing[key] == 0)
                            model.Add(production[key] == 0)

    # ---------- HARD: one grade per line per day ----------
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

    # ---------- MATERIAL RUNNING: force start block + mandatory changeover ----------
    # material_running_info expected: {line: (material_grade, expected_days_or_None)}
    material_running_map = {}
    for line, info in material_running_info.items():
        # tolerate both (grade, days) tuples or single-grade entries
        material = None
        expected_days = None
        if isinstance(info, (list, tuple)) and len(info) >= 1:
            material = info[0]
            if len(info) > 1:
                expected_days = info[1]
        else:
            material = info

        if material is None:
            continue

        # Force day 0 to produce material if allowed
        if is_allowed_combination(material, line):
            v0 = get_is_producing_var(material, line, 0)
            if v0 is not None:
                model.Add(v0 == 1)
            # force others 0 on day 0
            for other in grades:
                if other != material and is_allowed_combination(other, line):
                    ov = get_is_producing_var(other, line, 0)
                    if ov is not None:
                        model.Add(ov == 0)

        # If expected_days is a positive integer, force days [0..expected_days-1]
        if expected_days is not None:
            try:
                expected_days = int(expected_days)
            except Exception:
                expected_days = None

        if expected_days is not None and expected_days > 0:
            forced_days = min(expected_days, num_days)
            # days 1..forced_days-1 (day0 already forced above)
            for d in range(1, forced_days):
                if d < num_days and is_allowed_combination(material, line):
                    v = get_is_producing_var(material, line, d)
                    if v is not None:
                        model.Add(v == 1)
                    # set other grades to 0 on forced days
                    for other in grades:
                        if other != material and is_allowed_combination(other, line):
                            ov = get_is_producing_var(other, line, d)
                            if ov is not None:
                                model.Add(ov == 0)

            material_running_map[line] = {'material': material, 'expected_days': forced_days}

            # MANDATORY changeover on day forced_days (i.e., day after the forced block)
            end_day = forced_days
            if end_day < num_days:
                # forbid the same material on end_day
                next_same = get_is_producing_var(material, line, end_day)
                if next_same is not None:
                    model.Add(next_same == 0)

                # require at least one other allowed grade on that day (if feasible)
                alt_vars = []
                for other in grades:
                    if other != material and is_allowed_combination(other, line):
                        v_alt = get_is_producing_var(other, line, end_day)
                        if v_alt is not None:
                            alt_vars.append(v_alt)
                # If alternatives exist, require at least one to run (hard changeover)
                if alt_vars:
                    model.Add(sum(alt_vars) >= 1)
                # If no alternatives exist, we already enforced next_same==0; this may cause infeasibility if full-capacity required—user should ensure allowed_lines includes alternatives.
        else:
            # no forced continuation beyond day 0
            material_running_map[line] = {'material': material, 'expected_days': 1 if expected_days == 0 else 0}

    if progress_callback:
        progress_callback(0.2, "Adding inventory constraints...")

    # ---------- INVENTORY VARS ----------
    inventory_vars = {}
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 10**8, f'inventory_{grade}_{d}')

    # Opening inventory (HARD)
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == int(initial_inventory.get(grade, 0)))

    # stockout vars (unmet demand)
    stockout_vars = {}
    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 10**8, f'stockout_{grade}_{d}')

    # supply and available helper vars & inventory balance
    for grade in grades:
        for d in range(num_days):
            # total produced of grade on day d (sum across allowed lines)
            produced_today_terms = []
            for line in allowed_lines.get(grade, []):
                pvar = get_production_var(grade, line, d)
                if pvar is not None:
                    produced_today_terms.append(pvar)
            # model requires an intvar for sum since CP-SAT likes explicit var; create aggregated var
            produced_today = model.NewIntVar(0, 10**8, f'prodsum_{grade}_{d}')
            if produced_today_terms:
                model.Add(produced_today == sum(produced_today_terms))
            else:
                model.Add(produced_today == 0)

            demand_today = int(demand_data.get(grade, {}).get(dates[d], 0))

            # available = opening inventory + produced_today
            available = model.NewIntVar(0, 10**8, f'available_{grade}_{d}')
            model.Add(available == inventory_vars[(grade, d)] + produced_today)

            # supplied = min(available, demand)
            supplied = model.NewIntVar(0, 10**8, f'supplied_{grade}_{d}')
            # constraints to force supplied to be max possible:
            # If available >= demand -> supplied == demand; else supplied == available
            enough = model.NewBoolVar(f'enough_{grade}_{d}')
            model.Add(available >= demand_today).OnlyEnforceIf(enough)
            model.Add(available < demand_today).OnlyEnforceIf(enough.Not())
            model.Add(supplied == demand_today).OnlyEnforceIf(enough)
            model.Add(supplied == available).OnlyEnforceIf(enough.Not())

            # stockout = demand - supplied
            model.Add(stockout_vars[(grade, d)] == demand_today - supplied)
            # inventory update
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)

    # Max inventory (HARD)
    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= int(max_inventory.get(grade, 10**8)))

    if progress_callback:
        progress_callback(0.3, "Adding capacity & run constraints...")

    # ---------- FULL CAPACITY utilization (HARD, except shutdown) ----------
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            prod_vars = []
            for grade in grades:
                if is_allowed_combination(grade, line):
                    pv = get_production_var(grade, line, d)
                    if pv is not None:
                        prod_vars.append(pv)
            if prod_vars:
                model.Add(sum(prod_vars) == capacities[line])

    # ---------- FORCE START DATE (HARD) ----------
    for (grade, plant), start_date in force_start_date.items():
        if start_date:
            try:
                start_idx = dates.index(start_date)
                v = get_is_producing_var(grade, plant, start_idx)
                if v is not None:
                    model.Add(v == 1)
            except ValueError:
                pass

    # ---------- START INDICATORS for rerun enforcement ----------
    # start_indicator[(grade,line,d)] == 1 if production starts at day d (prod_today==1 and prod_yesterday==0 or d==0)
    start_indicators = {}
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            for d in range(num_days):
                prod_today = get_is_producing_var(grade, line, d)
                if prod_today is None:
                    continue
                if d == 0:
                    # day0 start indicator equals prod_today (counts forced start)
                    s = model.NewBoolVar(f'start_{grade}_{line}_{d}')
                    model.Add(s == prod_today)
                    start_indicators[(grade, line, d)] = s
                else:
                    prod_yesterday = get_is_producing_var(grade, line, d - 1)
                    if prod_yesterday is None:
                        continue
                    s = model.NewBoolVar(f'start_{grade}_{line}_{d}')
                    # s <= prod_today ; s <= 1 - prod_yesterday ; s >= prod_today - prod_yesterday
                    model.Add(s <= prod_today)
                    model.Add(s <= prod_yesterday.Not())
                    model.Add(s >= prod_today - prod_yesterday)
                    start_indicators[(grade, line, d)] = s

    # ---------- RERUN_ALLOWED (HARD) ----------
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            key = (grade, line)
            if not rerun_allowed.get(key, True):
                # sum of starts <= 1 (counts forced start too)
                starts = [start_indicators[(grade, line, d)] for d in range(num_days) if (grade, line, d) in start_indicators]
                if starts:
                    model.Add(sum(starts) <= 1)

    # ---------- MIN RUN DAYS (HARD) - apply whenever a start occurs ----------
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            min_run = int(min_run_days.get((grade, line), 1))
            if min_run <= 1:
                continue
            for d in range(num_days):
                if (grade, line, d) not in start_indicators:
                    continue
                start_var = start_indicators[(grade, line, d)]
                # ensure sufficient days exist
                if d + min_run > num_days:
                    # cannot enforce if not enough days remain; skip to avoid out-of-bounds
                    continue
                # build list of prod_vars for the run length
                run_vars = []
                valid = True
                for offset in range(min_run):
                    dd = d + offset
                    # skip if shutdown day
                    if line in shutdown_periods and dd in shutdown_periods[line]:
                        valid = False
                        break
                    pv = get_is_producing_var(grade, line, dd)
                    if pv is None:
                        valid = False
                        break
                    run_vars.append(pv)
                if not valid or len(run_vars) < min_run:
                    continue
                # If start_var==1 then all run_vars must be 1
                for rv in run_vars:
                    model.Add(rv == 1).OnlyEnforceIf(start_var)

    # ---------- MAX RUN DAYS (HARD) ----------
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            max_run = int(max_run_days.get((grade, line), 9999))
            if max_run < 1:
                continue
            # sliding window of length max_run+1 cannot be all ones
            for d in range(0, num_days - max_run):
                window = []
                valid = True
                for offset in range(max_run + 1):
                    dd = d + offset
                    if line in shutdown_periods and dd in shutdown_periods[line]:
                        valid = False
                        break
                    pv = get_is_producing_var(grade, line, dd)
                    if pv is None:
                        valid = False
                        break
                    window.append(pv)
                if not valid or len(window) < (max_run + 1):
                    continue
                model.Add(sum(window) <= max_run)

    # ---------- If RERUN_ALLOWED == False AND material_running forced, forbid future production after forced block ----------
    for line, info in material_running_map.items():
        mat = info['material']
        forced_days = info['expected_days']
        key = (mat, line)
        # if rerun not allowed, forbid mat on all days >= forced_days
        if not rerun_allowed.get(key, True):
            for d in range(forced_days, num_days):
                pv = get_is_producing_var(mat, line, d)
                if pv is not None:
                    model.Add(pv == 0)

    if progress_callback:
        progress_callback(0.5, "Adding transition constraints...")

    # ---------- FORBIDDEN transitions (HARD) ----------
    # transition_rules: {line: {prev_grade: [allowed_next_grades]}} or matrix with "No" meaning forbidden
    for line in lines:
        rules_for_line = transition_rules.get(line, {})
        for d in range(num_days - 1):
            for prev in grades:
                if prev in rules_for_line:
                    allowed_next = rules_for_line[prev]
                    for curr in grades:
                        if curr == prev:
                            continue
                        if curr not in allowed_next and is_allowed_combination(prev, line) and is_allowed_combination(curr, line):
                            prev_var = get_is_producing_var(prev, line, d)
                            curr_var = get_is_producing_var(curr, line, d + 1)
                            if prev_var is not None and curr_var is not None:
                                # HARD forbid
                                model.Add(prev_var + curr_var <= 1)

    # ---------- SOFT constraints: penalties (objective) ----------
    if progress_callback:
        progress_callback(0.6, "Building objective function...")

    objective_terms = []

    # inventory deficit penalties (min inventory)
    inv_deficit_vars = {}
    for grade in grades:
        for d in range(num_days):
            min_inv = int(min_inventory.get(grade, 0))
            if min_inv > 0:
                inv_tomorrow = inventory_vars[(grade, d + 1)]
                deficit = model.NewIntVar(0, 10**8, f'inv_deficit_{grade}_{d}')
                # deficit >= min_inv - inventory_tomorrow and >= 0
                model.Add(deficit >= min_inv - inv_tomorrow)
                model.Add(deficit >= 0)
                inv_deficit_vars[(grade, d)] = deficit

    # closing inventory deficit (soft)
    closing_deficit_vars = {}
    if buffer_days is None:
        buffer_days = 0
    closing_day_index = max(0, num_days - buffer_days)
    for grade in grades:
        if min_closing_inventory.get(grade, 0) > 0:
            # closing inventory defined at inventory_vars[(grade, num_days - buffer_days)]
            closing_idx = max(0, num_days - buffer_days)
            if closing_idx <= num_days:
                closing_inv = inventory_vars[(grade, closing_idx)]
                deficit = model.NewIntVar(0, 10**8, f'closing_deficit_{grade}')
                model.Add(deficit >= int(min_closing_inventory.get(grade, 0)) - closing_inv)
                model.Add(deficit >= 0)
                closing_deficit_vars[grade] = deficit

    # Stockout penalty
    demand_days = max(0, num_days - buffer_days)
    if penalty_method == "Ensure All Grades' Production":
        # scale per-grade by total demand so objective approximates %stockout minimization
        SCALE = 10000  # scaling to convert fractional weights to integers
        for grade in grades:
            total_demand = sum(int(demand_data.get(grade, {}).get(dates[d], 0)) for d in range(num_days))
            if total_demand <= 0:
                continue
            per_unit_penalty = max(1, int(stockout_penalty * SCALE / total_demand))
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    objective_terms.append(per_unit_penalty * stockout_vars[(grade, d)])
            # inventory deficits extra weight
            for (g, dd), defvar in inv_deficit_vars.items():
                if g == grade:
                    objective_terms.append(per_unit_penalty * defvar)
            if grade in closing_deficit_vars:
                objective_terms.append(per_unit_penalty * 3 * closing_deficit_vars[grade])
    else:
        # Standard method: per unit stockout penalty same across grades
        for grade in grades:
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    objective_terms.append(stockout_penalty * stockout_vars[(grade, d)])
        # min inventory deficits
        for defvar in inv_deficit_vars.values():
            objective_terms.append(stockout_penalty * defvar)
        for defvar in closing_deficit_vars.values():
            objective_terms.append(stockout_penalty * 3 * defvar)

    # Transition penalties (for allowed transitions only)
    for line in lines:
        rules_for_line = transition_rules.get(line, {})
        for d in range(demand_days - 1):
            for g1 in grades:
                if not is_allowed_combination(g1, line):
                    continue
                for g2 in grades:
                    if g1 == g2:
                        continue
                    if not is_allowed_combination(g2, line):
                        continue
                    # if transition is explicitly forbidden we already added HARD constraint; only add penalty for allowed ones
                    if rules_for_line and g1 in rules_for_line and g2 not in rules_for_line[g1]:
                        continue
                    # create transition indicator
                    tvar = model.NewBoolVar(f'trans_{line}_{d}_{g1}_to_{g2}')
                    p1 = get_is_producing_var(g1, line, d)
                    p2 = get_is_producing_var(g2, line, d + 1)
                    if p1 is None or p2 is None:
                        continue
                    model.Add(tvar <= p1)
                    model.Add(tvar <= p2)
                    model.Add(tvar >= p1 + p2 - 1)
                    objective_terms.append(transition_penalty * tvar)

    # Set objective
    if objective_terms:
        model.Minimize(sum(objective_terms))
    else:
        model.Minimize(0)

    if progress_callback:
        progress_callback(0.8, "Solving optimization problem...")

    # solver settings
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit_min) * 60.0
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED

    # callback
    solution_callback = SolutionCallback(
        production, inventory_vars, stockout_vars, is_producing,
        grades, lines, dates, formatted_dates, num_days,
        inventory_deficit_penalties=None, closing_inventory_deficit_penalties=None,
        buffer_days=buffer_days
    )

    status = solver.Solve(model, solution_callback)

    if progress_callback:
        progress_callback(1.0, "Optimization complete!")

    return status, solution_callback, solver
