"""
CP-SAT Solver for production optimization with adaptive stockout weighting
"""

from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED


class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Callback to capture all solutions during search"""
    
    def __init__(self, production, inventory, stockout, is_producing, grades, lines, dates, formatted_dates, num_days, 
                 inventory_deficit_penalties=None, closing_inventory_deficit_penalties=None):
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


def compute_adaptive_stockout_weights(
    grades: List[str],
    demand_data: Dict[str, Dict[datetime, int]],
    dates: List[datetime],
    allowed_lines: Dict[str, List[str]],
    initial_inventory: Dict[str, int],
    min_run_days: Dict[Tuple[str, str], int],
    max_run_days: Dict[Tuple[str, str], int],
    force_start_date: Dict[Tuple[str, str], datetime],
    buffer_days: int = 3,
    min_weight: float = 0.5,
    max_weight: float = 5.0
) -> Dict[str, float]:
    """
    Compute intelligent stockout penalty weights based on multiple factors.
    
    Factors considered:
    1. Demand volume and variability
    2. Production flexibility (number of eligible lines)
    3. Inventory risk (current stock relative to demand)
    4. Run constraints (min/max run days)
    5. Temporal importance (urgency based on force start dates)
    """
    
    num_days = len(dates)
    weights = {}
    
    if not grades:
        return weights
    
    # Phase 1: Calculate base metrics for each grade
    metrics = {}
    for grade in grades:
        # Extract demand series
        daily_demand = [demand_data[grade].get(date, 0) for date in dates]
        total_demand = sum(daily_demand)
        avg_daily_demand = total_demand / num_days if num_days > 0 else 0
        
        # Calculate demand variability (coefficient of variation)
        if avg_daily_demand > 0:
            demand_std = (sum((d - avg_daily_demand) ** 2 for d in daily_demand) / num_days) ** 0.5
            cv_demand = demand_std / avg_daily_demand
        else:
            cv_demand = 0
        
        # Calculate days of coverage from opening inventory
        opening_inv = initial_inventory.get(grade, 0)
        days_coverage = opening_inv / avg_daily_demand if avg_daily_demand > 0 else float('inf')
        
        # Production flexibility
        num_eligible_lines = len(allowed_lines.get(grade, []))
        
        # Run constraint severity - get min/max run for first eligible line
        run_constraint_factor = 1.0
        if allowed_lines.get(grade):
            first_line = allowed_lines[grade][0]
            min_run = min_run_days.get((grade, first_line), 1)
            max_run = max_run_days.get((grade, first_line), float('inf'))
            run_constraint_factor = min_run / max_run if max_run > 0 else 1.0
        
        # Temporal urgency (force start date proximity)
        urgency_factor = 0.0
        if allowed_lines.get(grade):
            first_line = allowed_lines[grade][0]
            force_start = force_start_date.get((grade, first_line))
            if force_start:
                try:
                    start_idx = dates.index(force_start)
                    days_until_force = max(0, start_idx)
                    urgency_factor = max(0, 1 - (days_until_force / num_days))
                except (ValueError, AttributeError):
                    urgency_factor = 0.0
        
        # Determine if grade has low demand (below 1/3 of average)
        avg_all_demand = sum(metrics.get(g, {}).get('avg_daily_demand', 0) for g in grades[:grades.index(grade)]) / max(len(grades[:grades.index(grade)]), 1)
        is_low_demand = False
        if grades.index(grade) > 0 and avg_all_demand > 0:
            is_low_demand = avg_daily_demand < (avg_all_demand * 0.33)
        
        metrics[grade] = {
            'total_demand': total_demand,
            'avg_daily_demand': avg_daily_demand,
            'cv_demand': cv_demand,
            'days_coverage': days_coverage,
            'num_lines': num_eligible_lines,
            'run_constraint': run_constraint_factor,
            'urgency': urgency_factor,
            'is_low_demand': is_low_demand
        }
    
    # Calculate average demand across all grades for comparison
    all_avg_demand = sum(m['avg_daily_demand'] for m in metrics.values()) / len(metrics)
    
    # Phase 2: Calculate normalized scores for each factor
    def normalize_values(values_dict, inverse=False):
        """Normalize values to [0, 1] range"""
        vals = [v for v in values_dict.values() if isinstance(v, (int, float))]
        if not vals:
            return {k: 0.5 for k in values_dict.keys()}
        
        min_val = min(vals)
        max_val = max(vals)
        
        if max_val - min_val < 1e-6:
            return {k: 0.5 for k in values_dict.keys()}
        
        normalized = {}
        for k, v in values_dict.items():
            if isinstance(v, (int, float)):
                if inverse:
                    # Higher original value gives lower normalized score
                    norm = (max_val - v) / (max_val - min_val)
                else:
                    norm = (v - min_val) / (max_val - min_val)
                normalized[k] = max(0, min(1, norm))  # Clamp to [0, 1]
            else:
                normalized[k] = 0.5
        return normalized
    
    # Extract metrics for normalization
    total_demands = {g: m['total_demand'] for g, m in metrics.items()}
    avg_demands = {g: m['avg_daily_demand'] for g, m in metrics.items()}
    cvs = {g: m['cv_demand'] for g, m in metrics.items()}
    coverages = {g: m['days_coverage'] for g, m in metrics.items()}
    line_counts = {g: m['num_lines'] for g, m in metrics.items()}
    run_constraints = {g: m['run_constraint'] for g, m in metrics.items()}
    urgencies = {g: m['urgency'] for g, m in metrics.items()}
    
    # Normalize (inverse for some, direct for others)
    norm_total_demand = normalize_values(total_demands, inverse=True)  # Inverse: lower demand → higher score
    norm_avg_demand = normalize_values(avg_demands, inverse=True)  # Inverse: lower daily demand → higher score
    norm_cv = normalize_values(cvs, inverse=False)  # Direct: higher variability → higher score
    norm_coverage = normalize_values(coverages, inverse=True)  # Inverse: lower coverage → higher score
    norm_lines = normalize_values(line_counts, inverse=True)  # Inverse: fewer lines → higher score
    norm_run = normalize_values(run_constraints, inverse=False)  # Direct: tighter constraints → higher score
    norm_urgency = normalize_values(urgencies, inverse=False)  # Direct: more urgent → higher score
    
    # Phase 3: Calculate composite score with adaptive weighting
    for grade in grades:
        m = metrics[grade]
        
        # Base importance factors (can be tuned)
        demand_factor = 0.35  # How much to weight demand characteristics
        flexibility_factor = 0.25  # How much to weight production flexibility
        risk_factor = 0.20  # How much to weight inventory risk
        constraint_factor = 0.15  # How much to weight run constraints
        urgency_factor = 0.05  # How much to weight temporal urgency
        
        # Calculate weighted composite score
        composite_score = (
            demand_factor * (norm_total_demand[grade] * 0.6 + norm_avg_demand[grade] * 0.3 + norm_cv[grade] * 0.1) +
            flexibility_factor * norm_lines[grade] +
            risk_factor * norm_coverage[grade] +
            constraint_factor * norm_run[grade] +
            urgency_factor * norm_urgency[grade]
        )
        
        # Apply special boosting for very low-demand grades
        if all_avg_demand > 0:
            relative_size = m['avg_daily_demand'] / all_avg_demand
            if relative_size < 0.3:  # Less than 30% of average
                # Boost score for very small grades
                boost_factor = 1.5 - (relative_size * 2)  # 1.5x to 0.9x boost
                composite_score = min(1.0, composite_score * boost_factor)
        
        # Convert to weight in desired range with smooth transformation
        # Use power transformation for smoother distribution
        final_weight = min_weight + (max_weight - min_weight) * (composite_score ** 0.7)
        
        weights[grade] = round(final_weight, 2)
    
    # Phase 4: Ensure no grade gets extreme weight unless justified
    weight_values = list(weights.values())
    if len(weight_values) >= 3:
        weight_values.sort()
        n = len(weight_values)
        
        q1 = weight_values[n // 4]
        q3 = weight_values[3 * n // 4]
        iqr = q3 - q1
        
        if iqr > 0:  # Only moderate if there's variation
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            for grade, weight in weights.items():
                if weight < lower_bound:
                    # Very low weight - check if justified
                    m = metrics[grade]
                    if m['avg_daily_demand'] > all_avg_demand * 0.5 and m['num_lines'] > 1:
                        # High demand grade with very low weight - adjust upward
                        weights[grade] = max(weight, q1 * 0.8)
                elif weight > upper_bound:
                    # Very high weight - check if justified
                    m = metrics[grade]
                    if m['days_coverage'] > 7 and m['num_lines'] > 1:
                        # Good coverage and multiple lines - reduce weight
                        weights[grade] = min(weight, q3 * 1.2)
    
    # Ensure all grades have weights
    for grade in grades:
        if grade not in weights:
            weights[grade] = 1.0
    
    return weights


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
    progress_callback=None,
    grade_priority_weights: Optional[Dict[str, float]] = None,
    adaptive_weighting: bool = True,
    min_weight: float = 0.5,
    max_weight: float = 5.0
) -> Tuple[int, SolutionCallback, cp_model.CpSolver]:
    """Build and solve the optimization model with adaptive stockout weighting"""
    
    if progress_callback:
        progress_callback(0.0, "Building optimization model...")
    
    # Calculate adaptive weights if not provided
    if grade_priority_weights is None and adaptive_weighting:
        if progress_callback:
            progress_callback(0.05, "Computing adaptive stockout weights...")
        
        grade_priority_weights = compute_adaptive_stockout_weights(
            grades=grades,
            demand_data=demand_data,
            dates=dates,
            allowed_lines=allowed_lines,
            initial_inventory=initial_inventory,
            min_run_days=min_run_days,
            max_run_days=max_run_days,
            force_start_date=force_start_date,
            buffer_days=buffer_days,
            min_weight=min_weight,
            max_weight=max_weight
        )
    
    # Use default weights if still None
    if grade_priority_weights is None:
        grade_priority_weights = {grade: 1.0 for grade in grades}
    
    # Log the computed weights for debugging
    print("Adaptive stockout weights:")
    for grade, weight in sorted(grade_priority_weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  {grade}: {weight}")
    
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
    material_running_map = {}
    for plant, (material, expected_days) in material_running_info.items():
        material_running_map[plant] = {
            'material': material,
            'expected_days': min(expected_days, num_days)
        }
        
        # Force the material to run for exactly expected_days
        for d in range(min(expected_days, num_days)):
            if is_allowed_combination(material, plant):
                model.Add(get_is_producing_var(material, plant, d) == 1)
                # Force all other grades to 0
                for other_material in grades:
                    if other_material != material and is_allowed_combination(other_material, plant):
                        model.Add(get_is_producing_var(other_material, plant, d) == 0)
    
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
    # This fixes the bug where stockouts occur despite available inventory
    
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
            
            # ========== CRITICAL FIX: FORCE MAXIMUM POSSIBLE SUPPLY ==========
            # This prevents artificial stockouts when inventory is available
            
            # Supply cannot exceed available inventory or demand
            model.Add(supplied <= available)
            model.Add(supplied <= demand_today)
            
            # Create indicator variable: do we have enough inventory to meet demand?
            enough_inventory = model.NewBoolVar(f'enough_{grade}_{d}')
            
            # Set the indicator variable
            model.Add(available >= demand_today).OnlyEnforceIf(enough_inventory)
            model.Add(available < demand_today).OnlyEnforceIf(enough_inventory.Not())
            
            # Force supply to be maximum possible:
            # If enough inventory, supply = demand
            # If not enough, supply = available inventory
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
    
    # ========== CORRECTED MIN/MAX RUN DAYS LOGIC ==========
    for grade in grades:
        for line in allowed_lines[grade]:
            grade_plant_key = (grade, line)
            min_run = min_run_days.get(grade_plant_key, 1)
            max_run = max_run_days.get(grade_plant_key, 9999)
            
            # Check if this line has material running
            has_material_running = line in material_running_map
            material_running_grade = material_running_map[line]['material'] if has_material_running else None
            material_running_days = material_running_map[line]['expected_days'] if has_material_running else 0
            
            # ========== FORCE CHANGEOVER AFTER MATERIAL RUNNING ==========
            if has_material_running and material_running_grade == grade:
                # This grade is forced for material_running_days
                # The day after material running ends, we MUST NOT produce the same grade
                if material_running_days < num_days:
                    prod_day_after = get_is_producing_var(grade, line, material_running_days)
                    if prod_day_after is not None:
                        model.Add(prod_day_after == 0)  # Force changeover
            
            # ========== MINIMUM RUN DAYS CONSTRAINT ==========
            for d in range(num_days):
                # Check if this day is within material running block
                is_in_material_block = (has_material_running and 
                                       material_running_grade == grade and 
                                       d < material_running_days)
                
                if is_in_material_block:
                    continue  # Skip min-run constraint for material running days
                
                prod_today = get_is_producing_var(grade, line, d)
                if prod_today is None:
                    continue
                
                # Check if this is start of a new run
                if d == 0:
                    starts_new_run = prod_today
                else:
                    prod_yesterday = get_is_producing_var(grade, line, d - 1)
                    if prod_yesterday is not None:
                        # Check if yesterday was material running
                        yesterday_in_material_block = (has_material_running and 
                                                      material_running_grade == grade and 
                                                      (d - 1) < material_running_days)
                        
                        if yesterday_in_material_block:
                            # Yesterday was forced material running
                            # Today cannot be same grade (we already enforced changeover)
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
                
                # Collect variables for the next min_run days
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
            
            # ========== MAXIMUM RUN DAYS CONSTRAINT ==========
            for d in range(num_days - max_run):
                # Check sequence of max_run + 1 consecutive days
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
                    has_material_running = line in material_running_map
                    if has_material_running:
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
                            yesterday_in_material = (has_material_running and 
                                                    material_running_grade == grade and 
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
    
    # 1. Stockout penalties with ADAPTIVE WEIGHTS (SOFT)
    for grade in grades:
        weight = grade_priority_weights.get(grade, 1.0)
        # Scale by 100 to avoid floating point issues, then convert to int
        scaled_penalty = int(stockout_penalty * weight * 100)
        
        for d in range(num_days):
            if (grade, d) in stockout_vars:
                objective_terms.append(scaled_penalty * stockout_vars[(grade, d)])
    
    # 2. Inventory deficit penalties (SOFT)
    for (grade, d), deficit_var in inventory_deficit_penalties.items():
        # Use adaptive weight for inventory deficits too
        weight = grade_priority_weights.get(grade, 1.0)
        scaled_penalty = int(stockout_penalty * weight * 100)
        objective_terms.append(scaled_penalty * deficit_var)
    
    # 3. Closing inventory deficit penalties (SOFT)
    for grade, closing_deficit_var in closing_inventory_deficit_penalties.items():
        # Use adaptive weight for closing inventory deficits
        weight = grade_priority_weights.get(grade, 1.0)
        scaled_penalty = int(stockout_penalty * weight * 100 * 3)  # 3x multiplier for closing inventory
        objective_terms.append(scaled_penalty * closing_deficit_var)
    
    # 4. Transition penalties (SOFT - for ALLOWED transitions only)
    for line in lines:
        for d in range(num_days - 1):
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
        inventory_deficit_penalties, closing_inventory_deficit_penalties
    )
    
    status = solver.Solve(model, solution_callback)
    
    if progress_callback:
        progress_callback(1.0, "Optimization complete!")
    
    return status, solution_callback, solver
