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
                 inventory_deficit_penalties=None, closing_inventory_deficit_penalties=None, run_starts=None):
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

        # Count transitions (actual grade changes, not run starts)
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
    lookahead_days: int = 3,
    progress_callback=None
) -> Tuple[int, SolutionCallback, cp_model.CpSolver]:
    """Build and solve the optimization model"""
    
    if progress_callback:
        progress_callback(0.0, "Building optimization model...")
    
    model = cp_model.CpModel()
    
    # Decision variables
    is_producing = {}
    production = {}
    run_starts = {}  # NEW: Track run starts
    
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
                
                # NEW: Create run start variable
                run_starts[key] = model.NewBoolVar(f'run_start_{grade}_{line}_{d}')
    
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
    material_running_map = {}
    
    for plant, (material, expected_days) in material_running_info.items():
        # ALWAYS force the material to run on day 0
        if is_allowed_combination(material, plant):
            day0_var = get_is_producing_var(material, plant, 0)
            if day0_var is not None:
                model.Add(day0_var == 1)
            
            for other_material in grades:
                if other_material != material and is_allowed_combination(other_material, plant):
                    other_var = get_is_producing_var(other_material, plant, 0)
                    if other_var is not None:
                        model.Add(other_var == 0)
        
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
    
    # Inventory variables
    inventory_vars = {}
    for grade in grades:
        for d in range(num_days + 1):
            inventory_vars[(grade, d)] = model.NewIntVar(0, 100000, f'inventory_{grade}_{d}')
    
    stockout_vars = {}
    for grade in grades:
        for d in range(num_days):
            stockout_vars[(grade, d)] = model.NewIntVar(0, 100000, f'stockout_{grade}_{d}')
    
    # Initial inventory
    for grade in grades:
        model.Add(inventory_vars[(grade, 0)] == initial_inventory[grade])
    
    # Inventory balance for each day
    for grade in grades:
        for d in range(num_days):
            produced_today = sum(
                get_production_var(grade, line, d) 
                for line in allowed_lines[grade]
            )
            demand_today = demand_data[grade].get(dates[d], 0)
            
            available = model.NewIntVar(0, 100000, f'available_{grade}_{d}')
            model.Add(available == inventory_vars[(grade, d)] + produced_today)
            
            supplied = model.NewIntVar(0, 100000, f'supplied_{grade}_{d}')
            stockout = model.NewIntVar(0, 100000, f'stockout_{grade}_{d}')
            
            model.Add(supplied <= available)
            model.Add(supplied <= demand_today)
            
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
        for line in allowed_lines[grade]:
            grade_plant_key = (grade, line)
            min_run = min_run_days.get(grade_plant_key, 1)
            max_run = max_run_days.get(grade_plant_key, 9999)
            
            # Define run start variables
            for d in range(num_days):
                key = (grade, line, d)
                if key not in run_starts:
                    continue
                
                prod_today = get_is_producing_var(grade, line, d)
                if prod_today is None:
                    continue
                
                # Check if in material running block
                is_in_material_block = False
                if line in material_running_map:
                    material_grade = material_running_map[line]['material']
                    expected_days = material_running_map[line]['expected_days']
                    if material_grade == grade and d < expected_days:
                        is_in_material_block = True
                
                if d == 0:
                    # Day 0: run start = producing
                    model.Add(run_starts[key] == prod_today)
                else:
                    prod_yesterday = get_is_producing_var(grade, line, d - 1)
                    if prod_yesterday is not None:
                        # run_start = producing today AND not producing yesterday
                        model.Add(run_starts[key] <= prod_today)
                        model.Add(run_starts[key] <= 1 - prod_yesterday)
                        model.Add(run_starts[key] >= prod_today - prod_yesterday)
                    else:
                        model.Add(run_starts[key] == 0)
            
            # Force changeover after material running
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
            
            # Minimum run days
            for d in range(num_days):
                is_in_material_block = False
                if line in material_running_map:
                    material_grade = material_running_map[line]['material']
                    expected_days = material_running_map[line]['expected_days']
                    if material_grade == grade and d < expected_days:
                        is_in_material_block = True
                
                if is_in_material_block:
                    continue
                
                key = (grade, line, d)
                if key not in run_starts:
                    continue
                
                if d + min_run > num_days:
                    continue
                
                run_days_vars = []
                valid_for_min_run = True
                
                for offset in range(min_run):
                    day_idx = d + offset
                    if day_idx >= num_days:
                        valid_for_min_run = False
                        break
                    
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
                
                for prod_var in run_days_vars[:min_run]:
                    model.Add(prod_var == 1).OnlyEnforceIf(run_starts[key])
            
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
        for line in allowed_lines[grade]:
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
    lookahead_deficit_penalties = {}
    production_target_shortfalls = {}
    
    # ========== ENHANCED "MINIMIZE STOCKOUTS" LOGIC ==========
    if penalty_method == "Minimize Stockouts":
        if progress_callback:
            progress_callback(0.65, "Calculating stockout minimization parameters...")
        
        # ========== SIMPLIFIED STRATEGY ==========
        # 1. Identify critical grades based on demand vs capacity
        grade_criticality = {}
        total_daily_capacity = sum(capacities[line] for line in lines) * num_days
        
        for grade in grades:
            # Calculate total demand
            total_demand = sum(demand_data[grade].get(dates[d], 0) for d in range(num_days))
            
            # Calculate available production capacity for this grade
            grade_capacity = 0
            for line in allowed_lines[grade]:
                if line in capacities:
                    grade_capacity += capacities[line] * num_days
            
            # Criticality score: demand / capacity ratio
            if grade_capacity > 0:
                utilization = total_demand / grade_capacity
            else:
                utilization = 999  # Very high if no capacity
            
            # Demand variability
            daily_demands = [demand_data[grade].get(dates[d], 0) for d in range(num_days)]
            avg_demand = total_demand / num_days if num_days > 0 else 0
            
            if avg_demand > 0:
                # Calculate max daily demand relative to average
                max_daily = max(daily_demands)
                peak_factor = max_daily / avg_demand
            else:
                peak_factor = 1.0
            
            # Critical grades: high utilization OR high peak demand
            is_critical = (utilization > 0.8) or (peak_factor > 2.0)
            
            grade_criticality[grade] = {
                'total_demand': total_demand,
                'grade_capacity': grade_capacity,
                'utilization': utilization,
                'peak_factor': peak_factor,
                'is_critical': is_critical,
                'priority_multiplier': 5.0 if is_critical else 1.0  # 5x higher penalty for critical grades
            }
        
        # ========== ADJUSTED PENALTIES ==========
        # Increase stockout penalties significantly for all grades
        base_stockout_multiplier = 10  # 10x higher than standard mode
        
        # Critical grades get even higher penalties
        critical_penalty_multiplier = {}
        for grade in grades:
            if grade_criticality[grade]['is_critical']:
                # Critical grades: 20x standard penalty
                critical_penalty_multiplier[grade] = 20
            else:
                # Non-critical grades: 10x standard penalty
                critical_penalty_multiplier[grade] = 10
        
        # ========== FOCUSED LOOKAHEAD ==========
        # Only look ahead for critical grades
        lookahead_deficit_penalties = {}
        
        for grade in grades:
            if not grade_criticality[grade]['is_critical']:
                continue
                
            # For critical grades, ensure we have inventory for next 3 days
            for d in range(num_days - 3):
                future_demand = 0
                for offset in range(1, 4):  # Next 3 days
                    if d + offset < num_days:
                        future_demand += demand_data[grade].get(dates[d + offset], 0)
                
                if future_demand > 0:
                    # Simple: need at least future demand as inventory
                    required_inventory = future_demand
                    inventory_shortfall = model.NewIntVar(0, 100000, f'critical_lookahead_{grade}_{d}')
                    current_inventory = inventory_vars[(grade, d)]
                    
                    model.Add(inventory_shortfall >= required_inventory - current_inventory)
                    model.Add(inventory_shortfall >= 0)
                    
                    # High penalty for not having enough inventory for future demand
                    lookahead_deficit_penalties[(grade, d)] = inventory_shortfall
        
        # ========== DYNAMIC SAFETY STOCK ==========
        # Simple: 2 days of average demand for critical grades, 1 day for others
        dynamic_safety_stocks = {}
        for grade in grades:
            avg_daily = grade_criticality[grade]['total_demand'] / num_days if num_days > 0 else 0
            if grade_criticality[grade]['is_critical']:
                # Critical: 3 days of safety stock
                safety_days = 3
            else:
                # Non-critical: 1.5 days of safety stock
                safety_days = 1.5
            
            safety_stock = int(avg_daily * safety_days)
            dynamic_safety_stocks[grade] = max(min_inventory[grade], safety_stock)
        
        # ========== INVENTORY DEFICIT PENALTIES ==========
        inventory_deficit_penalties = {}
        for grade in grades:
            target_inventory = dynamic_safety_stocks[grade]
            if target_inventory > 0:
                for d in range(num_days):
                    inventory_tomorrow = inventory_vars[(grade, d + 1)]
                    
                    deficit_var = model.NewIntVar(0, 100000, f'safety_deficit_{grade}_{d}')
                    model.Add(deficit_var >= target_inventory - inventory_tomorrow)
                    model.Add(deficit_var >= 0)
                    
                    inventory_deficit_penalties[(grade, d)] = deficit_var
        
        # ========== REDUCED TRANSITION PENALTY ==========
        # Allow more flexibility to switch to needed grades
        effective_transition_penalty = max(1, transition_penalty // 20)  # 5% of normal
        
        # ========== OBJECTIVE FUNCTION ==========
        objective_terms = []
        
        # 1. High stockout penalties (PRIORITY 1)
        for grade in grades:
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    multiplier = critical_penalty_multiplier[grade]
                    penalty = stockout_penalty * multiplier
                    objective_terms.append(penalty * stockout_vars[(grade, d)])
        
        # 2. Safety stock inventory deficits (PRIORITY 2)
        for (grade, d), deficit_var in inventory_deficit_penalties.items():
            if grade_criticality[grade]['is_critical']:
                # Higher penalty for critical grades
                penalty = stockout_penalty * 8
            else:
                penalty = stockout_penalty * 3
            objective_terms.append(penalty * deficit_var)
        
        # 3. Critical lookahead penalties (PRIORITY 1.5)
        for (grade, d), shortfall_var in lookahead_deficit_penalties.items():
            # Very high penalty for not preparing for future demand of critical grades
            penalty = stockout_penalty * 15
            objective_terms.append(penalty * shortfall_var)
        
        # 4. Minimal transition penalty
        for line in lines:
            for grade in grades:
                for d in range(num_days):
                    key = (grade, line, d)
                    if key in run_starts:
                        objective_terms.append(effective_transition_penalty * run_starts[key])
        
        # 5. Minimal idle penalty (just to break ties)
        idle_penalty = 10
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
        
        if objective_terms:
            model.Minimize(sum(objective_terms))
        else:
            model.Minimize(0)
    
    else:
        # ========== STANDARD MINIMUM INVENTORY (SOFT) ==========
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
    objective_terms = []
    epsilon = 1.0
    
    if penalty_method == "Minimize Stockouts":
        # ========== ENHANCED OBJECTIVE FOR MINIMIZE STOCKOUTS ==========
        
        # 1. Risk-weighted stockout penalties (HIGH PRIORITY)
        for grade in grades:
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    penalty = risk_weighted_penalties[grade]
                    objective_terms.append(penalty * stockout_vars[(grade, d)])
        
        # 2. Dynamic inventory deficits (MEDIUM PRIORITY)
        for (grade, d), deficit_var in inventory_deficit_penalties.items():
            weight = grade_metrics[grade]['priority_factor']
            penalty = stockout_penalty * weight * 0.5
            objective_terms.append(penalty * deficit_var)
        
        # 3. Lookahead deficits (HIGH PRIORITY for near-term)
        for (grade, d), (shortfall_var, urgency_factor) in lookahead_deficit_penalties.items():
            penalty = risk_weighted_penalties[grade] * urgency_factor
            objective_terms.append(penalty * shortfall_var)
        
        # 4. Production target shortfalls (LOW-MEDIUM PRIORITY)
        for grade, shortfall_var in production_target_shortfalls.items():
            penalty = stockout_penalty * 0.3
            objective_terms.append(penalty * shortfall_var)
        
        # 5. Reduced transition penalties
        effective_transition_penalty = max(1, transition_penalty // 5)
        
        # Use run starts for transition counting
        for line in lines:
            for grade in grades:
                for d in range(num_days):
                    key = (grade, line, d)
                    if key in run_starts:
                        objective_terms.append(effective_transition_penalty * run_starts[key])
        
        # 6. Minimal idle penalty (only to break ties)
        idle_penalty = 50
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
    
    elif penalty_method == "Ensure All Grades' Production":
        PERCENTAGE_PENALTY_WEIGHT = 100
        
        # Stockout penalties
        for grade in grades:
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    demand_today = demand_data[grade].get(dates[d], 0)
                    
                    if demand_today > 0:
                        penalty_per_unit = (PERCENTAGE_PENALTY_WEIGHT * stockout_penalty) / (demand_today + epsilon)
                        scaled_penalty = int(penalty_per_unit * 100)
                        objective_terms.append(scaled_penalty * stockout_vars[(grade, d)])
        
        # Inventory deficit penalties
        MIN_INV_VIOLATION_MULTIPLIER = 2
        for (grade, d), deficit_var in inventory_deficit_penalties.items():
            daily_demand = demand_data[grade].get(dates[d], 0)
            
            if daily_demand > 0:
                penalty_coeff = (PERCENTAGE_PENALTY_WEIGHT * stockout_penalty * MIN_INV_VIOLATION_MULTIPLIER) / (daily_demand + epsilon)
                scaled_penalty = int(penalty_coeff * 100)
                objective_terms.append(scaled_penalty * deficit_var)
            else:
                objective_terms.append(stockout_penalty * MIN_INV_VIOLATION_MULTIPLIER * deficit_var)
        
        # Closing inventory deficit penalties
        for grade, closing_deficit_var in closing_inventory_deficit_penalties.items():
            total_demand = sum(demand_data[grade].get(dates[d], 0) for d in range(num_days))
            avg_daily_demand = total_demand / num_days if num_days > 0 else 1
            
            if avg_daily_demand > 0:
                penalty_coeff = (PERCENTAGE_PENALTY_WEIGHT * stockout_penalty * 3) / (avg_daily_demand + epsilon)
                scaled_penalty = int(penalty_coeff * 100)
                objective_terms.append(scaled_penalty * closing_deficit_var)
            else:
                objective_terms.append(stockout_penalty * closing_deficit_var * 3)
        
        # Transition penalties
        effective_transition_penalty = transition_penalty
        
        # Standard pairwise transitions
        for line in lines:
            for d in range(num_days - 1):
                for grade1 in grades:
                    if line not in allowed_lines[grade1]:
                        continue
                    for grade2 in grades:
                        if line not in allowed_lines[grade2] or grade1 == grade2:
                            continue
                        
                        if (transition_rules.get(line) and 
                            grade1 in transition_rules[line] and 
                            grade2 not in transition_rules[line][grade1]):
                            continue
                        
                        trans_var = model.NewBoolVar(f'trans_{line}_{d}_{grade1}_to_{grade2}')
                        model.Add(trans_var <= is_producing[(grade1, line, d)])
                        model.Add(trans_var <= is_producing[(grade2, line, d + 1)])
                        model.Add(trans_var >= is_producing[(grade1, line, d)] + 
                                  is_producing[(grade2, line, d + 1)] - 1)
                        
                        objective_terms.append(effective_transition_penalty * trans_var)
        
        # Idle line penalty
        idle_penalty = 500
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
    
    elif penalty_method == "Minimize Transitions":
        # Stockout penalties
        for grade in grades:
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    objective_terms.append(stockout_penalty * stockout_vars[(grade, d)])
        
        # Use run starts for transition counting
        for line in lines:
            for grade in grades:
                for d in range(num_days):
                    key = (grade, line, d)
                    if key in run_starts:
                        objective_terms.append(transition_penalty * run_starts[key])
        
        # Inventory deficit penalties
        for (grade, d), deficit_var in inventory_deficit_penalties.items():
            objective_terms.append(stockout_penalty * deficit_var)
        
        # Closing inventory deficit penalties
        for grade, closing_deficit_var in closing_inventory_deficit_penalties.items():
            objective_terms.append(stockout_penalty * closing_deficit_var * 3)
    
    else:  # Standard mode
        # Stockout penalties
        for grade in grades:
            for d in range(num_days):
                if (grade, d) in stockout_vars:
                    objective_terms.append(stockout_penalty * stockout_vars[(grade, d)])
        
        # Inventory deficit penalties
        for (grade, d), deficit_var in inventory_deficit_penalties.items():
            objective_terms.append(stockout_penalty * deficit_var)
        
        # Closing inventory deficit penalties
        for grade, closing_deficit_var in closing_inventory_deficit_penalties.items():
            objective_terms.append(stockout_penalty * closing_deficit_var * 3)
        
        # Transition penalties
        effective_transition_penalty = transition_penalty
        
        # Standard pairwise transitions
        for line in lines:
            for d in range(num_days - 1):
                for grade1 in grades:
                    if line not in allowed_lines[grade1]:
                        continue
                    for grade2 in grades:
                        if line not in allowed_lines[grade2] or grade1 == grade2:
                            continue
                        
                        if (transition_rules.get(line) and 
                            grade1 in transition_rules[line] and 
                            grade2 not in transition_rules[line][grade1]):
                            continue
                        
                        trans_var = model.NewBoolVar(f'trans_{line}_{d}_{grade1}_to_{grade2}')
                        model.Add(trans_var <= is_producing[(grade1, line, d)])
                        model.Add(trans_var <= is_producing[(grade2, line, d + 1)])
                        model.Add(trans_var >= is_producing[(grade1, line, d)] + 
                                  is_producing[(grade2, line, d + 1)] - 1)
                        
                        objective_terms.append(effective_transition_penalty * trans_var)
        
        # Idle line penalty
        idle_penalty = 500
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
        inventory_deficit_penalties, closing_inventory_deficit_penalties, run_starts
    )
    
    status = solver.Solve(model, solution_callback)
    
    if progress_callback:
        progress_callback(1.0, "Optimization complete!")
    
    return status, solution_callback, solver
