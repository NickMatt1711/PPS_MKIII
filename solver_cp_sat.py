
""" 
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
    """Build and solve the optimization model"""
    if progress_callback:
        progress_callback(0.0, "Building optimization model...")

    model = cp_model.CpModel()

    # Decision variables
    is_producing = {}
    production = {}

    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])

    # Create production variables
    for grade in grades:
        for line in allowed_lines[grade]:
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                # Always enforce full capacity or zero (HARD CONSTRAINT)
                production_value = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                model.Add(production_value == capacities[line]).OnlyEnforceIf(is_producing[key])
                model.Add(production_value == 0).OnlyEnforceIf(is_producing[key].Not())
                production[key] = production_value

    # Helper functions
    def get_production_var(grade, line, d):
        key = (grade, line, d)
        return production.get(key, 0)

    def get_is_producing_var(grade, line, d):
        key = (grade, line, d)
        return is_producing.get(key)

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

    # 2. One grade per line per day (HARD)
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

    # 3. Material running constraints (HARD)
    # If material running is specified, it MUST run on day 0
    # If expected_days is a positive integer, it MUST run for exactly that many days
    # If expected_days is None (not specified), only day 0 is forced, rest is optimization decision
    material_running_map = {}

    for plant, info in material_running_info.items():
        # info expected to be a tuple (material, expected_days) or similar
        try:
            material, expected_days = info
        except Exception:
            # If format unexpected, skip and warn (avoid silent failure)
            expected_days = None
            material = info if isinstance(info, str) else None

        if material is None:
            continue

        # Force the material on day 0 if allowed
        if is_allowed_combination(material, plant):
            day0_var = get_is_producing_var(material, plant, 0)
            if day0_var is not None:
                model.Add(day0_var == 1)

            # Force all other grades to 0 on day 0 (clear exclusivity)
            for other_grade in grades:
                if other_grade != material and is_allowed_combination(other_grade, plant):
                    other_var = get_is_producing_var(other_grade, plant, 0)
                    if other_var is not None:
                        model.Add(other_var == 0)

        # If expected_days is a positive integer, force continuation for exactly that many days
        if expected_days is not None and isinstance(expected_days, int) and expected_days > 0:
            forced_days = min(expected_days, num_days)  # never exceed planning horizon

            # Force the material to run for days [0 .. forced_days-1]
            for d in range(1, forced_days):  # day 0 already forced above
                if d < num_days and is_allowed_combination(material, plant):
                    v = get_is_producing_var(material, plant, d)
                    if v is not None:
                        model.Add(v == 1)
                    # ensure other grades are zero on those forced days
                    for other_grade in grades:
                        if other_grade != material and is_allowed_combination(other_grade, plant):
                            other_v = get_is_producing_var(other_grade, plant, d)
                            if other_v is not None:
                                model.Add(other_v == 0)

            # record the forced block (useful later)
            material_running_map[plant] = {
                'material': material,
                'expected_days': forced_days
            }

            # ---------------------------
            # CRITICAL: Enforce mandatory changeover ON THE NEXT DAY (forced_days)
            # That is: day index forced_days must NOT produce the same material.
            # And, if possible, enforce that some other allowed grade runs on that day
            # (this prevents leaving the line idle if other constraints allow it).
            # ---------------------------
            end_day = forced_days  # day index that must be a different grade

            if end_day < num_days:
                # Prevent the same material on day end_day
                if is_allowed_combination(material, plant):
                    next_var = get_is_producing_var(material, plant, end_day)
                    if next_var is not None:
                        model.Add(next_var == 0)

                # As an additional safety, require at least one other allowed grade to run
                # (only add if there exists at least one other allowed grade that can run on this plant)
                alternative_grade_vars = []
                for other_grade in grades:
                    if other_grade != material and is_allowed_combination(other_grade, plant):
                        v_alt = get_is_producing_var(other_grade, plant, end_day)
                        if v_alt is not None:
                            alternative_grade_vars.append(v_alt)

                if alternative_grade_vars:
                    # At least one of the other grades must run on the day after the material block.
                    # This is a HARD constraint: if it cannot be satisfied it will make model infeasible
                    model.Add(sum(alternative_grade_vars) >= 1)
                else:
                    # No alternative grade allowed on this plant — log/warn (helps debugging)
                    # If you want silent behavior, remove or replace this with a debug print
                    # (in Streamlit context you might call st.warning, but avoid UI calls in solver module)
                    # Here we add no-op; constraint on next_var == 0 is already set above if applicable.
                    pass

        else:
            # expected_days is None/0/invalid — treat as no forced continuation beyond day 0 (or none at all)
            # Record as 'not forced' if you wish
            material_running_map[plant] = {
                'material': material,
                'expected_days': 1 if expected_days == 0 else 0
            }

    # ========== NEW: PRE-SHUTDOWN AND RESTART GRADE CONSTRAINTS ==========
    if progress_callback:
        progress_callback(0.15, "Adding shutdown/restart constraints...")
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            shutdown_days = shutdown_periods[line]
            # Pre-Shutdown Grade constraint - ONLY if specified and not empty
            if line in pre_shutdown_grades and pre_shutdown_grades[line]:
                pre_grade = pre_shutdown_grades[line]
                if pre_grade in grades and is_allowed_combination(pre_grade, line):
                    # Day before shutdown must produce the pre-shutdown grade
                    # HARD CONSTRAINT
                    day_before = shutdown_days[0] - 1
                    if day_before >= 0:
                        var = get_is_producing_var(pre_grade, line, day_before)
                        if var is not None:
                            model.Add(var == 1)
                        # Also force all other grades to 0 on that day
                        for other_grade in grades:
                            if other_grade != pre_grade and is_allowed_combination(other_grade, line):
                                other_var = get_is_producing_var(other_grade, line, day_before)
                                if other_var is not None:
                                    model.Add(other_var == 0)
            # Restart Grade constraint - ONLY if specified and not empty
            if line in restart_grades and restart_grades[line]:
                restart_grade = restart_grades[line]
                if restart_grade in grades and is_allowed_combination(restart_grade, line):
                    # Day after shutdown must produce the restart grade
                    # HARD CONSTRAINT
                    day_after = shutdown_days[-1] + 1
                    if day_after < num_days:
                        var = get_is_producing_var(restart_grade, line, day_after)
                        if var is not None:
                            model.Add(var == 1)
                        # Also force all other grades to 0 on that day
                        for other_grade in grades:
                            if other_grade != restart_grade and is_allowed_combination(other_grade, line):
                                other_var = get_is_producing_var(other_grade, line, day_after)
                                if other_var is not None:
                                    model.Add(other_var == 0)

    if progress_callback:
        progress_callback(0.2, "Adding inventory constraints...")

    # Inventory variables
    inventory_vars = {}
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 100000, f'inventory_{grade}_{d}')

    stockout_vars = {}
    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 100000, f'stockout_{grade}_{d}')

    # ========== FIXED INVENTORY BALANCE CONSTRAINTS ==========
    # Initial inventory
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == initial_inventory[grade])

    # Inventory balance for each day
    for grade in grades:
        for d in range(num_days):
            # Calculate total production for this grade on day d
            produced_today = sum(
                get_production_var(grade, line, d)
                for line in allowed_lines[grade]
            )
            demand_today = demand_data[grade].get(dates[d], 0)
            # Available inventory (opening inventory + production)
            available = model.NewIntVar(0, 100000, f'available_{grade}_{d}')
            model.Add(available == inventory_vars[(grade, d)] + produced_today)
            # Supply variable - what we actually supply today
            supplied = model.NewIntVar(0, 100000, f'supplied_{grade}_{d}')
            # Stockout variable
            stockout = model.NewIntVar(0, 100000, f'stockout_{grade}_{d}')

            # CRITICAL FIX: FORCE MAXIMUM POSSIBLE SUPPLY
            # Supply cannot exceed available inventory or demand
            model.Add(supplied <= available)
            model.Add(supplied <= demand_today)

            # Indicator: do we have enough inventory to meet demand?
            enough_inventory = model.NewBoolVar(f'enough_{grade}_{d}')
            model.Add(available >= demand_today).OnlyEnforceIf(enough_inventory)
            model.Add(available < demand_today).OnlyEnforceIf(enough_inventory.Not())

            # Force supply to be maximum possible
            model.Add(supplied == demand_today).OnlyEnforceIf(enough_inventory)
            model.Add(supplied == available).OnlyEnforceIf(enough_inventory.Not())

            # Stockout is unmet demand
            model.Add(stockout == demand_today - supplied)

            # Update inventory for next day
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)

            # Store stockout variable
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
            if production_vars:
                # Line must produce at full capacity
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

    # CORRECTED MIN/MAX RUN DAYS LOGIC
    for grade in grades:
        for line in allowed_lines[grade]:
            grade_plant_key = (grade, line)
            min_run = min_run_days.get(grade_plant_key, 1)
            max_run = max_run_days.get(grade_plant_key, 9999)

            # Check if this line has material running
            has_material_running = line in material_running_map
            material_running_grade = material_running_map[line]['material'] if has_material_running else None
            material_running_days = material_running_map[line]['expected_days'] if has_material_running else 0

            # FORCE CHANGEOVER AFTER MATERIAL RUNNING if explicitly specified
            if line in material_running_info:
                material_grade, original_expected_days = material_running_info[line]
                has_forced_block = (line in material_running_map and
                                    material_running_map[line]['expected_days'] > 1)
                if material_grade == grade and has_forced_block:
                    forced_days = material_running_map[line]['expected_days']
                    if forced_days < num_days:
                        prod_day_after = get_is_producing_var(grade, line, forced_days)
                        if prod_day_after is not None:
                            model.Add(prod_day_after == 0)  # Force changeover

            # MINIMUM RUN DAYS CONSTRAINT (applies to NEW runs started within planning horizon)
            for d in range(num_days):
                # Check if this day is within material running block
                is_in_material_block = False
                if line in material_running_map:
                    material_grade = material_running_map[line]['material']
                    expected_days = material_running_map[line]['expected_days']
                    if material_grade == grade and d < expected_days:
                        is_in_material_block = True
                if is_in_material_block:
                    continue  # Skip min-run constraint for material running days

                prod_today = get_is_producing_var(grade, line, d)
                if prod_today is None:
                    continue

                # Check if this is start of a new run
                if d == 0:
                    # Day 0: Check if this is forced material running
                    is_forced_material = False
                    if line in material_running_info:
                        material_grade, expected_days = material_running_info[line]
                        if material_grade == grade:
                            is_forced_material = True
                    if is_forced_material:
                        # This is forced material running on day 0
                        # Don't treat it as a new start for min-run constraints
                        continue
                    else:
                        # Otherwise, treat day 0 as a potential new start
                        starts_new_run = prod_today
                else:
                    prod_yesterday = get_is_producing_var(grade, line, d - 1)
                    if prod_yesterday is not None:
                        # Check if yesterday was material running
                        yesterday_in_material_block = False
                        if line in material_running_map:
                            material_grade = material_running_map[line]['material']
                            expected_days = material_running_map[line]['expected_days']
                            if material_grade == grade and (d - 1) < expected_days:
                                yesterday_in_material_block = True
                        if yesterday_in_material_block:
                            # Yesterday was forced material running
                            # Today cannot be same grade (we already enforced changeover)
                            # So this cannot be a continuation
                            continue
                        # Create start indicator: producing today AND not producing yesterday
                        starts_new_run = model.NewBoolVar(f'starts_new_run_{grade}_{line}_{d}')
                        model.Add(starts_new_run <= prod_today)
                        model.Add(starts_new_run <= 1 - prod_yesterday)
                        model.Add(starts_new_run >= prod_today - prod_yesterday)
                    else:
                        continue

                # If this is start of a new run, enforce min_run days
                if d + min_run > num_days:
                    continue  # Not enough days for min_run
                run_days_vars = []
                valid_for_min_run = True
                for offset in range(min_run):
                    day_idx = d + offset
                    if day_idx >= num_days:
                        valid_for_min_run = False
                        break
                    # Check for shutdown days
                    if line in shutdown_periods and day_idx in shutdown_periods[line]:
                        valid_for_min_run = False
                        break
                    prod_var = get_is_producing_var(grade, line, day_idx)
                    if prod_var is not None:
                        run_days_vars.append(prod_var)
                    else:
                        valid_for_min_run = False
                        break
                if not valid_for_min_run or len(run_days_vars) < min_run:
                    continue
                # Enforce that if this is a start, all run_days_vars must be 1
                for prod_var in run_days_vars[:min_run]:
                    if d == 0:
                        model.Add(prod_var == 1).OnlyEnforceIf(prod_today)
                    else:
                        model.Add(prod_var == 1).OnlyEnforceIf(starts_new_run)

            # MAXIMUM RUN DAYS CONSTRAINT (applies to ALL runs, including material running)
            for d in range(num_days - max_run):
                consecutive_vars = []
                valid_sequence = True
                for offset in range(max_run + 1):
                    day_idx = d + offset
                    if day_idx >= num_days:
                        valid_sequence = False
                        break
                    # Shutdown days break the sequence
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
                    # Cannot have all max_run+1 days producing this grade
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
                                    # HARD CONSTRAINT: Cannot have forbidden transition
                                    model.Add(prev_var + current_var <= 1)

    # 7. Rerun allowed constraints (HARD)
    for grade in grades:
        for line in allowed_lines[grade]:
            grade_plant_key = (grade, line)
            if not rerun_allowed.get(grade_plant_key, True):
                # Count how many times this grade starts a new run
                # Exclude material running from the count
                start_count_vars = []
                for d in range(num_days):
                    # Skip if this is within material running block
                    if line in material_running_map:
                        material_running_grade = material_running_map[line]['material']
                        material_running_days = material_running_map[line]['expected_days']
                        if material_running_grade == grade and d < material_running_days:
                            continue
                    prod_today = get_is_producing_var(grade, line, d)
                    if prod_today is None:
                        continue
                    if d == 0:
                        # Day 0 could be a start (if not in material block)
                        start_count_vars.append(prod_today)
                    else:
                        prod_yesterday = get_is_producing_var(grade, line, d - 1)
                        if prod_yesterday is not None:
                            # Check if yesterday was material running
                            yesterday_in_material = False
                            if line in material_running_map:
                                material_running_grade = material_running_map[line]['material']
                                material_running_days = material_running_map[line]['expected_days']
                                yesterday_in_material = (material_running_grade == grade and
                                                         (d - 1) < material_running_days)
                            if yesterday_in_material:
                                # Yesterday was material running
                                # Today cannot be same grade (changeover enforced)
                                continue
                            # Create start indicator
                            start_indicator = model.NewBoolVar(f'rerun_start_{grade}_{line}_{d}')
                            model.Add(start_indicator <= prod_today)
                            model.Add(start_indicator <= 1 - prod_yesterday)
                            model.Add(start_indicator >= prod_today - prod_yesterday)
                            start_count_vars.append(start_indicator)
                        else:
                            continue
                if start_count_vars:
                    # Can start at most once (excluding material running)
                    model.Add(sum(start_count_vars) <= 1)

    if progress_callback:
        progress_callback(0.6, "Adding soft constraints...")

    # ========== SOFT CONSTRAINTS ==========
    # These go into the objective function with penalties
    # Create explicit penalty variables for SOFT constraints
    inventory_deficit_penalties = {}
    closing_inventory_deficit_penalties = {}

    # 1. Minimum inventory (SOFT)
    for grade in grades:
        for d in range(num_days):
            if min_inventory[grade] > 0:
                min_inv_value = int(min_inventory[grade])
                inventory_tomorrow = inventory_vars[(grade, d + 1)]
                deficit_var = model.NewIntVar(0, 100000, f'inv_deficit_{grade}_{d}')
                model.Add(deficit_var >= min_inv_value - inventory_tomorrow)
                model.Add(deficit_var >= 0)
                inventory_deficit_penalties[(grade, d)] = deficit_var

        # Minimum closing inventory (SOFT)
        if min_closing_inventory[grade] > 0 and buffer_days > 0:
            closing_inventory = inventory_vars[(grade, num_days - buffer_days)]
            min_closing = min_closing_inventory[grade]
            closing_deficit_var = model.NewIntVar(0, 100000, f'closing_deficit_{grade}')
            model.Add(closing_deficit_var >= min_closing - closing_inventory)
            model.Add(closing_deficit_var >= 0)
            closing_inventory_deficit_penalties[grade] = closing_deficit_var

    if progress_callback:
        progress_callback(0.7, "Building objective function...")

    # ========== OBJECTIVE FUNCTION ==========
    # Only contains SOFT constraints with penalties
    objective_terms = []
    epsilon = 1.0  # Small constant to avoid division by zero

    # Demand period length (exclude buffer days at the tail)
    demand_days = max(0, num_days - buffer_days)

    # 1. Stockout penalties (SOFT) - Two methods
    if penalty_method == "Ensure All Grades' Production":
        for grade in grades:
            # Total demand over entire horizon
            total_demand = sum(demand_data[grade].get(dates[d], 0) for d in range(num_days))
            if total_demand <= 0:
                continue
    
            # Penalty such that cost = stockout_percentage × stockout_penalty
            per_unit_penalty = int(stockout_penalty * 10000 / total_demand)
    
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    objective_terms.append(per_unit_penalty * stockout_vars[(grade, d)])

    else:  # Standard method (default)
        for grade in grades:
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    objective_terms.append(stockout_penalty * stockout_vars[(grade, d)])

    # 2. Inventory deficit penalties (SOFT) - Adjusted based on method
    if penalty_method == "Ensure All Grades' Production":
        MIN_INV_VIOLATION_MULTIPLIER = 2  # Make min inventory violations more expensive
        for (grade, d), deficit_var in inventory_deficit_penalties.items():
            daily_demand = demand_data[grade].get(dates[d], 0)
            if daily_demand > 0:
                penalty_coeff = (PERCENTAGE_PENALTY_WEIGHT * stockout_penalty * MIN_INV_VIOLATION_MULTIPLIER) / (daily_demand + epsilon)
                scaled_penalty = int(penalty_coeff * 100)
                objective_terms.append(scaled_penalty * deficit_var)
            else:
                objective_terms.append(stockout_penalty * MIN_INV_VIOLATION_MULTIPLIER * deficit_var)
    else:  # Standard method
        for (grade, d), deficit_var in inventory_deficit_penalties.items():
            objective_terms.append(stockout_penalty * deficit_var)

    # 3. Closing inventory deficit penalties (SOFT)
    if penalty_method == "Ensure All Grades' Production":
        for grade, closing_deficit_var in closing_inventory_deficit_penalties.items():
            total_demand = sum(demand_data[grade].get(dates[d], 0) for d in range(num_days))
            avg_daily_demand = total_demand / num_days if num_days > 0 else 1
            if avg_daily_demand > 0:
                penalty_coeff = (PERCENTAGE_PENALTY_WEIGHT * stockout_penalty * 3) / (avg_daily_demand + epsilon)
                scaled_penalty = int(penalty_coeff * 100)
                objective_terms.append(scaled_penalty * closing_deficit_var)
            else:
                objective_terms.append(stockout_penalty * closing_deficit_var * 3)
    else:  # Standard method
        for grade, closing_deficit_var in closing_inventory_deficit_penalties.items():
            objective_terms.append(stockout_penalty * closing_deficit_var * 3)

    # 4. Transition penalties (SOFT - for ALLOWED transitions only; only within demand period)
    # Forbidden transitions are already prevented by HARD constraints
    # This remains the same for all methods
    for line in lines:
        for d in range(demand_days - 1):
            for grade1 in grades:
                if line not in allowed_lines[grade1]:
                    continue
                for grade2 in grades:
                    if line not in allowed_lines[grade2] or grade1 == grade2:
                        continue
                    # Skip if this is a forbidden transition (already handled as HARD)
                    if (transition_rules.get(line) and
                        grade1 in transition_rules[line] and
                        grade2 not in transition_rules[line][grade1]):
                        continue
                    # Only penalize ALLOWED transitions
                    trans_var = model.NewBoolVar(f'trans_{line}_{d}_{grade1}_to_{grade2}')
                    # Link transition variable to production decisions
                    model.Add(trans_var <= is_producing[(grade1, line, d)])
                    model.Add(trans_var <= is_producing[(grade2, line, d + 1)])
                    model.Add(trans_var >= is_producing[(grade1, line, d)] +
                              is_producing[(grade2, line, d + 1)] - 1)
                    objective_terms.append(transition_penalty * trans_var)

    # 5. Idle line penalty (SOFT - to minimize gaps, but not required)
    idle_penalty = 500  # Lower than transition penalty to prioritize min runs
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            is_idle = model.NewBoolVar(f'idle_{line}_{d}')
            producing_vars = [
                is_producing[(grade, line, d)]
                for grade in grades
                if (grade, line, d) in is_producing
            ]
            if producing_vars:
                model.Add(sum(producing_vars) == 0).OnlyEnforceIf(is_idle)
                model.Add(sum(producing_vars) == 1).OnlyEnforceIf(is_idle.Not())
                objective_terms.append(idle_penalty * is_idle)

    # Set the objective to minimize SOFT constraint violations
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
