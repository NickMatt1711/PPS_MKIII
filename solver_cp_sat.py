"""
CP-SAT Solver for production optimization (patched)

"""

from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple, Set, Any
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED


class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Callback to capture all solutions during search"""

    def __init__(
        self,
        production: Dict,
        inventory: Dict,
        stockout: Dict,
        is_producing: Dict,
        grades: List[str],
        lines: List[str],
        dates: List,
        formatted_dates: List[str],
        num_days: int,
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
        self.solutions = []
        self.solution_times = []
        self.start_time = time.time()

    def on_solution_callback(self):
        current_time = time.time() - self.start_time
        self.solution_times.append(current_time)
        current_obj = self.ObjectiveValue()

        solution = {
            "objective": current_obj,
            "time": current_time,
            "production": {},
            "inventory": {},
            "stockout": {},
            "is_producing": {},
        }

        # Store production data
        for grade in self.grades:
            solution["production"][grade] = {}
            for line in self.lines:
                for d in range(self.num_days):
                    key = (grade, line, d)
                    if key in self.production:
                        value = self.Value(self.production[key])
                        if value > 0:
                            date_key = self.formatted_dates[d]
                            if date_key not in solution["production"][grade]:
                                solution["production"][grade][date_key] = 0
                            solution["production"][grade][date_key] += value

        # Store inventory data (initial + days + final)
        for grade in self.grades:
            solution["inventory"][grade] = {}
            for d in range(self.num_days + 1):
                key = (grade, d)
                if key in self.inventory:
                    if d < self.num_days:
                        # Use formatted date for day > 0, and 'initial' label for d == 0
                        solution["inventory"][grade][
                            self.formatted_dates[d] if d > 0 else "initial"
                        ] = self.Value(self.inventory[key])
                    else:
                        solution["inventory"][grade]["final"] = self.Value(self.inventory[key])

        # Store stockout data
        for grade in self.grades:
            solution["stockout"][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.stockout:
                    value = self.Value(self.stockout[key])
                    if value > 0:
                        solution["stockout"][grade][self.formatted_dates[d]] = value

        # Store production schedule
        for line in self.lines:
            solution["is_producing"][line] = {}
            for d in range(self.num_days):
                date_key = self.formatted_dates[d]
                solution["is_producing"][line][date_key] = None
                for grade in self.grades:
                    key = (grade, line, d)
                    if key in self.is_producing and self.Value(self.is_producing[key]) == 1:
                        solution["is_producing"][line][date_key] = grade
                        break

        # Count transitions
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

        solution["transitions"] = {
            "per_line": transition_count_per_line,
            "total": total_transitions,
        }

        self.solutions.append(solution)

    def num_solutions(self):
        return len(self.solutions)


def _normalize_transition_rules(raw_rules: Dict[str, Any], grades: List[str]) -> Dict[str, Dict[str, Set[str]]]:
    """
    Normalize transition_rules into the shape:
      allowed_next[line][prev_grade] = set(of allowed next grades)

    Accepts raw rules in either:
    - { line: { prev_grade: [next_grade1, next_grade2, ...] } }
    - { line: { prev_grade: { next_grade: "Yes"/"No", ... } } }
    - If a line is missing or a prev_grade missing => treat 'all next grades allowed' (fallback).
    """
    normalized: Dict[str, Dict[str, Set[str]]] = {}

    for line, mapping in (raw_rules or {}).items():
        normalized[line] = {}
        if mapping is None:
            # allow all transitions by default for this line
            for g in grades:
                normalized[line][g] = set(grades)
            continue

        # mapping expected as dict(prev -> either list or dict)
        for prev_grade in grades:
            entry = mapping.get(prev_grade)
            if entry is None:
                # If prev_grade not specified, allow all next grades by default
                normalized[line][prev_grade] = set(grades)
                continue

            if isinstance(entry, dict):
                # entry is next_grade -> "Yes"/"No" or truthy/falsy
                allowed = set()
                for nxt, val in entry.items():
                    if isinstance(val, str):
                        if val.strip().lower() == "yes":
                            allowed.add(nxt)
                    else:
                        # truthy value indicates allowed
                        if val:
                            allowed.add(nxt)
                normalized[line][prev_grade] = allowed
            elif isinstance(entry, (list, set, tuple)):
                # explicit list of allowed next grades
                normalized[line][prev_grade] = set(entry)
            else:
                # Unknown shape: fallback to allowing all
                normalized[line][prev_grade] = set(grades)

    return normalized


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
    transition_rules: Dict,
    buffer_days: int,
    stockout_penalty: int,
    transition_penalty: int,
    continuity_bonus: int,
    time_limit_min: int,
    progress_callback=None,
) -> Tuple[int, SolutionCallback, cp_model.CpSolver]:
    """Build and solve the optimization model"""

    if progress_callback:
        progress_callback(0.0, "Building optimization model...")

    model = cp_model.CpModel()

    # Decision variables
    is_producing: Dict[Tuple[str, str, int], cp_model.IntVar] = {}
    production: Dict[Tuple[str, str, int], cp_model.IntVar] = {}

    def is_allowed_combination(grade: str, line: str) -> bool:
        return line in allowed_lines.get(grade, [])

    # Create production variables
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f"is_producing_{grade}_{line}_{d}")

                # Production value bound / link to is_producing
                production_value = model.NewIntVar(0, capacities[line], f"production_{grade}_{line}_{d}")
                if d < num_days - buffer_days:
                    # full capacity if producing
                    model.Add(production_value == capacities[line]).OnlyEnforceIf(is_producing[key])
                    model.Add(production_value == 0).OnlyEnforceIf(is_producing[key].Not())
                else:
                    model.Add(production_value <= capacities[line] * is_producing[key])
                production[key] = production_value

    # Helper to safely fetch variables
    def get_production_var(grade: str, line: str, d: int):
        return production.get((grade, line, d), None)

    def get_is_producing_var(grade: str, line: str, d: int):
        return is_producing.get((grade, line, d), None)

    if progress_callback:
        progress_callback(0.1, "Adding shutdown constraints...")

    # Shutdown constraints
    for line in lines:
        if line in (shutdown_periods or {}) and shutdown_periods[line]:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        key = (grade, line, d)
                        if key in is_producing:
                            model.Add(is_producing[key] == 0)
                            model.Add(production[key] == 0)

    if progress_callback:
        progress_callback(0.2, "Adding inventory constraints...")

    # Inventory variables
    inventory_vars: Dict[Tuple[str, int], cp_model.IntVar] = {}
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 100000, f"inventory_{grade}_{d}")

    stockout_vars: Dict[Tuple[str, int], cp_model.IntVar] = {}
    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 100000, f"stockout_{grade}_{d}")

    # One grade per line per day
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

    # Material running constraints
    for plant, (material, expected_days) in (material_running_info or {}).items():
        for d in range(min(expected_days, num_days)):
            if is_allowed_combination(material, plant):
                var = get_is_producing_var(material, plant, d)
                if var is not None:
                    model.Add(var == 1)
                    for other_material in grades:
                        if other_material != material and is_allowed_combination(other_material, plant):
                            other_var = get_is_producing_var(other_material, plant, d)
                            if other_var is not None:
                                model.Add(other_var == 0)

    if progress_callback:
        progress_callback(0.3, "Adding inventory balance constraints...")

    # Inventory balance and objective initialization
    objective = 0

    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == int(initial_inventory.get(grade, 0)))

    for grade in grades:
        for d in range(num_days):
            produced_today = sum(
                get_production_var(grade, line, d) or 0
                for line in allowed_lines.get(grade, [])
            )
            demand_today = demand_data.get(grade, {}).get(dates[d], 0)

            supplied = model.NewIntVar(0, 100000, f"supplied_{grade}_{d}")
            model.Add(supplied <= inventory_vars[(grade, d)] + produced_today)
            model.Add(supplied <= demand_today)

            model.Add(stockout_vars[(grade, d)] == demand_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)

    if progress_callback:
        progress_callback(0.4, "Adding minimum inventory constraints...")

    # Minimum inventory (soft via objective)
    for grade in grades:
        for d in range(num_days):
            if min_inventory.get(grade, 0) > 0:
                min_inv_value = int(min_inventory[grade])
                inventory_tomorrow = inventory_vars[(grade, d + 1)]
                deficit = model.NewIntVar(0, 100000, f"deficit_{grade}_{d}")
                model.Add(deficit >= min_inv_value - inventory_tomorrow)
                model.Add(deficit >= 0)
                objective += stockout_penalty * deficit

    # Minimum closing inventory (ex. near horizon)
    for grade in grades:
        closing_day_index = max(0, num_days - 1 - buffer_days)
        closing_inventory = inventory_vars[(grade, closing_day_index)]
        min_closing = min_closing_inventory.get(grade, 0)

        if min_closing > 0:
            closing_deficit = model.NewIntVar(0, 100000, f"closing_deficit_{grade}")
            model.Add(closing_deficit >= min_closing - closing_inventory)
            model.Add(closing_deficit >= 0)
            objective += stockout_penalty * closing_deficit * 3

    # Maximum inventory
    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= int(max_inventory.get(grade, 100000)))

    if progress_callback:
        progress_callback(0.5, "Adding capacity constraints...")

    # Capacity constraints
    for line in lines:
        for d in range(num_days - buffer_days):
            if line in (shutdown_periods or {}) and d in shutdown_periods[line]:
                continue
            production_vars = [
                get_production_var(grade, line, d) or 0
                for grade in grades
                if is_allowed_combination(grade, line)
            ]
            if production_vars:
                model.Add(sum(production_vars) == capacities[line])

        for d in range(num_days - buffer_days, num_days):
            production_vars = [
                get_production_var(grade, line, d) or 0
                for grade in grades
                if is_allowed_combination(grade, line)
            ]
            if production_vars:
                model.Add(sum(production_vars) <= capacities[line])

    if progress_callback:
        progress_callback(0.6, "Adding run constraints...")

    # Force start date constraints
    for grade_plant_key, start_date in (force_start_date or {}).items():
        if start_date:
            grade, plant = grade_plant_key
            try:
                start_day_index = dates.index(start_date)
                var = get_is_producing_var(grade, plant, start_day_index)
                if var is not None:
                    model.Add(var == 1)
            except ValueError:
                pass

    # Min/Max run days
    is_start_vars: Dict[Tuple[str, str, int], cp_model.BoolVar] = {}
    run_end_vars: Dict[Tuple[str, str, int], cp_model.BoolVar] = {}

    for grade in grades:
        for line in allowed_lines.get(grade, []):
            grade_plant_key = (grade, line)
            min_run = min_run_days.get(grade_plant_key, 1)
            max_run = max_run_days.get(grade_plant_key, 9999)

            for d in range(num_days):
                is_start = model.NewBoolVar(f"start_{grade}_{line}_{d}")
                is_start_vars[(grade, line, d)] = is_start

                is_end = model.NewBoolVar(f"end_{grade}_{line}_{d}")
                run_end_vars[(grade, line, d)] = is_end

                current_prod = get_is_producing_var(grade, line, d)

                if d > 0:
                    prev_prod = get_is_producing_var(grade, line, d - 1)
                    if current_prod is not None and prev_prod is not None:
                        # is_start <=> current_prod == 1 and prev_prod == 0
                        model.AddBoolAnd([current_prod, prev_prod.Not()]).OnlyEnforceIf(is_start)
                        model.AddBoolOr([current_prod.Not(), prev_prod, is_start.Not()])
                else:
                    if current_prod is not None:
                        model.Add(current_prod == 1).OnlyEnforceIf(is_start)
                        model.Add(is_start == 1).OnlyEnforceIf(current_prod)

                if d < num_days - 1:
                    next_prod = get_is_producing_var(grade, line, d + 1)
                    if current_prod is not None and next_prod is not None:
                        model.AddBoolAnd([current_prod, next_prod.Not()]).OnlyEnforceIf(is_end)
                        model.AddBoolOr([current_prod.Not(), next_prod, is_end.Not()])
                else:
                    if current_prod is not None:
                        model.Add(current_prod == 1).OnlyEnforceIf(is_end)
                        model.Add(is_end == 1).OnlyEnforceIf(current_prod)

            # Minimum run days
            for d in range(num_days):
                is_start = is_start_vars[(grade, line, d)]
                max_possible_run = 0
                for k in range(min_run):
                    if d + k < num_days:
                        if line in (shutdown_periods or {}) and (d + k) in shutdown_periods[line]:
                            break
                        max_possible_run += 1

                if max_possible_run >= min_run:
                    for k in range(min_run):
                        if d + k < num_days:
                            if line in (shutdown_periods or {}) and (d + k) in shutdown_periods[line]:
                                continue
                            future_prod = get_is_producing_var(grade, line, d + k)
                            if future_prod is not None:
                                model.Add(future_prod == 1).OnlyEnforceIf(is_start)

            # Maximum run days
            if max_run < 9999:
                for d in range(num_days - max_run):
                    consecutive_days = []
                    for k in range(max_run + 1):
                        if d + k < num_days:
                            if line in (shutdown_periods or {}) and (d + k) in shutdown_periods[line]:
                                break
                            prod_var = get_is_producing_var(grade, line, d + k)
                            if prod_var is not None:
                                consecutive_days.append(prod_var)

                    if len(consecutive_days) == max_run + 1:
                        model.Add(sum(consecutive_days) <= max_run)

    if progress_callback:
        progress_callback(0.7, "Adding transition constraints...")

    # ---- Normalize transition rules to allowed_next[line][prev] = set(next_grades)
    allowed_next = _normalize_transition_rules(transition_rules, grades)

    # ---- HARD FORBIDDANCE: block any (prev at d) AND (next at d+1) if next is forbidden
    for line in lines:
        line_rules = allowed_next.get(line, None)
        if line_rules is None:
            # If no rules for this line, assume all transitions allowed
            continue

        for d in range(num_days - 1):
            for prev_grade in grades:
                # only consider prev grades allowed on this line
                if not is_allowed_combination(prev_grade, line):
                    continue
                prev_var = get_is_producing_var(prev_grade, line, d)
                if prev_var is None:
                    continue

                allowed_set = line_rules.get(prev_grade, set(grades))

                for next_grade in grades:
                    if next_grade == prev_grade:
                        continue
                    if not is_allowed_combination(next_grade, line):
                        continue
                    next_var = get_is_producing_var(next_grade, line, d + 1)
                    if next_var is None:
                        continue

                    # If next_grade is not allowed after prev_grade -> forbid prev_var=1 AND next_var=1
                    if next_grade not in allowed_set:
                        model.Add(prev_var + next_var <= 1)

    # ---- TRANSITION PENALTIES: create trans_var for allowed transitions and penalize them
    for line in lines:
        line_rules = allowed_next.get(line, None)
        # If no rules for the line, treat everything allowed (penalize all grade changes)
        for d in range(num_days - 1):
            for g1 in grades:
                if not is_allowed_combination(g1, line):
                    continue
                var_g1 = get_is_producing_var(g1, line, d)
                if var_g1 is None:
                    continue

                for g2 in grades:
                    if g1 == g2:
                        continue
                    if not is_allowed_combination(g2, line):
                        continue
                    var_g2 = get_is_producing_var(g2, line, d + 1)
                    if var_g2 is None:
                        continue

                    # Check rule: only create penalty var if this transition is allowed
                    allowed_set = line_rules.get(g1, set(grades)) if line_rules is not None else set(grades)
                    if g2 not in allowed_set:
                        # forbidden transitions already blocked by hard constraint above
                        continue

                    trans_var = model.NewBoolVar(f"trans_{line}_{d}_{g1}_to_{g2}")

                    # trans_var <-> (var_g1 AND var_g2)
                    # If trans_var is true => var_g1 and var_g2 must be true
                    model.AddBoolAnd([var_g1, var_g2]).OnlyEnforceIf(trans_var)
                    # If both var_g1 and var_g2 are true => trans_var must be true
                    model.AddBoolOr([var_g1.Not(), var_g2.Not(), trans_var])

                    objective += transition_penalty * trans_var

            # continuity bonus for same grade day-to-day
            for grade in grades:
                if not is_allowed_combination(grade, line):
                    continue
                v_today = get_is_producing_var(grade, line, d)
                v_tomorrow = get_is_producing_var(grade, line, d + 1)
                if v_today is None or v_tomorrow is None:
                    continue
                continuity = model.NewBoolVar(f"continuity_{line}_{d}_{grade}")
                model.AddBoolAnd([v_today, v_tomorrow]).OnlyEnforceIf(continuity)
                model.AddBoolOr([v_today.Not(), v_tomorrow.Not(), continuity])
                objective += -continuity_bonus * continuity

    if progress_callback:
        progress_callback(0.8, "Building objective function...")

    # Stockout penalties
    for grade in grades:
        for d in range(num_days):
            objective += stockout_penalty * stockout_vars[(grade, d)]

    model.Minimize(objective)

    if progress_callback:
        progress_callback(0.9, "Solving optimization problem...")

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60.0
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED
    solver.parameters.log_search_progress = True

    solution_callback = SolutionCallback(
        production, inventory_vars, stockout_vars, is_producing, grades, lines, dates, formatted_dates, num_days
    )

    status = solver.Solve(model, solution_callback)

    if progress_callback:
        progress_callback(1.0, "Optimization complete!")

    return status, solution_callback, solver
