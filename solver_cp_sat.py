"""
CP-SAT Solver for production optimization (IMPROVED VERSION)
All 10 accuracy fixes applied - Part 1: Core solver logic

IMPROVEMENTS APPLIED:
✓ FIX #1: Simplified inventory balance (AddMinEquality)
✓ FIX #2: Material running changeover timing with end_day tracking
✓ FIX #3: Run start definition excludes material running
✓ FIX #4: Transition pairs optimization (N²→N(N-1)/2 variables)
✓ FIX #5: No variables created for shutdown days
✓ FIX #6: Average demand normalization (not per-day)
✓ FIX #7: Min-run enforcement at horizon end
✓ FIX #8: Rerun constraint excludes forced material running
✓ FIX #9: Buffer days excluded from stockout penalties
✓ FIX #10: Idle penalty removed (redundant with capacity)
"""

from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED
import math


class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Callback to capture all solutions during search"""
    
    def __init__(self, production, inventory, stockout, is_producing, grades, lines, dates, 
                 formatted_dates, num_days, inventory_deficit_penalties=None, 
                 closing_inventory_deficit_penalties=None, run_starts=None, planning_days=None):
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
        self.planning_days = planning_days or num_days
        self.inventory_deficit_penalties = inventory_deficit_penalties or {}
        self.closing_inventory_deficit_penalties = closing_inventory_deficit_penalties or {}
        self.run_starts = run_starts or {}
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

        # Store production
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
        
        # Store inventory
        for grade in self.grades:
            solution['inventory'][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.inventory:
                    solution['inventory'][grade][self.formatted_dates[d]] = self.Value(self.inventory[key])
            final_key = (grade, self.num_days)
            if final_key in self.inventory:
                solution['inventory'][grade]['final'] = self.Value(self.inventory[final_key])
        
        # Store stockout (only planning days)
        for grade in self.grades:
            solution['stockout'][grade] = {}
            for d in range(self.planning_days):
                key = (grade, d)
                if key in self.stockout:
                    value = self.Value(self.stockout[key])
                    if value > 0:
                        solution['stockout'][grade][self.formatted_dates[d]] = value
        
        # Store schedule
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
        solution['transitions'] = {'per_line': transition_count_per_line, 'total': total_transitions}
        self.solutions.append(solution)

    def num_solutions(self):
        return len(self.solutions)


def build_and_solve_model(
    grades: List[str], lines: List[str], dates: List, formatted_dates: List[str],
    num_days: int, capacities: Dict, initial_inventory: Dict, min_inventory: Dict,
    max_inventory: Dict, min_closing_inventory: Dict, demand_data: Dict,
    allowed_lines: Dict, min_run_days: Dict, max_run_days: Dict,
    force_start_date: Dict, rerun_allowed: Dict, material_running_info: Dict,
    shutdown_periods: Dict, pre_shutdown_grades: Dict, restart_grades: Dict,
    transition_rules: Dict, buffer_days: int, stockout_penalty: int,
    transition_penalty: int, time_limit_min: int, penalty_method: str = "Standard",
    progress_callback=None
) -> Tuple[int, SolutionCallback, cp_model.CpSolver]:
    """Build and solve with all 10 accuracy improvements"""
    
    if progress_callback:
        progress_callback(0.0, "Building model...")
    
    model = cp_model.CpModel()
    
    # FIX #9: Planning days exclude buffer
    planning_days = num_days - buffer_days
    
    is_producing = {}
    production = {}
    run_starts = {}
    
    def is_allowed(grade, line):
        return line in allowed_lines.get(grade, [])
    
    # FIX #5: Don't create variables for shutdown days
    for grade in grades:
        for line in allowed_lines[grade]:
            for d in range(num_days):
                if line in shutdown_periods and d in shutdown_periods[line]:
                    continue  # Skip shutdown days entirely
                
                key = (grade, line, d)
                is_producing[key] = model.NewBoolVar(f'prod_{grade}_{line}_{d}')
                prod_val = model.NewIntVar(0, capacities[line], f'pval_{grade}_{line}_{d}')
                model.Add(prod_val == capacities[line]).OnlyEnforceIf(is_producing[key])
                model.Add(prod_val == 0).OnlyEnforceIf(is_producing[key].Not())
                production[key] = prod_val
                run_starts[key] = model.NewBoolVar(f'start_{grade}_{line}_{d}')
    
    def get_prod(g, l, d):
        return production.get((g, l, d), 0)
    
    def get_is_prod(g, l, d):
        return is_producing.get((g, l, d))
    
    if progress_callback:
        progress_callback(0.1, "Hard constraints...")
    
    # One grade per line per day
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            vars_list = [get_is_prod(g, line, d) for g in grades if is_allowed(g, line) and get_is_prod(g, line, d)]
            if vars_list:
                model.Add(sum(vars_list) <= 1)
    
    # FIX #2: Material running with end_day tracking
    material_map = {}
    for plant, (material, exp_days) in material_running_info.items():
        if is_allowed(material, plant):
            v0 = get_is_prod(material, plant, 0)
            if v0:
                model.Add(v0 == 1)
            for other in grades:
                if other != material and is_allowed(other, plant):
                    vo = get_is_prod(other, plant, 0)
                    if vo:
                        model.Add(vo == 0)
        
        if exp_days and exp_days > 0:
            forced = min(exp_days, num_days)
            for d in range(1, forced):
                if plant in shutdown_periods and d in shutdown_periods[plant]:
                    continue
                if d < num_days and is_allowed(material, plant):
                    v = get_is_prod(material, plant, d)
                    if v:
                        model.Add(v == 1)
                    for other in grades:
                        if other != material and is_allowed(other, plant):
                            vo = get_is_prod(other, plant, d)
                            if vo:
                                model.Add(vo == 0)
            material_map[plant] = {'material': material, 'expected_days': forced, 'end_day': forced - 1}
        else:
            material_map[plant] = {'material': material, 'expected_days': 1, 'end_day': 0}
    
    # Pre-shutdown/restart grades
    for line in lines:
        if line in shutdown_periods and shutdown_periods[line]:
            sd = shutdown_periods[line]
            if line in pre_shutdown_grades and pre_shutdown_grades[line]:
                pre = pre_shutdown_grades[line]
                if pre in grades and is_allowed(pre, line):
                    db = sd[0] - 1
                    if db >= 0:
                        v = get_is_prod(pre, line, db)
                        if v:
                            model.Add(v == 1)
                            for o in grades:
                                if o != pre and is_allowed(o, line):
                                    vo = get_is_prod(o, line, db)
                                    if vo:
                                        model.Add(vo == 0)
            if line in restart_grades and restart_grades[line]:
                rst = restart_grades[line]
                if rst in grades and is_allowed(rst, line):
                    da = sd[-1] + 1
                    if da < num_days:
                        v = get_is_prod(rst, line, da)
                        if v:
                            model.Add(v == 1)
                            for o in grades:
                                if o != rst and is_allowed(o, line):
                                    vo = get_is_prod(o, line, da)
                                    if vo:
                                        model.Add(vo == 0)
    
    if progress_callback:
        progress_callback(0.2, "Inventory...")
    
    # Inventory
    inv_vars = {}
    for g in grades:
        for d in range(num_days + 1):
            inv_vars[(g, d)] = model.NewIntVar(0, 100000, f'inv_{g}_{d}')
    
    # FIX #9: Stockout only for planning days
    stockout_vars = {}
    for g in grades:
        for d in range(planning_days):
            stockout_vars[(g, d)] = model.NewIntVar(0, 100000, f'stk_{g}_{d}')
    
    for g in grades:
        model.Add(inv_vars[(g, 0)] == initial_inventory[g])
    
    # FIX #1: Simplified balance
    for g in grades:
        for d in range(num_days):
            prod_today = sum(get_prod(g, l, d) for l in allowed_lines[g])
            if d < planning_days:
                demand = demand_data[g].get(dates[d], 0)
                avail = model.NewIntVar(0, 100000, f'av_{g}_{d}')
                model.Add(avail == inv_vars[(g, d)] + prod_today)
                supplied = model.NewIntVar(0, 100000, f'sup_{g}_{d}')
                stockout = model.NewIntVar(0, 100000, f'so_{g}_{d}')
                model.AddMinEquality(supplied, [avail, demand])
                model.Add(stockout == demand - supplied)
                model.Add(inv_vars[(g, d + 1)] == avail - supplied)
                stockout_vars[(g, d)] = stockout
            else:
                model.Add(inv_vars[(g, d + 1)] == inv_vars[(g, d)] + prod_today)
    
    for g in grades:
        for d in range(1, num_days + 1):
            model.Add(inv_vars[(g, d)] <= max_inventory[g])
    
    if progress_callback:
        progress_callback(0.3, "Capacity...")
    
    # Full capacity
    for line in lines:
        for d in range(num_days):
            if line in shutdown_periods and d in shutdown_periods[line]:
                continue
            pvars = [get_prod(g, line, d) for g in grades if is_allowed(g, line)]
            if pvars:
                model.Add(sum(pvars) == capacities[line])
    
    if progress_callback:
        progress_callback(0.4, "Run constraints...")
    
    # Force start dates
    for gp_key, sd in force_start_date.items():
        if sd:
            g, p = gp_key
            try:
                idx = dates.index(sd)
                v = get_is_prod(g, p, idx)
                if v:
                    model.Add(v == 1)
            except:
                pass
    

    # FIX #3: Run start definitions (exclude material running)
    for grade in grades:
        for line in allowed_lines[grade]:
            gp_key = (grade, line)
            min_run = min_run_days.get(gp_key, 1)
            max_run = max_run_days.get(gp_key, 9999)
            
            # Define run starts
            for d in range(num_days):
                key = (grade, line, d)
                if key not in run_starts:
                    continue
                
                if line in shutdown_periods and d in shutdown_periods[line]:
                    model.Add(run_starts[key] == 0)
                    continue
                
                prod_today = get_is_prod(grade, line, d)
                if not prod_today:
                    continue
                
                # Check material running
                in_mat_block = False
                if line in material_map:
                    mat_g = material_map[line]['material']
                    end_d = material_map[line]['end_day']
                    if mat_g == grade and d <= end_d:
                        in_mat_block = True
                
                if in_mat_block:
                    model.Add(run_starts[key] == 0)  # FIX #3
                elif d == 0:
                    model.Add(run_starts[key] == prod_today)
                else:
                    prod_yest = get_is_prod(grade, line, d - 1)
                    if prod_yest:
                        model.Add(run_starts[key] <= prod_today)
                        model.Add(run_starts[key] <= 1 - prod_yest)
                        model.Add(run_starts[key] >= prod_today - prod_yest)
                    else:
                        model.Add(run_starts[key] == 0)
            
            # FIX #2: Force changeover after material running
            if line in material_map:
                mat_g = material_map[line]['material']
                end_d = material_map[line]['end_day']
                exp_d = material_map[line]['expected_days']
                
                if mat_g == grade and exp_d > 1:
                    co_day = end_d + 1
                    if co_day < num_days:
                        if not (line in shutdown_periods and co_day in shutdown_periods[line]):
                            v = get_is_prod(grade, line, co_day)
                            if v:
                                model.Add(v == 0)
            
            # FIX #7: Min run with horizon end handling
            for d in range(num_days):
                key = (grade, line, d)
                if key not in run_starts:
                    continue
                
                if line in shutdown_periods and d in shutdown_periods[line]:
                    continue
                
                in_mat_block = False
                if line in material_map:
                    mat_g = material_map[line]['material']
                    end_d = material_map[line]['end_day']
                    if mat_g == grade and d <= end_d:
                        in_mat_block = True
                
                if in_mat_block:
                    continue
                
                remaining = min(num_days - d, min_run)
                run_vars = []
                valid = True
                
                for off in range(remaining):
                    day_idx = d + off
                    if line in shutdown_periods and day_idx in shutdown_periods[line]:
                        valid = False
                        break
                    pv = get_is_prod(grade, line, day_idx)
                    if pv:
                        run_vars.append(pv)
                    else:
                        valid = False
                        break
                
                if valid and run_vars:
                    for pv in run_vars:
                        model.Add(pv == 1).OnlyEnforceIf(run_starts[key])
            
            # Max run days
            for d in range(num_days - max_run):
                consec = []
                valid = True
                for off in range(max_run + 1):
                    idx = d + off
                    if idx >= num_days:
                        valid = False
                        break
                    if line in shutdown_periods and idx in shutdown_periods[line]:
                        valid = False
                        break
                    pv = get_is_prod(grade, line, idx)
                    if pv:
                        consec.append(pv)
                    else:
                        valid = False
                        break
                if valid and len(consec) == max_run + 1:
                    model.Add(sum(consec) <= max_run)
    
    if progress_callback:
        progress_callback(0.5, "Transitions...")
    
    # Forbidden transitions
    for line in lines:
        if transition_rules.get(line):
            for d in range(num_days - 1):
                if line in shutdown_periods:
                    if d in shutdown_periods[line] or (d + 1) in shutdown_periods[line]:
                        continue
                
                for prev_g in grades:
                    if prev_g in transition_rules[line] and is_allowed(prev_g, line):
                        allowed_next = transition_rules[line][prev_g]
                        for curr_g in grades:
                            if curr_g != prev_g and curr_g not in allowed_next and is_allowed(curr_g, line):
                                pv = get_is_prod(prev_g, line, d)
                                cv = get_is_prod(curr_g, line, d + 1)
                                if pv and cv:
                                    model.Add(pv + cv <= 1)
    
    # FIX #8: Rerun constraint (exclude forced material)
    for grade in grades:
        for line in allowed_lines[grade]:
            gp_key = (grade, line)
            if not rerun_allowed.get(gp_key, True):
                start_vars = []
                for d in range(num_days):
                    if line in shutdown_periods and d in shutdown_periods[line]:
                        continue
                    
                    # FIX #8: Skip material running
                    if line in material_map:
                        mat_g = material_map[line]['material']
                        end_d = material_map[line]['end_day']
                        if mat_g == grade and d <= end_d:
                            continue
                    
                    key = (grade, line, d)
                    if key in run_starts:
                        start_vars.append(run_starts[key])
                
                if start_vars:
                    model.Add(sum(start_vars) <= 1)
    
    if progress_callback:
        progress_callback(0.6, "Soft constraints...")
    
    # Soft constraints
    inv_deficit = {}
    closing_deficit = {}
    
    for g in grades:
        for d in range(planning_days):  # FIX #9
            if min_inventory[g] > 0:
                deficit = model.NewIntVar(0, 100000, f'idef_{g}_{d}')
                model.Add(deficit >= min_inventory[g] - inv_vars[(g, d + 1)])
                model.Add(deficit >= 0)
                inv_deficit[(g, d)] = deficit
        
        if min_closing_inventory[g] > 0 and buffer_days > 0:
            cdef = model.NewIntVar(0, 100000, f'cdef_{g}')
            model.Add(cdef >= min_closing_inventory[g] - inv_vars[(g, planning_days)])
            model.Add(cdef >= 0)
            closing_deficit[g] = cdef
    
    if progress_callback:
        progress_callback(0.7, "Objective...")
    
    # FIX #6: Calculate average demand per grade
    avg_demand = {}
    for g in grades:
        total = sum(demand_data[g].get(dates[d], 0) for d in range(planning_days))
        avg_demand[g] = max(total / planning_days, 1.0) if planning_days > 0 else 1.0
    
    obj_terms = []
    epsilon = 1.0
    
    if penalty_method == "Ensure All Grades' Production":
        WEIGHT = 100
        
        # Stockout penalties
        for g in grades:
            avg = avg_demand[g]
            for d in range(planning_days):  # FIX #9
                if (g, d) in stockout_vars:
                    penalty = int((WEIGHT * stockout_penalty * 100) / avg)
                    obj_terms.append(penalty * stockout_vars[(g, d)])
        
        # Inventory deficits
        for (g, d), def_var in inv_deficit.items():
            avg = avg_demand[g]
            penalty = int((WEIGHT * stockout_penalty * 2 * 100) / avg)
            obj_terms.append(penalty * def_var)
        
        # Closing deficits
        for g, cdef_var in closing_deficit.items():
            avg = avg_demand[g]
            penalty = int((WEIGHT * stockout_penalty * 3 * 100) / avg)
            obj_terms.append(penalty * cdef_var)
        
        # FIX #4: Transitions (only forward pairs)
        for line in lines:
            for d in range(num_days - 1):
                if line in shutdown_periods:
                    if d in shutdown_periods[line] or (d + 1) in shutdown_periods[line]:
                        continue
                
                for i, g1 in enumerate(grades):
                    if line not in allowed_lines[g1]:
                        continue
                    for g2 in grades[i+1:]:  # FIX #4: Only forward pairs
                        if line not in allowed_lines[g2]:
                            continue
                        
                        # Skip forbidden
                        forbidden_12 = False
                        forbidden_21 = False
                        if transition_rules.get(line):
                            if g1 in transition_rules[line] and g2 not in transition_rules[line][g1]:
                                forbidden_12 = True
                            if g2 in transition_rules[line] and g1 not in transition_rules[line][g2]:
                                forbidden_21 = True
                        
                        if forbidden_12 and forbidden_21:
                            continue
                        
                        # Create bidirectional transition var
                        tv = model.NewBoolVar(f'tr_{line}_{d}_{g1}_{g2}')
                        v1_d = get_is_prod(g1, line, d)
                        v2_d1 = get_is_prod(g2, line, d + 1)
                        v2_d = get_is_prod(g2, line, d)
                        v1_d1 = get_is_prod(g1, line, d + 1)
                        
                        # tv = 1 if (g1→g2) OR (g2→g1)
                        if v1_d and v2_d1:
                            model.Add(tv >= v1_d + v2_d1 - 1)
                        if v2_d and v1_d1:
                            model.Add(tv >= v2_d + v1_d1 - 1)
                        
                        obj_terms.append(transition_penalty * tv)
        
        # FIX #10: Idle penalty removed (redundant with capacity)
    
    else:  # Standard mode
        # Stockout
        for g in grades:
            for d in range(planning_days):  # FIX #9
                if (g, d) in stockout_vars:
                    obj_terms.append(stockout_penalty * stockout_vars[(g, d)])
        
        # Inventory deficits
        for (g, d), def_var in inv_deficit.items():
            obj_terms.append(stockout_penalty * def_var)
        
        # Closing deficits
        for g, cdef_var in closing_deficit.items():
            obj_terms.append(stockout_penalty * cdef_var * 3)
        
        # FIX #4: Transitions (forward pairs only)
        for line in lines:
            for d in range(num_days - 1):
                if line in shutdown_periods:
                    if d in shutdown_periods[line] or (d + 1) in shutdown_periods[line]:
                        continue
                
                for i, g1 in enumerate(grades):
                    if line not in allowed_lines[g1]:
                        continue
                    for g2 in grades[i+1:]:
                        if line not in allowed_lines[g2]:
                            continue
                        
                        forbidden_12 = False
                        forbidden_21 = False
                        if transition_rules.get(line):
                            if g1 in transition_rules[line] and g2 not in transition_rules[line][g1]:
                                forbidden_12 = True
                            if g2 in transition_rules[line] and g1 not in transition_rules[line][g2]:
                                forbidden_21 = True
                        
                        if forbidden_12 and forbidden_21:
                            continue
                        
                        tv = model.NewBoolVar(f'tr_{line}_{d}_{g1}_{g2}')
                        v1_d = get_is_prod(g1, line, d)
                        v2_d1 = get_is_prod(g2, line, d + 1)
                        v2_d = get_is_prod(g2, line, d)
                        v1_d1 = get_is_prod(g1, line, d + 1)
                        
                        if v1_d and v2_d1:
                            model.Add(tv >= v1_d + v2_d1 - 1)
                        if v2_d and v1_d1:
                            model.Add(tv >= v2_d + v1_d1 - 1)
                        
                        obj_terms.append(transition_penalty * tv)
    
    if obj_terms:
        model.Minimize(sum(obj_terms))
    else:
        model.Minimize(0)
    
    if progress_callback:
        progress_callback(0.8, "Solving...")
    
    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60.0
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED
    solver.parameters.log_search_progress = True
    
    callback = SolutionCallback(
        production, inv_vars, stockout_vars, is_producing,
        grades, lines, dates, formatted_dates, num_days,
        inv_deficit, closing_deficit, run_starts, planning_days
    )
    
    status = solver.Solve(model, callback)
    
    if progress_callback:
        progress_callback(1.0, "Complete!")
    
    return status, callback, solver
