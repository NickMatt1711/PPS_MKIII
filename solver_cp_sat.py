"""
Refactored CP-SAT Solver for production optimization
- Exactly one grade per line per day at full capacity (non-shutdown days)
- Tight variable domains for better propagation
- Clean stockout variable creation (no duplicates)
- Min-run starts forbidden when infeasible near shutdown/horizon
- Simplified transition (changeover) penalties; forbidden transitions remain hard
- Closing inventory measured at horizon excluding buffer days
- Penalty scaling without truncation artifacts; integer-safe scaling
- Objective breakdown computed in the solution callback
- Decision hints and mild symmetry reduction (optional)
"""

from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED


class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Callback to capture all solutions during search"""

    def __init__(
        self,
        production,
        inventory,
        stockout,
        is_producing,
        grades,
        lines,
        dates,
        formatted_dates,
        num_days,
        inventory_deficit_penalties=None,
        closing_inventory_deficit_penalties=None,
        run_starts=None,
        objective_components=None,
    ):
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
        self.inventory_deficit_penalties = inventory_deficit_penalties or {}
        self.closing_inventory_deficit_penalties = closing_inventory_deficit_penalties or {}
        self.run_starts = run_starts or {}
        self.objective_components = objective_components or []

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

        # Store production data (aggregated per grade per date across lines)
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

        # Store inventory data - opening inventory for each day
        for grade in self.grades:
            solution['inventory'][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.inventory:
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

        # Store production schedule (grade selected per line per day)
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

        # Count transitions (actual grade changes)
        transition_count_per_line = {line: 0 for line in self.lines}
        total_transitions = 0
        for line in self.lines:
            last_grade = None
            for d in range(self.num_days):
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
        totals = {
            'stockout': 0,
            'min_inv_deficit': 0,
            'closing_deficit': 0,
            'changeover': 0,
            'solver_objective': solver_objective,
            'calculated_total': 0
        }
        for var, coeff, tag in self.objective_components:
            val = self.Value(var)
            amount = coeff * val
            kind = tag[0]
            if kind in totals:
                totals[kind] += amount
            totals['calculated_total'] += amount
        return totals

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
    """Build and solve the optimization model"""
    if progress_callback:
        progress_callback(0.0, "Building optimization model...")

    model = cp_model.CpModel()

    # Decision variables
    is_producing = {}
    production = {}
    run_starts = {}  # Track run starts

    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])

    # Create production variables (capacity-or-zero per grade-line-day)
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                prod_val = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                # Production equals capacity if producing, else 0
                model.Add(prod_val == capacities[line]).OnlyEnforceIf(is_producing[key])
                model.Add(prod_val == 0).OnlyEnforceIf(is_producing[key].Not())
                production[key] = prod_val
                # Run start flag
                run_starts[key] = model.NewBoolVar(f'run_start_{grade}_{line}_{d}')

    # Helper getters
    def get_production_var(grade, line, d):
        key = (grade, line, d)
        return production.get(key, None)

    def get_is_producing_var(grade, line, d):
        key = (grade, line, d)
        return is_producing.get(key, None)

    if progress_callback:
        progress_callback(0.1, "Adding hard constraints...")

    # ========== HARD CONSTRAINTS ==========
    # 1. Shutdown constraints (HARD)
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        key = (grade, line, d)
                        if key in is_producing:
                            model.Add(is_producing[key] == 0)
                            model.Add(production[key] == 0)

    # 2. Exactly one grade per line per day (HARD, except shutdown days)
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            producing_vars = []
            for grade in grades:
                if is_allowed_combination(grade, line):
                    var = get_is_producing_var(grade, line, d)
                    if var is not None:
                        producing_vars.append(var)
            if producing_vars:
                model.Add(sum(producing_vars) == 1)

    # 3. Material running constraints (HARD)
    material_running_map = {}
    for plant, (material, expected_days) in material_running_info.items():
        # Force the material to run on day 0
        if is_allowed_combination(material, plant):
            day0_var = get_is_producing_var(material, plant, 0)
            if day0_var is not None:
                model.Add(day0_var == 1)
            # Prohibit others on day 0
            for other_material in grades:
                if other_material != material and is_allowed_combination(other_material, plant):
                    other_var = get_is_producing_var(other_material, plant, 0)
                    if other_var is not None:
                        model.Add(other_var == 0)
        # Extend forced block across expected days (if provided)
        if expected_days is not None and expected_days > 0:
            forced_days = min(expected_days, num_days)
            for d in range(1, forced_days):
                if d < num_days and is_allowed_combination(material, plant):
                    var = get_is_producing_var(material, plant, d)
                    if var is not None:
                        model.Add(var == 1)
                for other_material in grades:
                    if other_material != material and is_allowed_combination(other_material, plant):
                        other_var = get_is_producing_var(other_material, plant, d)
                        if other_var is not None:
                            model.Add(other_var == 0)
            material_running_map[plant] = {
                'material': material,
                'expected_days': forced_days
            }
        else:
            material_running_map[plant] = {
                'material': material,
                'expected_days': 1
            }

    # ========== PRE-SHUTDOWN AND RESTART GRADE CONSTRAINTS ==========
    if progress_callback:
        progress_callback(0.15, "Adding shutdown/restart constraints...")

    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            shutdown_days = shutdown_periods[line]
            # Pre-shutdown grade on the day before first shutdown
            if line in pre_shutdown_grades and pre_shutdown_grades[line]:
                pre_grade = pre_shutdown_grades[line]
                if pre_grade in grades and is_allowed_combination(pre_grade, line):
                    day_before = shutdown_days[0] - 1
                    if day_before >= 0:
                        var = get_is_producing_var(pre_grade, line, day_before)
                        if var is not None:
                            model.Add(var == 1)
                        for other_grade in grades:
                            if other_grade != pre_grade and is_allowed_combination(other_grade, line):
                                other_var = get_is_producing_var(other_grade, line, day_before)
                                if other_var is not None:
                                    model.Add(other_var == 0)
            # Restart grade on the day after last shutdown
            if line in restart_grades and restart_grades[line]:
                restart_grade = restart_grades[line]
                if restart_grade in grades and is_allowed_combination(restart_grade, line):
                    day_after = shutdown_days[-1] + 1
                    if day_after < num_days:
                        var = get_is_producing_var(restart_grade, line, day_after)
                        if var is not None:
                            model.Add(var == 1)
                        for other_grade in grades:
                            if other_grade != restart_grade and is_allowed_combination(other_grade, line):
                                other_var = get_is_producing_var(other_grade, line, day_after)
                                if other_var is not None:
                                    model.Add(other_var == 0)

    if progress_callback:
        progress_callback(0.2, "Adding inventory constraints...")

    # Inventory variables with tighter bounds
    inventory_vars = {}
    for grade in grades:
        max_daily_prod = sum(capacities[line] for line in allowed_lines.get(grade, []))
        for d in range(num_days + 1):
            inv_ub = min(
                max_inventory[grade],
                initial_inventory[grade] + d * max_daily_prod
            )
            inventory_vars[(grade, d)] = model.NewIntVar(0, inv_ub, f'inventory_{grade}_{d}')

    stockout_vars = {}

    # Initial inventory
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == initial_inventory[grade])

    # Inventory balance for each day
    for grade in grades:
        max_daily_prod = sum(capacities[line] for line in allowed_lines.get(grade, []))
        for d in range(num_days):
            produced_today = sum(
                get_production_var(grade, line, d) or model.NewIntVar(0, 0, f'zero_prod_{grade}_{line}_{d}')
                for line in allowed_lines.get(grade, [])
            )
            demand_today = demand_data[grade].get(dates[d], 0)

            # Tighter domains
            inv_cap_d = min(
                max_inventory[grade],
                initial_inventory[grade] + d * max_daily_prod
            )
            available = model.NewIntVar(0, inv_cap_d + max_daily_prod, f'available_{grade}_{d}')
            model.Add(available == inventory_vars[(grade, d)] + produced_today)

            supplied = model.NewIntVar(0, demand_today, f'supplied_{grade}_{d}')
            stockout = model.NewIntVar(0, demand_today, f'stockout_{grade}_{d}')

            # Supply cannot exceed available or demand
            model.Add(supplied <= available)
            model.Add(supplied <= demand_today)

            # Boolean to branch supply rule
            enough_inventory = model.NewBoolVar(f'enough_{grade}_{d}')
            model.Add(available >= demand_today).OnlyEnforceIf(enough_inventory)
            model.Add(available < demand_today).OnlyEnforceIf(enough_inventory.Not())
            model.Add(supplied == demand_today).OnlyEnforceIf(enough_inventory)
            model.Add(supplied == available).OnlyEnforceIf(enough_inventory.Not())

            model.Add(stockout == demand_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)

            stockout_vars[(grade, d)] = stockout

    # Maximum inventory (HARD)
    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= max_inventory[grade])

    if progress_callback:
        progress_callback(0.3, "Adding capacity constraints...")

    # 4. Full capacity utilization (HARD - except shutdown days)
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            production_vars = [
                get_production_var(grade, line, d)
                for grade in grades
                if is_allowed_combination(grade, line)
            ]
            production_vars = [pv for pv in production_vars if pv is not None]
            if production_vars:
                model.Add(sum(production_vars) == capacities[line])

    if progress_callback:
        progress_callback(0.4, "Adding run constraints...")

    # 5. Force start date constraints (HARD)
    for grade_plant_key, start_date in force_start_date.items():
        if start_date:
            grade, plant = grade_plant_key
            try:
                start_day_index = dates.index(start_date)
                var = get_is_producing_var(grade, plant, start_day_index)
                if var is not None:
                    model.Add(var == 1)
            except ValueError:
                pass

    # ========== RUN START DEFINITION & MIN/MAX RUN DAYS ==========
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            grade_plant_key = (grade, line)
            min_run = min_run_days.get(grade_plant_key, 1)
            max_run = max_run_days.get(grade_plant_key, 9999)

            # Define run start variables: start when producing today and not yesterday
            for d in range(num_days):
                key = (grade, line, d)
                prod_today = get_is_producing_var(grade, line, d)
                if prod_today is None:
                    continue
                if d == 0:
                    model.Add(run_starts[key] == prod_today)
                else:
                    prod_yesterday = get_is_producing_var(grade, line, d - 1)
                    if prod_yesterday is not None:
                        model.Add(run_starts[key] <= prod_today)
                        model.Add(run_starts[key] <= 1 - prod_yesterday)
                        model.Add(run_starts[key] >= prod_today - prod_yesterday)
                    else:
                        model.Add(run_starts[key] == 0)

            # Force changeover after material running block
            if line in material_running_info:
                material_grade, original_expected_days = material_running_info[line]
                has_forced_block = (line in material_running_map and
                                    material_running_map[line]['expected_days'] > 1)
                if material_grade == grade and has_forced_block:
                    forced_days = material_running_map[line]['expected_days']
                    if forced_days < num_days:
                        prod_day_after = get_is_producing_var(grade, line, forced_days)
                        if prod_day_after is not None:
                            model.Add(prod_day_after == 0)

            # Minimum run days: forbid starts that cannot meet min_run
            for d in range(num_days):
                key = (grade, line, d)
                if key not in run_starts:
                    continue

                # Check feasibility of min_run starting at d
                feasible = True
                for offset in range(min_run):
                    day_idx = d + offset
                    if day_idx >= num_days:
                        feasible = False
                        break
                    if line in shutdown_periods and day_idx in shutdown_periods[line]:
                        feasible = False
                        break
                if not feasible:
                    model.Add(run_starts[key] == 0)
                else:
                    # Enforce min_run when start occurs
                    for offset in range(min_run):
                        day_idx = d + offset
                        pv = get_is_producing_var(grade, line, day_idx)
                        if pv is not None:
                            model.Add(pv == 1).OnlyEnforceIf(run_starts[key])

            # Maximum run days
            for d in range(num_days - max_run):
                consecutive_vars = []
                valid_sequence = True
                for offset in range(max_run + 1):
                    day_idx = d + offset
                    if day_idx >= num_days:
                        valid_sequence = False
                        break
                    if line in shutdown_periods and day_idx in shutdown_periods[line]:
                        valid_sequence = False
                        break
                    prod_var = get_is_producing_var(grade, line, day_idx)
                    if prod_var is not None:
                        consecutive_vars.append(prod_var)
                    else:
                        valid_sequence = False
                        break
                if valid_sequence and len(consecutive_vars) == max_run + 1:
                    model.Add(sum(consecutive_vars) <= max_run)

    if progress_callback:
        progress_callback(0.5, "Adding transition constraints...")

    # 6. Forbidden transitions (HARD)
    for line in lines:
        if transition_rules.get(line):
            for d in range(num_days - 1):
                for prev_grade in grades:
                    if prev_grade in transition_rules[line] and is_allowed_combination(prev_grade, line):
                        allowed_next = transition_rules[line][prev_grade]
                        for current_grade in grades:
                            if (current_grade != prev_grade and
                                current_grade not in allowed_next and
                                is_allowed_combination(current_grade, line)):
                                prev_var = get_is_producing_var(prev_grade, line, d)
                                current_var = get_is_producing_var(current_grade, line, d + 1)
                                if prev_var is not None and current_var is not None:
                                    model.Add(prev_var + current_var <= 1)

    # 7. Rerun allowed constraints (HARD)
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            grade_plant_key = (grade, line)
            if not rerun_allowed.get(grade_plant_key, True):
                start_count_vars = []
                for d in range(num_days):
                    if line in material_running_map:
                        material_running_grade = material_running_map[line]['material']
                        material_running_days = material_running_map[line]['expected_days']
                        if material_running_grade == grade and d < material_running_days:
                            continue
                    key = (grade, line, d)
                    if key in run_starts:
                        start_count_vars.append(run_starts[key])
                if start_count_vars:
                    model.Add(sum(start_count_vars) <= 1)

    if progress_callback:
        progress_callback(0.6, "Adding soft constraints...")

    # ========== SOFT CONSTRAINTS ==========
    inventory_deficit_penalties = {}
    closing_inventory_deficit_penalties = {}

    # Standard minimum inventory (SOFT)
    for grade in grades:
        for d in range(num_days):
            if min_inventory[grade] > 0:
                min_inv_value = int(min_inventory[grade])
                inventory_tomorrow = inventory_vars[(grade, d + 1)]
                deficit_var = model.NewIntVar(0, min_inv_value, f'inv_deficit_{grade}_{d}')
                model.Add(deficit_var >= min_inv_value - inventory_tomorrow)
                model.Add(deficit_var >= 0)
                inventory_deficit_penalties[(grade, d)] = deficit_var

    # Minimum closing inventory (SOFT) at horizon excluding buffer days
    # closing_day_index = num_days - buffer_days (clamped)
    closing_day_index = num_days - buffer_days
    closing_day_index = max(0, min(closing_day_index, num_days))
    for grade in grades:
        if min_closing_inventory[grade] > 0:
            closing_inventory = inventory_vars[(grade, closing_day_index)]
            min_closing = min_closing_inventory[grade]
            closing_deficit_var = model.NewIntVar(0, min_closing, f'closing_deficit_{grade}')
            model.Add(closing_deficit_var >= min_closing - closing_inventory)
            model.Add(closing_deficit_var >= 0)
            closing_inventory_deficit_penalties[grade] = closing_deficit_var

    if progress_callback:
        progress_callback(0.7, "Building objective function...")

    # ========== OBJECTIVE FUNCTION ==========
    objective_terms = []
    objective_components = []  # (var, coeff, tag)

    SCALE = 1000  # integer-safe scaling factor

    if penalty_method == "Ensure All Grades' Production":
        PERCENTAGE_PENALTY_WEIGHT = 100
        MIN_INV_VIOLATION_MULTIPLIER = 2

        # 1. Stockout penalties with demand normalization
        for grade in grades:
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    demand_today = demand_data[grade].get(dates[d], 0)
                    if demand_today > 0:
                        coeff = PERCENTAGE_PENALTY_WEIGHT * stockout_penalty * SCALE // demand_today
                    else:
                        coeff = stockout_penalty * SCALE
                    objective_terms.append(coeff * stockout_vars[(grade, d)])
                    objective_components.append((stockout_vars[(grade, d)], coeff, ('stockout', grade, d)))

        # 2. Inventory deficit penalties with normalization
        for (grade, d), deficit_var in inventory_deficit_penalties.items():
            daily_demand = demand_data[grade].get(dates[d], 0)
            if daily_demand > 0:
                coeff = (PERCENTAGE_PENALTY_WEIGHT * stockout_penalty * MIN_INV_VIOLATION_MULTIPLIER * SCALE) // daily_demand
            else:
                coeff = stockout_penalty * MIN_INV_VIOLATION_MULTIPLIER * SCALE
            objective_terms.append(coeff * deficit_var)
            objective_components.append((deficit_var, coeff, ('min_inv_deficit', grade, d)))

        # 3. Closing inventory deficit penalties with normalization
        for grade, closing_deficit_var in closing_inventory_deficit_penalties.items():
            total_demand = sum(demand_data[grade].get(dates[d], 0) for d in range(num_days))
            avg_daily_demand = total_demand // num_days if num_days > 0 else 0
            if avg_daily_demand > 0:
                coeff = (PERCENTAGE_PENALTY_WEIGHT * stockout_penalty * 3 * SCALE) // avg_daily_demand
            else:
                coeff = stockout_penalty * 3 * SCALE
            objective_terms.append(coeff * closing_deficit_var)
            objective_components.append((closing_deficit_var, coeff, ('closing_deficit', grade)))

    else:
        # ========== STANDARD MODE ==========
        # 1. Stockout penalties (linear)
        for grade in grades:
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    coeff = stockout_penalty * SCALE
                    objective_terms.append(coeff * stockout_vars[(grade, d)])
                    objective_components.append((stockout_vars[(grade, d)], coeff, ('stockout', grade, d)))

        # 2. Inventory deficit penalties
        for (grade, d), deficit_var in inventory_deficit_penalties.items():
            coeff = stockout_penalty * SCALE
            objective_terms.append(coeff * deficit_var)
            objective_components.append((deficit_var, coeff, ('min_inv_deficit', grade, d)))

        # 3. Closing inventory deficit penalties
        for grade, closing_deficit_var in closing_inventory_deficit_penalties.items():
            coeff = stockout_penalty * 3 * SCALE
            objective_terms.append(coeff * closing_deficit_var)
            objective_components.append((closing_deficit_var, coeff, ('closing_deficit', grade)))

    # 4. Transition penalties (changeover per line/day)
    for line in lines:
        for d in range(num_days - 1):
            changeover = model.NewBoolVar(f'changeover_{line}_{d}')
            # continuity vars (same grade continues)
            same_grade_vars = []
            for grade in grades:
                if is_allowed_combination(grade, line):
                    g_today = get_is_producing_var(grade, line, d)
                    g_next = get_is_producing_var(grade, line, d + 1)
                    if g_today is not None and g_next is not None:
                        cont = model.NewBoolVar(f'cont_{line}_{d}_{grade}')
                        model.Add(cont <= g_today)
                        model.Add(cont <= g_next)
                        model.Add(cont >= g_today + g_next - 1)
                        same_grade_vars.append(cont)
            if same_grade_vars:
                # Exactly one continuity or a changeover
                model.Add(sum(same_grade_vars) + changeover == 1)
            coeff = transition_penalty * SCALE
            objective_terms.append(coeff * changeover)
            objective_components.append((changeover, coeff, ('changeover', line, d)))

    # Build objective
    if objective_terms:
        model.Minimize(sum(objective_terms))
    else:
        model.Minimize(0)

    if progress_callback:
        progress_callback(0.8, "Solving optimization problem...")

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60.0
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED
    solver.parameters.log_search_progress = True

    # Decision hints (optional): give hints for forced material blocks
    for plant, info in material_running_map.items():
        mat = info['material']
        forced_days = info['expected_days']
        for d in range(min(forced_days, num_days)):
            var = get_is_producing_var(mat, plant, d)
            if var is not None:
                model.AddHint(var, 1)
        # day 0: other grades = 0
        for grade in grades:
            if grade != mat and is_allowed_combination(grade, plant):
                var = get_is_producing_var(grade, plant, 0)
                if var is not None:
                    model.AddHint(var, 0)

    solution_callback = SolutionCallback(
        production, inventory_vars, stockout_vars, is_producing,
        grades, lines, dates, formatted_dates, num_days,
        inventory_deficit_penalties, closing_inventory_deficit_penalties,
        run_starts, objective_components
    )

    status = solver.Solve(model, solution_callback)

    if progress_callback:
        progress_callback(1.0, "Optimization complete!")

    return status, solution_callback, solver
