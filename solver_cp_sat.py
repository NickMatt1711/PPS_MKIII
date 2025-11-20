"""
CP-SAT Solver Module
====================

Implements the EXACT solver logic with CORRECTED transition logic:
1. Forbidden transitions ("No") are HARD CONSTRAINTS.
2. Transition penalty only applies to VALID transitions.
"""

import time
from typing import Dict, Any
from ortools.sat.python import cp_model


def solve(instance: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    # Extract parameters
    buffer_days = parameters.get('buffer_days', 3)
    time_limit_min = parameters.get('time_limit_min', 10)
    stockout_penalty = parameters.get('stockout_penalty', 10)
    transition_penalty = parameters.get('transition_penalty', 50)

    # Extract problem data
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = instance['num_days']
    capacities = instance['capacities']
    demand_data = instance['demand_data']
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
    transition_rules = instance['transition_rules']
    material_running_info = instance['material_running_info']

    model = cp_model.CpModel()

    # -------------------------
    # Variables
    # -------------------------
    is_producing = {}
    production = {}

    def is_allowed_combination(grade, line):
        return line in allowed_lines.get(grade, [])

    for grade in grades:
        for line in allowed_lines[grade]:
            for d in range(num_days):
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')

                if d < num_days - buffer_days:
                    prod_var = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                    model.Add(prod_var == capacities[line]).OnlyEnforceIf(is_producing[key])
                    model.Add(prod_var == 0).OnlyEnforceIf(is_producing[key].Not())
                else:
                    prod_var = model.NewIntVar(0, capacities[line], f'production_{grade}_{line}_{d}')
                    model.Add(prod_var <= capacities[line] * is_producing[key])

                production[key] = prod_var

    def get_production_var(grade, line, d):
        return production.get((grade, line, d), 0)

    def get_is_producing_var(grade, line, d):
        return is_producing.get((grade, line, d), None)

    # -------------------------
    # Shutdown constraints
    # -------------------------
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            for d in shutdown_periods[line]:
                for grade in grades:
                    if is_allowed_combination(grade, line):
                        key = (grade, line, d)
                        if key in is_producing:
                            model.Add(is_producing[key] == 0)
                            model.Add(production[key] == 0)

    # -------------------------
    # Inventory & stockout
    # -------------------------
    inventory_vars = {}
    stockout_vars = {}
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 100000, f'inventory_{grade}_{d}')
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 100000, f'stockout_{grade}_{d}')
        model.Add(inventory_vars[(grade, 0)] == initial_inventory[grade])

    for grade in grades:
        for d in range(num_days):
            produced_today = sum(get_production_var(grade, line, d) for line in allowed_lines[grade])
            demand_today = demand_data[grade].get(dates[d], 0)

            supplied = model.NewIntVar(0, 100000, f'supplied_{grade}_{d}')
            model.Add(supplied <= inventory_vars[(grade, d)] + produced_today)
            model.Add(supplied <= int(demand_today))
            model.Add(stockout_vars[(grade, d)] == int(demand_today) - supplied)
            model.Add(inventory_vars[(grade, d + 1)] == inventory_vars[(grade, d)] + produced_today - supplied)
            model.Add(inventory_vars[(grade, d + 1)] >= 0)

    # -------------------------
    # One grade per line per day
    # -------------------------
    for line in lines:
        for d in range(num_days):
            vars_today = [get_is_producing_var(grade, line, d)
                          for grade in grades if is_allowed_combination(grade, line)]
            if vars_today:
                model.Add(sum(vars_today) <= 1)

    # -------------------------
    # Forbidden transitions (Yes/No) - HARD CONSTRAINTS
    # -------------------------
    for line in lines:
        rules = transition_rules.get(line)
        if not rules:
            continue
        for d in range(num_days - 1):
            for prev_grade in grades:
                for next_grade in grades:
                    if prev_grade == next_grade:
                        continue
                    allowed = rules.get(prev_grade, {}).get(next_grade, "Yes")
                    if allowed == "No":
                        prev_var = get_is_producing_var(prev_grade, line, d)
                        next_var = get_is_producing_var(next_grade, line, d + 1)
                        if prev_var is not None and next_var is not None:
                            model.AddBoolOr([prev_var.Not(), next_var.Not()])

    # -------------------------
    # Objective: minimize valid transitions + stockouts + inventory deficits
    # -------------------------
    objective = 0

    # Min inventory deficit penalties
    for grade in grades:
        for d in range(num_days):
            min_inv = min_inventory.get(grade, 0)
            if min_inv > 0:
                deficit = model.NewIntVar(0, 100000, f'deficit_{grade}_{d}')
                model.Add(deficit >= min_inv - inventory_vars[(grade, d + 1)])
                model.Add(deficit >= 0)
                objective += stockout_penalty * deficit

    # Closing inventory
    for grade in grades:
        min_closing = min_closing_inventory.get(grade, 0)
        if min_closing > 0:
            closing_deficit = model.NewIntVar(0, 100000, f'closing_deficit_{grade}')
            model.Add(closing_deficit >= min_closing - inventory_vars[(grade, num_days - buffer_days)])
            model.Add(closing_deficit >= 0)
            objective += stockout_penalty * closing_deficit * 3

    # Max inventory
    for grade in grades:
        for d in range(1, num_days + 1):
            model.Add(inventory_vars[(grade, d)] <= max_inventory[grade])

    # -------------------------
    # Transitions penalty (minimize valid transitions)
    # -------------------------
    transition_vars = []
    for line in lines:
        for d in range(num_days - 1):
            trans_var = model.NewBoolVar(f'transition_{line}_{d}')
            prev_day_vars = [get_is_producing_var(g, line, d) for g in grades if is_allowed_combination(g, line)]
            next_day_vars = [get_is_producing_var(g, line, d + 1) for g in grades if is_allowed_combination(g, line)]
            # Only continue if vars exist
            prev_day_vars = [v for v in prev_day_vars if v is not None]
            next_day_vars = [v for v in next_day_vars if v is not None]
            if prev_day_vars and next_day_vars:
                same_grade = []
                for g in grades:
                    if not is_allowed_combination(g, line):
                        continue
                    var_prev = get_is_producing_var(g, line, d)
                    var_next = get_is_producing_var(g, line, d + 1)
                    if var_prev is not None and var_next is not None:
                        cont = model.NewBoolVar(f'continue_{line}_{d}_{g}')
                        model.AddBoolAnd([var_prev, var_next]).OnlyEnforceIf(cont)
                        model.AddBoolOr([var_prev.Not(), var_next.Not()]).OnlyEnforceIf(cont.Not())
                        same_grade.append(cont)
                if same_grade:
                    continuity = model.NewBoolVar(f'continuity_{line}_{d}')
                    model.AddMaxEquality(continuity, same_grade)
                    # Transition occurs if producing both days AND continuity == 0
                    prod_prev = model.NewBoolVar(f'prod_prev_{line}_{d}')
                    prod_next = model.NewBoolVar(f'prod_next_{line}_{d}')
                    model.AddMaxEquality(prod_prev, prev_day_vars)
                    model.AddMaxEquality(prod_next, next_day_vars)
                    model.AddBoolAnd([prod_prev, prod_next, continuity.Not()]).OnlyEnforceIf(trans_var)
                    model.AddBoolOr([prod_prev.Not(), prod_next.Not(), continuity]).OnlyEnforceIf(trans_var.Not())
                    transition_vars.append(trans_var)
            else:
                model.Add(trans_var == 0)

    # Add transition penalty to objective
    for t in transition_vars:
        objective += transition_penalty * t

    # Stockout penalties
    for grade in grades:
        for d in range(num_days):
            objective += stockout_penalty * stockout_vars[(grade, d)]

    model.Minimize(objective)

    # -------------------------
    # Solve
    # -------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 42
    solver.parameters.log_search_progress = True

    class SolutionCallback(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.solutions = []
            self.start_time = time.time()

        def on_solution_callback(self):
            elapsed = time.time() - self.start_time
            self.solutions.append({'objective': self.ObjectiveValue(), 'time': elapsed})

    callback = SolutionCallback()
    start_time = time.time()
    status = solver.Solve(model, callback)
    runtime = time.time() - start_time

    return {
        'status': solver.StatusName(status),
        'solver': solver,
        'solutions': callback.solutions,
        'runtime': runtime,
    }
