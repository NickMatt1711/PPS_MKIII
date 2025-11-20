from ortools.sat.python import cp_model
import time
from typing import Dict, Any

# -----------------------------
# Solution Callback
# -----------------------------
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
        self.solution_times = []
        self.start_time = time.time()

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
            'is_producing': {},
            'transitions': {}
        }

        # Production schedule
        for grade in self.grades:
            solution['production'][grade] = {}
            for line in self.lines:
                for d in range(self.num_days):
                    key = (grade, line, d)
                    if key in self.production:
                        value = self.Value(self.production[key])
                        if value > 0:
                            date_key = self.formatted_dates[d]
                            solution['production'][grade].setdefault(date_key, 0)
                            solution['production'][grade][date_key] += value

        # Inventory
        for grade in self.grades:
            solution['inventory'][grade] = {}
            for d in range(self.num_days + 1):
                key = (grade, d)
                if key in self.inventory:
                    if d < self.num_days:
                        solution['inventory'][grade][self.formatted_dates[d] if d > 0 else 'initial'] = self.Value(self.inventory[key])
                    else:
                        solution['inventory'][grade]['final'] = self.Value(self.inventory[key])

        # Stockouts
        for grade in self.grades:
            solution['stockout'][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.stockout:
                    value = self.Value(self.stockout[key])
                    if value > 0:
                        solution['stockout'][grade][self.formatted_dates[d]] = value

        # Schedule
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

        # Transitions
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
        solution['transitions'] = {'per_line': transition_count_per_line, 'total': total_transitions}

        self.solutions.append(solution)

    def num_solutions(self):
        return len(self.solutions)


# -----------------------------
# Main Solver Function
# -----------------------------
def solve(instance: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    time_limit_min = parameters.get('time_limit_min', 10)
    stockout_penalty = parameters.get('stockout_penalty', 10)
    transition_penalty = parameters.get('transition_penalty', 10)

    grades = instance['grades']
    lines = instance['lines']
    capacities = instance['capacities']
    demand_data = instance['demand_data']
    dates = instance['dates']
    formatted_dates = instance['formatted_dates']
    num_days = instance['num_days']
    initial_inventory = instance['initial_inventory']
    min_inventory = instance['min_inventory']
    max_inventory = instance['max_inventory']
    min_closing_inventory = instance['min_closing_inventory']
    min_run_days = instance['min_run_days']
    max_run_days = instance['max_run_days']
    force_start_date = instance['force_start_date']
    allowed_lines = instance['allowed_lines']
    rerun_allowed = instance['rerun_allowed']
    shutdown_periods = instance['shutdown_periods']
    material_running_info = instance['material_running_info']
    transition_rules = instance['transition_rules']

    model = cp_model.CpModel()

    # Variables
    is_producing = {}
    production = {}
    inventory_vars = {}
    stockout_vars = {}

    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])

    for grade in grades:
        for line in allowed_lines[grade]:
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                production_value = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                model.Add(production_value <= capacities[line] * is_producing[key])
                production[key] = production_value

    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 100000, f'inventory_{grade}_{d}')

    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 100000, f'stockout_{grade}_{d}')

    # Constraints
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == initial_inventory[grade])

    for grade in grades:
        for d in range(num_days):
            produced_today = sum(production[(grade, line, d)] for line in allowed_lines[grade])
            demand_today = demand_data[grade].get(dates[d], 0)
            supplied = model.NewIntVar(0, 100000, f'supplied_{grade}_{d}')
            model.Add(supplied <= inventory_vars[(grade, d)] + produced_today)
            model.Add(supplied <= demand_today)
            model.Add(stockout_vars[(grade, d)] == demand_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)

    for line in lines:
        if line in shutdown_periods:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        model.Add(is_producing[(grade, line, d)] == 0)
                        model.Add(production[(grade, line, d)] == 0)

    for line in lines:
        for d in range(num_days):
            model.Add(sum(production[(grade, line, d)] for grade in grades if is_allowed_combination(grade, line)) <= capacities[line])

    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= max_inventory[grade])

    for (grade, plant), start_date in force_start_date.items():
        if start_date and plant in lines:
            try:
                start_day_index = dates.index(start_date)
                model.Add(is_producing[(grade, plant, start_day_index)] == 1)
            except ValueError:
                pass

    for plant, (material, expected_days) in material_running_info.items():
        for d in range(min(expected_days, num_days)):
            if is_allowed_combination(material, plant):
                model.Add(is_producing[(material, plant, d)] == 1)

    for line in lines:
        if transition_rules.get(line):
            for d in range(num_days - 1):
                for prev_grade in grades:
                    if prev_grade in transition_rules[line] and is_allowed_combination(prev_grade, line):
                        allowed_next = transition_rules[line][prev_grade]
                        for current_grade in grades:
                            if current_grade != prev_grade and current_grade not in allowed_next and is_allowed_combination(current_grade, line):
                                prev_var = is_producing[(prev_grade, line, d)]
                                current_var = is_producing[(current_grade, line, d + 1)]
                                model.Add(prev_var + current_var <= 1)

    # Objective
    objective = 0
    for grade in grades:
        for d in range(num_days):
            objective += stockout_penalty * stockout_vars[(grade, d)]

    for line in lines:
        for d in range(num_days - 1):
            for grade1 in grades:
                if not is_allowed_combination(grade1, line):
                    continue
                for grade2 in grades:
                    if grade1 == grade2 or not is_allowed_combination(grade2, line):
                        continue
                    trans_var = model.NewBoolVar(f'trans_{line}_{d}_{grade1}_to_{grade2}')
                    model.AddBoolAnd([is_producing[(grade1, line, d)], is_producing[(grade2, line, d + 1)]]).OnlyEnforceIf(trans_var)
                    model.Add(trans_var == 0).OnlyEnforceIf(is_producing[(grade1, line, d)].Not())
                    model.Add(trans_var == 0).OnlyEnforceIf(is_producing[(grade2, line, d + 1)].Not())
                    objective += transition_penalty * trans_var

    model.Minimize(objective)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 42

    callback = SolutionCallback(production, inventory_vars, stockout_vars, is_producing, grades, lines, dates, formatted_dates, num_days)
    start_time = time.time()
    status = solver.Solve(model, callback)

    return {
        "status": solver.StatusName(status),
        "solutions": callback.solutions,
        "best": callback.solutions[-1] if callback.solutions else None,
        "runtime": time.time() - start_time
