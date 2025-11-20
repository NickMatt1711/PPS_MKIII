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
        self.start_time = time.time()

    def on_solution_callback(self):
        current_time = time.time() - self.start_time
        solution = {
            'objective': self.ObjectiveValue(),
            'time': current_time,
            'production': {},
            'inventory': {},
            'stockout': {},
            'schedule': {},
            'transitions': {}
        }

        # Inventory and stockouts
        for grade in self.grades:
            solution['inventory'][grade] = {
                'initial': self.Value(self.inventory[(grade, 0)]),
                'daily': [self.Value(self.inventory[(grade, d)]) for d in range(1, self.num_days + 1)]
            }
            solution['stockout'][grade] = [self.Value(self.stockout[(grade, d)]) for d in range(self.num_days)]

        # Production schedule per plant
        transition_count_per_line = {line: 0 for line in self.lines}
        total_transitions = 0
        for line in self.lines:
            runs = []
            current_grade = None
            start_day = None
            for d in range(self.num_days):
                active_grade = None
                for grade in self.grades:
                    if (grade, line, d) in self.is_producing and self.Value(self.is_producing[(grade, line, d)]) == 1:
                        active_grade = grade
                        break
                if active_grade != current_grade:
                    if current_grade is not None:
                        runs.append({
                            'grade': current_grade,
                            'start': self.formatted_dates[start_day],
                            'end': self.formatted_dates[d - 1],
                            'days': (d - start_day)
                        })
                        if active_grade is not None:
                            transition_count_per_line[line] += 1
                            total_transitions += 1
                    current_grade = active_grade
                    start_day = d if active_grade else None
            if current_grade is not None:
                runs.append({
                    'grade': current_grade,
                    'start': self.formatted_dates[start_day],
                    'end': self.formatted_dates[self.num_days - 1],
                    'days': (self.num_days - start_day)
                })
            solution['schedule'][line] = runs

        solution['transitions'] = {'per_line': transition_count_per_line, 'total': total_transitions}
        self.solutions.append(solution)

    def num_solutions(self):
        return len(self.solutions)


# -----------------------------
# Main Solver Function
# -----------------------------
def solve(instance: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    # Extract parameters
    time_limit_min = parameters.get('time_limit_min', 10)
    stockout_penalty = parameters.get('stockout_penalty', 10)
    transition_penalty = parameters.get('transition_penalty', 10)

    # Extract instance data
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
    is_start_vars = {}
    is_end_vars = {}

    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])

    # Production and is_producing
    for grade in grades:
        for line in allowed_lines[grade]:
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                production_value = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                model.Add(production_value <= capacities[line] * is_producing[key])
                production[key] = production_value

    # Inventory and stockouts
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 100000, f'inventory_{grade}_{d}')
    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 100000, f'stockout_{grade}_{d}')

    # Initial inventory
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == initial_inventory[grade])

    # Inventory balance
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

    # Shutdown constraints
    for line in lines:
        if line in shutdown_periods:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        model.Add(is_producing[(grade, line, d)] == 0)
                        model.Add(production[(grade, line, d)] == 0)

    # Capacity constraints
    for line in lines:
        for d in range(num_days):
            model.Add(sum(production[(grade, line, d)] for grade in grades if is_allowed_combination(grade, line)) <= capacities[line])

    # Inventory limits
    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= max_inventory[grade])

    # Force start dates
    for (grade, plant), start_date in force_start_date.items():
        if start_date and plant in lines:
            try:
                start_day_index = dates.index(start_date)
                model.Add(is_producing[(grade, plant, start_day_index)] == 1)
            except ValueError:
                pass

    # Material running info
    for plant, (material, expected_days) in material_running_info.items():
        for d in range(min(expected_days, num_days)):
            if is_allowed_combination(material, plant):
                model.Add(is_producing[(material, plant, d)] == 1)

    # Min/Max run days
    for grade in grades:
        for line in allowed_lines[grade]:
            for d in range(num_days):
                is_start = model.NewBoolVar(f'start_{grade}_{line}_{d}')
                is_end = model.NewBoolVar(f'end_{grade}_{line}_{d}')
                is_start_vars[(grade, line, d)] = is_start
                is_end_vars[(grade, line, d)] = is_end

                current = is_producing[(grade, line, d)]
                prev = is_producing.get((grade, line, d - 1), None)
                next_ = is_producing.get((grade, line, d + 1), None)

                if prev:
                    model.AddBoolAnd([current, prev.Not()]).OnlyEnforceIf(is_start)
                    model.AddBoolOr([current.Not(), prev]).OnlyEnforceIf(is_start.Not())
                else:
                    model.Add(is_start == current)

                if next_:
                    model.AddBoolAnd([current, next_.Not()]).OnlyEnforceIf(is_end)
                    model.AddBoolOr([current.Not(), next_]).OnlyEnforceIf(is_end.Not())
                else:
                    model.Add(is_end == current)

            # Enforce min run days
            min_run = min_run_days.get((grade, line), 1)
            for d in range(num_days):
                if d + min_run <= num_days:
                    for k in range(min_run):
                        if (grade, line, d + k) in is_producing:
                            model.Add(is_producing[(grade, line, d + k)] == 1).OnlyEnforceIf(is_start_vars[(grade, line, d)])

            # Enforce max run days
            max_run = max_run_days.get((grade, line), 9999)
            for d in range(num_days - max_run):
                consecutive = [is_producing[(grade, line, d + k)] for k in range(max_run + 1) if (grade, line, d + k) in is_producing]
                if len(consecutive) == max_run + 1:
                    model.Add(sum(consecutive) <= max_run)

    # Rerun restrictions
    for grade in grades:
        for line in allowed_lines[grade]:
            if not rerun_allowed.get((grade, line), True):
                starts = [is_start_vars[(grade, line, d)] for d in range(num_days)]
                model.Add(sum(starts) <= 1)

    # Transition rules
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
    }
