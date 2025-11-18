"""
CP-SAT Solver Module
====================

Advanced constraint programming solver using OR-Tools CP-SAT for polymer production scheduling.
"""

import time
from typing import Dict, List, Any, Set
from ortools.sat.python import cp_model

import constants


class ProductionSolutionCallback(cp_model.CpSolverSolutionCallback):
    """
    Solution callback to capture intermediate and final solutions during solving.
    """
    
    def __init__(self, variables: Dict, instance: Dict, parameters: Dict):
        """
        Initialize callback with problem variables and data.
        
        Args:
            variables: Dict containing all model variables
            instance: Problem instance data
            parameters: Solver parameters
        """
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.variables = variables
        self.instance = instance
        self.parameters = parameters
        self.solutions = []
        self.start_time = time.time()
    
    def on_solution_callback(self):
        """Called by solver when a new solution is found."""
        current_time = time.time() - self.start_time
        
        solution = {
            'time': current_time,
            'objective': self.ObjectiveValue(),
            'assign': {},
            'production': {},
            'inventory': {},
            'unmet': {},
        }
        
        # Extract assignment (which grade on which line each day)
        for (line, d, grade), var in self.variables['assign'].items():
            if self.Value(var) == 1:
                solution['assign'][(line, d)] = grade
        
        # Extract production quantities
        for (line, d, grade), var in self.variables['production'].items():
            val = self.Value(var)
            if val > 0:
                solution['production'].setdefault((line, d), {})[grade] = val
        
        # Extract inventory levels
        for (grade, d), var in self.variables['inventory'].items():
            solution['inventory'][(grade, d)] = self.Value(var)
        
        # Extract unmet demand
        for (grade, d), var in self.variables['unmet'].items():
            val = self.Value(var)
            if val > 0:
                solution['unmet'][(grade, d)] = val
        
        self.solutions.append(solution)


def solve(instance: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Solve the polymer production scheduling problem using CP-SAT.
    
    Args:
        instance: Problem instance from data_loader
        parameters: Solver parameters including:
            - time_limit_min: Maximum runtime in minutes
            - stockout_penalty: Cost per unit of unmet demand
            - transition_penalty: Cost per grade changeover
            - num_search_workers: Number of parallel workers
            
    Returns:
        Dict containing:
            - status: Solver status string
            - solver: CP-SAT solver object
            - solutions: List of all solutions found
            - best: Best solution found (or None)
            - runtime: Total solving time
    """
    start_time = time.time()
    
    # Extract problem data
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = len(dates)
    
    # Create model
    model = cp_model.CpModel()
    
    # Build variables
    variables = _create_variables(model, instance)
    
    # Add constraints
    _add_assignment_constraints(model, variables, instance)
    _add_capacity_constraints(model, variables, instance)
    _add_inventory_constraints(model, variables, instance)
    _add_shutdown_constraints(model, variables, instance)
    _add_transition_constraints(model, variables, instance)
    _add_run_length_constraints(model, variables, instance)
    _add_rerun_constraints(model, variables, instance)
    _add_force_start_constraints(model, variables, instance)
    _add_material_running_constraints(model, variables, instance)
    
    # Set objective
    _set_objective(model, variables, instance, parameters)
    
    # Configure solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = parameters.get('time_limit_min', 10) * 60.0
    solver.parameters.num_search_workers = parameters.get('num_search_workers', constants.DEFAULT_NUM_SEARCH_WORKERS)
    solver.parameters.random_seed = constants.DEFAULT_RANDOM_SEED
    solver.parameters.log_search_progress = True
    
    # Solve with callback
    callback = ProductionSolutionCallback(variables, instance, parameters)
    status = solver.Solve(model, callback)
    
    runtime = time.time() - start_time
    
    # Prepare result
    result = {
        'status': solver.StatusName(status),
        'solver': solver,
        'solutions': callback.solutions,
        'best': callback.solutions[-1] if callback.solutions else None,
        'runtime': runtime,
        'num_solutions': len(callback.solutions),
    }
    
    return result


def _create_variables(model: cp_model.CpModel, instance: Dict) -> Dict:
    """Create all decision variables for the model."""
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = len(dates)
    
    variables = {
        'assign': {},
        'production': {},
        'inventory': {},
        'unmet': {},
        'prod_day': {},
        'changed': {},
        'has_continuity': {},
        'is_start': {},
    }
    
    # Assignment variables: assign[(line, d, grade)] = 1 if grade assigned to line on day d
    for line in lines:
        for d in range(num_days):
            for grade in grades:
                if line in instance['allowed_lines'].get(grade, []):
                    var = model.NewBoolVar(f'assign_{line}_{d}_{grade}')
                    variables['assign'][(line, d, grade)] = var
    
    # Production variables: production[(line, d, grade)] = quantity produced
    for (line, d, grade), _ in variables['assign'].items():
        capacity = int(instance['capacities'][line])
        var = model.NewIntVar(0, capacity, f'production_{line}_{d}_{grade}')
        variables['production'][(line, d, grade)] = var
    
    # Inventory variables: inventory[(grade, d)] = inventory level
    for grade in grades:
        for d in range(num_days + 1):
            var = model.NewIntVar(0, 10**9, f'inventory_{grade}_{d}')
            variables['inventory'][(grade, d)] = var
    
    # Unmet demand variables: unmet[(grade, d)] = stockout quantity
    for grade in grades:
        for d in range(num_days):
            var = model.NewIntVar(0, 10**9, f'unmet_{grade}_{d}')
            variables['unmet'][(grade, d)] = var
    
    # Production day indicators: prod_day[(line, d)] = 1 if line produces anything on day d
    for line in lines:
        for d in range(num_days):
            var = model.NewBoolVar(f'prod_day_{line}_{d}')
            variables['prod_day'][(line, d)] = var
    
    # Grade change indicators: changed[(line, d)] = 1 if grade changes from day d to d+1
    for line in lines:
        for d in range(num_days - 1):
            var = model.NewBoolVar(f'changed_{line}_{d}')
            variables['changed'][(line, d)] = var
            
            cont_var = model.NewBoolVar(f'has_continuity_{line}_{d}')
            variables['has_continuity'][(line, d)] = cont_var
    
    # Campaign start indicators: is_start[(grade, line, d)] = 1 if campaign starts
    for grade in grades:
        for line in lines:
            for d in range(num_days):
                if (line, d, grade) in variables['assign']:
                    var = model.NewBoolVar(f'is_start_{grade}_{line}_{d}')
                    variables['is_start'][(grade, line, d)] = var
    
    return variables


def _add_assignment_constraints(model: cp_model.CpModel, variables: Dict, instance: Dict) -> None:
    """Ensure exactly one grade assigned per line per day."""
    lines = instance['lines']
    grades = instance['grades']
    num_days = len(instance['dates'])
    
    for line in lines:
        for d in range(num_days):
            assigns = [
                variables['assign'][(line, d, grade)]
                for grade in grades
                if (line, d, grade) in variables['assign']
            ]
            if assigns:
                model.Add(sum(assigns) == 1)


def _add_capacity_constraints(model: cp_model.CpModel, variables: Dict, instance: Dict) -> None:
    """Link production to assignment and enforce capacity limits."""
    lines = instance['lines']
    grades = instance['grades']
    num_days = len(instance['dates'])
    
    # Link production to assignment
    for (line, d, grade), prod_var in variables['production'].items():
        assign_var = variables['assign'][(line, d, grade)]
        capacity = int(instance['capacities'][line])
        
        # If assigned, can produce up to capacity; otherwise zero
        model.Add(prod_var <= capacity * assign_var)
    
    # Total production per line per day <= capacity
    for line in lines:
        for d in range(num_days):
            prods = [
                variables['production'][(line, d, grade)]
                for grade in grades
                if (line, d, grade) in variables['production']
            ]
            if prods:
                capacity = int(instance['capacities'][line])
                model.Add(sum(prods) <= capacity)


def _add_inventory_constraints(model: cp_model.CpModel, variables: Dict, instance: Dict) -> None:
    """Enforce inventory balance and bounds."""
    grades = instance['grades']
    dates = instance['dates']
    num_days = len(dates)
    
    for grade in grades:
        # Initial inventory
        init_inv = int(instance['initial_inventory'][grade])
        model.Add(variables['inventory'][(grade, 0)] == init_inv)
        
        # Inventory balance each day
        for d in range(num_days):
            # Production this day across all lines
            produced = sum(
                variables['production'][(line, d, grade)]
                for line in instance['allowed_lines'].get(grade, [])
                if (line, d, grade) in variables['production']
            )
            
            demand = int(instance['demand'].get((grade, d), 0))
            
            # Inventory evolution
            inv_today = variables['inventory'][(grade, d)]
            inv_tomorrow = variables['inventory'][(grade, d + 1)]
            unmet = variables['unmet'][(grade, d)]
            
            # Unmet demand calculation
            model.Add(unmet >= demand - (inv_today + produced))
            model.Add(unmet >= 0)
            
            # Next inventory
            model.Add(inv_tomorrow == inv_today + produced - demand + unmet)
            
            # Inventory bounds
            min_inv = int(instance['min_inventory'][grade])
            max_inv = int(instance['max_inventory'][grade])
            model.Add(inv_tomorrow >= 0)
            model.Add(inv_tomorrow <= max_inv)
        
        # Minimum closing inventory
        min_closing = int(instance['min_closing_inventory'][grade])
        if min_closing > 0:
            model.Add(variables['inventory'][(grade, num_days)] >= min_closing)


def _add_shutdown_constraints(model: cp_model.CpModel, variables: Dict, instance: Dict) -> None:
    """Prevent production during shutdown periods."""
    lines = instance['lines']
    grades = instance['grades']
    
    for line in lines:
        shutdown_days = instance['shutdown_day_indices'].get(line, set())
        for d in shutdown_days:
            for grade in grades:
                if (line, d, grade) in variables['assign']:
                    model.Add(variables['assign'][(line, d, grade)] == 0)
                if (line, d, grade) in variables['production']:
                    model.Add(variables['production'][(line, d, grade)] == 0)


def _add_transition_constraints(model: cp_model.CpModel, variables: Dict, instance: Dict) -> None:
    """Enforce grade transition rules."""
    lines = instance['lines']
    grades = instance['grades']
    num_days = len(instance['dates'])
    
    for line in lines:
        rules = instance['transition_rules'].get(line)
        if rules is None:
            continue
        
        for d in range(num_days - 1):
            for prev_grade in grades:
                allowed_next = rules.get(prev_grade, [])
                if allowed_next is None:
                    continue
                
                for curr_grade in grades:
                    if curr_grade == prev_grade:
                        continue
                    
                    # If transition not allowed, forbid this combination
                    if curr_grade not in allowed_next:
                        prev_key = (line, d, prev_grade)
                        curr_key = (line, d + 1, curr_grade)
                        
                        if prev_key in variables['assign'] and curr_key in variables['assign']:
                            model.Add(
                                variables['assign'][prev_key] + variables['assign'][curr_key] <= 1
                            )
    
    # Link continuity detection
    for line in lines:
        for d in range(num_days - 1):
            # Check if same grade continues
            same_bools = []
            for grade in grades:
                prev_key = (line, d, grade)
                next_key = (line, d + 1, grade)
                
                if prev_key in variables['assign'] and next_key in variables['assign']:
                    same = model.NewBoolVar(f'same_{line}_{d}_{grade}')
                    model.AddBoolAnd([
                        variables['assign'][prev_key],
                        variables['assign'][next_key]
                    ]).OnlyEnforceIf(same)
                    model.AddBoolOr([
                        variables['assign'][prev_key].Not(),
                        variables['assign'][next_key].Not()
                    ]).OnlyEnforceIf(same.Not())
                    same_bools.append(same)
            
            if same_bools:
                model.AddMaxEquality(variables['has_continuity'][(line, d)], same_bools)
            else:
                model.Add(variables['has_continuity'][(line, d)] == 0)
            
            # changed = producing both days AND not continuous
            prod_today = variables['prod_day'][(line, d)]
            prod_tomorrow = variables['prod_day'][(line, d + 1)]
            has_cont = variables['has_continuity'][(line, d)]
            changed = variables['changed'][(line, d)]
            
            model.AddBoolAnd([prod_today, prod_tomorrow, has_cont.Not()]).OnlyEnforceIf(changed)
            model.AddBoolOr([prod_today.Not(), prod_tomorrow.Not(), has_cont]).OnlyEnforceIf(changed.Not())
    
    # Link prod_day to assignment
    for line in lines:
        for d in range(num_days):
            assigns = [
                variables['assign'][(line, d, grade)]
                for grade in grades
                if (line, d, grade) in variables['assign']
            ]
            if assigns:
                model.AddMaxEquality(variables['prod_day'][(line, d)], assigns)
            else:
                model.Add(variables['prod_day'][(line, d)] == 0)


def _add_run_length_constraints(model: cp_model.CpModel, variables: Dict, instance: Dict) -> None:
    """Enforce minimum and maximum run day constraints."""
    grades = instance['grades']
    lines = instance['lines']
    num_days = len(instance['dates'])

    for grade in grades:
        for line in instance['allowed_lines'].get(grade, []):
            key = (grade, line)
            min_run = int(instance['min_run_days'].get(key, 1))
            max_run = int(instance['max_run_days'].get(key, 9999))

            # --- Detect campaign starts ---
            for d in range(num_days):
                if (grade, line, d) not in variables['is_start']:
                    continue

                is_start = variables['is_start'][(grade, line, d)]
                assign_today = variables['assign'].get((line, d, grade))

                if assign_today is None:
                    continue

                # Must be assigned to start
                model.Add(is_start <= assign_today)

                # Start if today's assignment is 1 and yesterday's is 0 or nonexistent
                if d == 0:
                    model.Add(is_start >= assign_today) 
                else:
                    prev_assign = variables['assign'].get((line, d - 1, grade))
                    if prev_assign is not None:
                        # start = 1 if today=1 and yesterday=0
                        model.Add(is_start >= assign_today - prev_assign)
                    else:
                        model.Add(is_start >= assign_today)

                # --- Enforce minimum run days ---
                if min_run > 1:
                    for offset in range(min_run):
                        day_index = d + offset
                        if day_index < num_days:
                            next_assign = variables['assign'].get((line, day_index, grade))
                            if next_assign is not None:
                                model.Add(next_assign == 1).OnlyEnforceIf(is_start)

            # --- Enforce maximum run days ---
            if max_run < num_days:
                for d in range(num_days - max_run):
                    consecutive = []
                    for offset in range(max_run + 1):
                        day_index = d + offset
                        assign_var = variables['assign'].get((line, day_index, grade))
                        if assign_var is not None:
                            consecutive.append(assign_var)

                    # If all days exist, enforce limit
                    if len(consecutive) == max_run + 1:
                        model.Add(sum(consecutive) <= max_run)


def _add_rerun_constraints(model: cp_model.CpModel, variables: Dict, instance: Dict) -> None:
    """Enforce rerun allowed restrictions."""
    grades = instance['grades']
    lines = instance['lines']
    num_days = len(instance['dates'])
    
    for grade in grades:
        for line in instance['allowed_lines'].get(grade, []):
            key = (grade, line)
            if not instance['rerun_allowed'].get(key, True):
                # Only one campaign allowed
                starts = [
                    variables['is_start'][(grade, line, d)]
                    for d in range(num_days)
                    if (grade, line, d) in variables['is_start']
                ]
                if starts:
                    model.Add(sum(starts) <= 1)


def _add_force_start_constraints(model: cp_model.CpModel, variables: Dict, instance: Dict) -> None:
    """Enforce force start date requirements."""
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    
    for grade, force_date in instance['force_start_date'].items():
        if force_date is None:
            continue
        
        # Find eligible day indices (on or after force_date)
        eligible_days = [i for i, d in enumerate(dates) if d >= force_date]
        
        if not eligible_days:
            # Force date outside horizon - add infeasible constraint
            model.Add(0 == 1)
            continue
        
        # Collect all possible start variables on eligible days
        eligible_starts = []
        for line in instance['allowed_lines'].get(grade, []):
            for d in eligible_days:
                if (grade, line, d) in variables['is_start']:
                    eligible_starts.append(variables['is_start'][(grade, line, d)])
        
        if eligible_starts:
            # Require at least one start on or after force date
            model.Add(sum(eligible_starts) >= 1)
        else:
            # No possible start -> infeasible
            model.Add(0 == 1)


def _add_material_running_constraints(model: cp_model.CpModel, variables: Dict, instance: Dict) -> None:
    """Enforce continuing material production from previous period."""
    num_days = len(instance['dates'])
    
    for line, (material, expected_days) in instance['material_running'].items():
        # Force this material to run for expected_days at start
        for d in range(min(expected_days, num_days)):
            if (line, d, material) in variables['assign']:
                model.Add(variables['assign'][(line, d, material)] == 1)


def _set_objective(model: cp_model.CpModel, variables: Dict, 
                   instance: Dict, parameters: Dict) -> None:
    """Set the optimization objective."""
    grades = instance['grades']
    lines = instance['lines']
    num_days = len(instance['dates'])
    
    stockout_penalty = int(parameters.get('stockout_penalty', 10))
    transition_penalty = int(parameters.get('transition_penalty', 50))
    
    objective_terms = []
    
    # Penalize unmet demand
    for grade in grades:
        for d in range(num_days):
            objective_terms.append(stockout_penalty * variables['unmet'][(grade, d)])
    
    # Penalize minimum inventory violations
    for grade in grades:
        min_inv = int(instance['min_inventory'][grade])
        if min_inv > 0:
            for d in range(1, num_days + 1):
                deficit = model.NewIntVar(0, 10**9, f'deficit_{grade}_{d}')
                model.Add(deficit >= min_inv - variables['inventory'][(grade, d)])
                model.Add(deficit >= 0)
                objective_terms.append(stockout_penalty * deficit)
    
    # Penalize grade transitions
    for line in lines:
        for d in range(num_days - 1):
            objective_terms.append(transition_penalty * variables['changed'][(line, d)])
    
    model.Minimize(sum(objective_terms))
