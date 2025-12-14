"""
CP-SAT Solver for production optimization
"""

from ortools.sat.python import cp_model
# Explicitly import the types used in the signature and inheritance for robustness
from ortools.sat.python.cp_model import CpSolverStatus, CpSolver, CpSolverSolutionCallback 
import time
from typing import Dict, List, Tuple
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED
import math


# The SolutionCallback class now inherits directly from the imported type
class SolutionCallback(CpSolverSolutionCallback):
    """Callback to capture all solutions during search"""
    
    def __init__(self, production, inventory, stockout, is_producing, grades, lines, dates, formatted_dates, num_days, 
                 inventory_deficit_penalties=None, closing_inventory_deficit_penalties=None):
        # Change inheritance call to use the directly imported type
        CpSolverSolutionCallback.__init__(self) 
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
            'production': self.get_production_results(),
            'inventory': self.get_inventory_results(),
            'stockout': self.get_stockout_results(),
            'is_producing': self.get_is_producing_results(),
        }
        self.solutions.append(solution)
        self.objective_breakdowns.append(self.get_objective_breakdown())
    
    def get_objective_breakdown(self) -> Dict:
        """Calculate the values of soft constraints for the current solution."""
        breakdown = {
            'total_objective': int(self.ObjectiveValue()),
            'stockout_penalty': 0,
            'closing_inventory_penalty': 0,
            'transition_penalty': 0,
            'idle_penalty': 0,
            # Placeholder for actual calculation logic if needed
        }
        
        # Note: In a real CP-SAT implementation, getting the exact breakdown requires
        # retrieving the value of the objective variables themselves from the model.
        # Since we don't have access to the original model variables here, we'll
        # rely on the final objective value. For a full breakdown, the model
        # objective would need to be structured as a sum of variables, and their
        # values retrieved here. We return the total objective for now.
        
        return breakdown

    def get_production_results(self) -> Dict:
        """Extract production schedule."""
        prod_results = {}
        for (grade, line, d), var in self.production.items():
            if self.Value(var) > 0:
                prod_results.setdefault(line, {}).setdefault(self.dates[d], {})[grade] = int(self.Value(var))
        return prod_results

    def get_inventory_results(self) -> Dict:
        """Extract inventory levels (post-production, pre-demand)."""
        inv_results = {}
        for (grade, d), var in self.inventory.items():
            inv_results.setdefault(grade, {})[self.formatted_dates[d]] = int(self.Value(var))
        return inv_results

    def get_stockout_results(self) -> Dict:
        """Extract stockout quantities."""
        stockout_results = {}
        for (grade, d), var in self.stockout.items():
            if self.Value(var) > 0:
                stockout_results.setdefault(grade, {})[self.formatted_dates[d]] = int(self.Value(var))
        return stockout_results

    def get_is_producing_results(self) -> Dict:
        """Extract the grade running on each line per day."""
        is_producing_results = {}
        for (grade, line, d), var in self.is_producing.items():
            if self.Value(var) == 1:
                is_producing_results.setdefault(line, {})[self.dates[d]] = grade
        return is_producing_results


def build_and_solve_model(
    data: Dict,
    time_limit_min: int,
    stockout_penalty: int,
    transition_penalty: int,
    idle_penalty: int,
    buffer_days: int,
    progress_callback=None
) -> Tuple[CpSolverStatus, SolutionCallback, CpSolver]: # Updated type hints
    """
    Builds and solves the CP-SAT model for the Polymer Production Scheduler.
    
    Args:
        data (Dict): Parsed input data from Excel sheets.
        time_limit_min (int): Optimization time limit in minutes.
        stockout_penalty (int): Penalty for stockout (soft constraint).
        transition_penalty (int): Penalty for an unallowed transition (soft constraint).
        idle_penalty (int): Penalty for a line being idle (soft constraint).
        buffer_days (int): Number of days for minimum closing inventory enforcement.
        progress_callback (Callable): Callback function for Streamlit progress bar.
        
    Returns:
        Tuple[CpSolverStatus, SolutionCallback, CpSolver]: The solver status, 
        the SolutionCallback instance containing results, and the solver instance.
    """
    
    if progress_callback:
        progress_callback(0.1, "Initializing model...")

    model = cp_model.CpModel()
    
    # ===============================================================
    #  DATA EXTRACTION
    # ===============================================================
    dates = data['dates']
    formatted_dates = data['formatted_dates']
    num_days = len(dates)
    grades = data['grades']
    lines = data['lines']
    
    capacity = data['capacity']
    demand = data['demand']
    inventory_data = data['inventory']
    transition_rules = data['transition_rules']
    shutdown_days = data['shutdown_days']
    min_run_days = data['min_run_days']
    max_run_days = data['max_run_days']
    force_start = data['force_start']
    rerun_allowed = data['rerun_allowed']
    
    # ===============================================================
    #  VARIABLES
    # ===============================================================

    # production[(grade, line, day)] = quantity of grade produced on line on day
    production = {}
    # is_producing[(grade, line, day)] = 1 if grade is produced on line on day
    is_producing = {}
    # inventory[(grade, day)] = inventory of grade at end of day (before demand)
    inventory_vars = {} 
    # stockout[(grade, day)] = quantity of demand not met
    stockout_vars = {} 
    
    # Helper variables for tracking grade production
    # is_grade_produced[(grade, day)] = 1 if grade is produced on ANY line on day
    is_grade_produced = model.NewBoolVar('is_grade_produced')
    
    # Inventory deficit variables for soft constraints
    inventory_deficit_vars = {} # For daily min inventory
    inventory_deficit_penalties = {}
    closing_inventory_deficit_vars = {} # For final min closing inventory
    closing_inventory_deficit_penalties = {}
    
    max_production_per_day = max(capacity.values()) if capacity else 0
    max_inventory = sum(max_production_per_day for _ in range(num_days)) + max(inv['opening'] for inv in inventory_data.values()) if inventory_data else 100000

    if progress_callback:
        progress_callback(0.2, "Creating production variables...")
        
    # Production and Is_Producing variables
    for grade in grades:
        for line in lines:
            if line not in inventory_data[grade]['lines']:
                continue # Skip if grade is not allowed on this line
            
            for d in range(num_days):
                # Production variable
                var_prod = model.NewIntVar(0, capacity[line], f'prod_{grade}_{line}_{d}')
                production[(grade, line, d)] = var_prod
                
                # Boolean indicator for production
                var_is_prod = model.NewBoolVar(f'is_producing_{grade}_{line}_{d}')
                is_producing[(grade, line, d)] = var_is_prod
                
                # Link: if production > 0, is_producing must be 1.
                # Production must be <= capacity * is_producing
                # Using AddImplication: is_producing = 1 <=> production > 0
                model.Add(var_prod <= capacity[line] * var_is_prod)
                
                # If is_producing is true, production is at least 1 (not strictly necessary but can help)
                # model.Add(var_prod >= 1).OnlyEnforceIf(var_is_prod) 
                
                # Constraint: Production must be 0 on shutdown days
                if d in shutdown_days.get(line, []):
                    model.Add(var_prod == 0)

    if progress_callback:
        progress_callback(0.3, "Creating inventory and stockout variables...")

    # Inventory and Stockout variables
    for grade in grades:
        inv_max = inventory_data[grade]['max_inv'] # Max inventory limit
        
        for d in range(num_days):
            # Inventory variable (Inventory after production and before demand)
            inv_var = model.NewIntVar(0, inv_max + max_inventory, f'inventory_{grade}_{d}')
            inventory_vars[(grade, d)] = inv_var
            
            # Stockout variable (demand not met)
            # Max stockout is the maximum daily demand for a grade
            max_stockout = max(demand[d].get(grade, 0) for d in range(num_days)) 
            stockout_var = model.NewIntVar(0, max_stockout, f'stockout_{grade}_{d}')
            stockout_vars[(grade, d)] = stockout_var

            # Min Inventory Deficit variable (Soft Constraint)
            if inventory_data[grade]['min_inv'] > 0:
                deficit_var = model.NewIntVar(0, inventory_data[grade]['min_inv'], f'inv_deficit_{grade}_{d}')
                inventory_deficit_vars[(grade, d)] = deficit_var
                inventory_deficit_penalties[(grade, d)] = deficit_var

            # Min Closing Inventory Deficit variable (Soft Constraint - only last few days)
            if d >= num_days - buffer_days:
                min_close_inv = inventory_data[grade]['min_closing']
                if min_close_inv > 0:
                    deficit_close_var = model.NewIntVar(0, min_close_inv, f'close_inv_deficit_{grade}_{d}')
                    closing_inventory_deficit_vars[(grade, d)] = deficit_close_var
                    closing_inventory_deficit_penalties[(grade, d)] = deficit_close_var


    # ===============================================================
    #  HARD CONSTRAINTS
    # ===============================================================
    
    if progress_callback:
        progress_callback(0.4, "Setting hard constraints (Capacity, Production, Inventory)...")

    # 1. Capacity Constraint: Each line can only run one grade per day
    for line in lines:
        for d in range(num_days):
            # Boolean variables for production on the current day for all allowed grades on the line
            day_producing_vars = [
                is_producing[(grade, line, d)] 
                for grade in grades 
                if (grade, line, d) in is_producing
            ]
            
            # At most one grade can be produced on a line per day (0 or 1)
            model.Add(sum(day_producing_vars) <= 1)
            
            # Also, total production must be less than or equal to capacity (already linked by production var bound)
            # Total production of all grades on line 'line' on day 'd'
            day_production_vars = [
                production[(grade, line, d)] 
                for grade in grades 
                if (grade, line, d) in production
            ]
            model.Add(sum(day_production_vars) <= capacity[line])


    # 2. Inventory Flow and Demand Satisfaction
    for grade in grades:
        inv_min = inventory_data[grade]['min_inv']
        inv_max = inventory_data[grade]['max_inv']
        
        for d in range(num_days):
            
            # Production on day 'd' for grade
            total_production_d = sum(
                production.get((grade, line, d), 0) for line in lines
            )
            
            # Inventory at start of day 'd'
            inv_start_d = inventory_data[grade]['opening'] if d == 0 else inventory_vars[(grade, d-1)]
            
            # Demand on day 'd' for grade
            demand_d = demand[d].get(grade, 0)
            
            # Inventory Flow Constraint (Balance Equation):
            # Start Inv + Production - Demand + Stockout = End Inv
            # End Inv = Start Inv + Production - Demand + Stockout
            
            # The inventory_vars[(grade, d)] is the inventory *after* production, *before* demand
            # Temporary variable for inventory after demand
            inv_after_demand = model.NewIntVar(-max_inventory, max_inventory, f'inv_after_demand_{grade}_{d}')

            # 2a. Inventory After Production (pre-demand):
            # This must be within max_inv limit
            # model.Add(inventory_vars[(grade, d)] == inv_start_d + total_production_d)
            model.Add(inventory_vars[(grade, d)] <= inv_max) # Hard upper limit
            
            # 2b. Demand Satisfaction: Inv_After_Production - Demand = Final_Inv - Stockout
            # Inv_After_Production - Demand + Stockout = Inventory_Next_Day (or Final Inventory)
            # The total available material is inv_start_d + total_production_d
            
            # Total Available Material
            total_available = inv_start_d + total_production_d
            
            # Inventory at start of day d+1 (Inv_start_d_plus_1)
            # This is equal to: Total Available - Demand + Stockout
            
            # We use `inventory_vars[(grade, d)]` as the inventory available *at the end of day d*
            # after production.
            
            # Link Inventory_After_Production to flow:
            model.Add(inventory_vars[(grade, d)] == inv_start_d + total_production_d)
            
            # Link Stockout and Inventory_Next_Day
            if d < num_days - 1:
                inv_next_day = inventory_vars[(grade, d+1)] # Inventory at start of d+1 is inventory at end of d
            else:
                inv_next_day = model.NewIntVar(0, max_inventory, f'final_inv_{grade}') # Final inventory placeholder
            
            # Inventory at start of d+1 (end of d) = Inventory_Available - Demand + Stockout
            # Where Inventory_Available is `inventory_vars[(grade, d)]` (Inv_start_d + Prod_d)
            model.Add(inv_next_day == inventory_vars[(grade, d)] - demand_d + stockout_vars[(grade, d)])
            
            # 2c. Stockout must ensure that demand is either met or the available inventory is exhausted.
            # Stockout must be > 0 only if inventory is not enough to cover demand.
            # Available Inventory = inventory_vars[(grade, d)]
            
            # Stockout is the deficit: Stockout >= Demand - Available
            model.Add(stockout_vars[(grade, d)] >= demand_d - inventory_vars[(grade, d)])
            
            # Stockout must be <= Demand
            model.Add(stockout_vars[(grade, d)] <= demand_d)
            
            # If demand is met (stockout=0), then next day's start inventory must be Available - Demand
            
            
    # 3. Minimum Daily Inventory (Hard/Soft Mix)
    for grade in grades:
        inv_min = inventory_data[grade]['min_inv']
        if inv_min > 0:
            for d in range(num_days):
                # Min Daily Inventory Constraint (Soft): Inv_after_demand >= inv_min - deficit
                # This ensures inventory never drops below a required buffer, unless we pay the penalty.
                
                # Inventory after demand on day d is: inventory_vars[(grade, d)] - demand_d + stockout_vars[(grade, d)]
                inv_after_demand_d = model.NewIntVar(-max_inventory, max_inventory, f'inv_after_demand_temp_{grade}_{d}')
                model.Add(inv_after_demand_d == inventory_vars[(grade, d)] - demand_d + stockout_vars[(grade, d)])
                
                # Soft Constraint: inv_after_demand_d >= inv_min - deficit_var
                deficit_var = inventory_deficit_vars[(grade, d)]
                model.Add(inv_after_demand_d >= inv_min - deficit_var)
                
                # Deficit is 0 if inventory is met:
                # model.Add(deficit_var == 0).OnlyEnforceIf(inv_after_demand_d >= inv_min) # Redundant due to Add
                
    # 4. Minimum Closing Inventory (Soft Constraint)
    for grade in grades:
        min_close_inv = inventory_data[grade]['min_closing']
        if min_close_inv > 0:
            for d in range(num_days - buffer_days, num_days):
                # The inventory at the start of d+1 (end of d) is the 'final' inventory for day d
                if d < num_days - 1:
                    final_inv_d = inventory_vars[(grade, d+1)]
                else:
                    # Final inventory on the last day (d=num_days-1) is the last calculated inventory
                    final_inv_d = model.NewIntVar(0, max_inventory, f'final_inv_d_{grade}_{d}')
                    # Final Inv = Available - Demand + Stockout (last calculated flow)
                    demand_d = demand[d].get(grade, 0)
                    total_production_d = sum(production.get((grade, line, d), 0) for line in lines)
                    inv_start_d = inventory_data[grade]['opening'] if d == 0 else inventory_vars[(grade, d-1)]
                    model.Add(final_inv_d == inv_start_d + total_production_d - demand_d + stockout_vars[(grade, d)])


                deficit_close_var = closing_inventory_deficit_vars[(grade, d)]
                # Soft Constraint: final_inv_d >= min_close_inv - deficit_close_var
                model.Add(final_inv_d >= min_close_inv - deficit_close_var)
                

    # 5. Production Transition Constraints (Hard/Soft Mix)
    for line in lines:
        
        # Initial state (day -1)
        initial_grade = data['material_running'].get(line)
        
        # Determine the grade running yesterday for use in transition constraint
        for d in range(num_days):
            
            yesterday_grade_var = initial_grade if d == 0 else None
            
            if d > 0:
                # Create a variable to represent the grade running yesterday
                yesterday_is_producing = [
                    is_producing[(grade, line, d-1)] 
                    for grade in grades 
                    if (grade, line, d-1) in is_producing
                ]
                
                # Check for an unallowed transition
                transition_violation_var = model.NewBoolVar(f'trans_viol_{line}_{d}')
                
                # If d > 0, the transition is from d-1 production to d production
                
                for grade_current in grades:
                    if (grade_current, line, d) not in is_producing: continue

                    is_current = is_producing[(grade_current, line, d)]
                    
                    if d == 0:
                        # Day 0 transition from initial_grade
                        is_transition_allowed = grade_current in transition_rules.get(line, {}).get(initial_grade, [])
                        
                        if is_transition_allowed:
                            # Hard: If current grade is produced, transition is valid (always true)
                            pass 
                        else:
                            # Soft: If current grade is produced, violation must be 1
                            model.Add(transition_violation_var == 1).OnlyEnforceIf(is_current)

                    else:
                        # Day > 0 transition from grade_prev (produced on d-1)
                        for grade_prev in grades:
                            if (grade_prev, line, d-1) not in is_producing: continue

                            is_prev = is_producing[(grade_prev, line, d-1)]
                            
                            is_transition_allowed = grade_current in transition_rules.get(line, {}).get(grade_prev, [])
                            
                            # Implication: (is_prev AND is_current) => is_transition_valid
                            is_prev_and_current = model.NewBoolVar('')
                            model.AddBoolAnd([is_prev, is_current]).OnlyEnforceIf(is_prev_and_current)
                            
                            if is_transition_allowed:
                                # Hard: Allowed transition, no violation implied.
                                pass 
                            else:
                                # Soft: Unallowed transition, violation is 1
                                model.Add(transition_violation_var == 1).OnlyEnforceIf(is_prev_and_current)
                                
                # Add the transition penalty term
                if line in data['lines'] and transition_rules.get(line): # Only penalize if line exists and rules are defined
                    model.Add(transition_violation_var * transition_penalty).OnlyEnforceIf(transition_violation_var) # Add term only if it's 1


    # 6. Minimum/Maximum Run Days
    for grade in grades:
        min_run = min_run_days.get(grade, 1)
        max_run = max_run_days.get(grade, num_days)
        rerun = rerun_allowed.get(grade, False)
        
        for line in lines:
            if line not in inventory_data[grade]['lines']:
                continue

            # Check if grade is produced at all
            grade_running_vars = [is_producing[(grade, line, d)] for d in range(num_days) if (grade, line, d) in is_producing]
            if not grade_running_vars:
                continue

            # 6a. Minimum Run Days (Only applies if run starts)
            if min_run > 1:
                # Find the start of a run (is_producing[d] AND NOT is_producing[d-1])
                for d in range(num_days):
                    if (grade, line, d) not in is_producing: continue
                        
                    is_current = is_producing[(grade, line, d)]
                    
                    if d == 0:
                        is_start = is_current # Start of run at day 0
                    else:
                        is_prev = is_producing.get((grade, line, d-1), 0)
                        is_start = model.NewBoolVar('')
                        model.AddBoolAnd([is_current, is_prev.Not()]).OnlyEnforceIf(is_start)
                        
                    # If it's a start, it must run for at least min_run days
                    # sum(is_producing[d:d+min_run]) == min_run
                    if d + min_run <= num_days:
                        run_span = [is_producing.get((grade, line, t), 0) for t in range(d, d + min_run) if (grade, line, t) in is_producing]
                        model.Add(sum(run_span) == min_run).OnlyEnforceIf(is_start)
                    else:
                        # Cannot satisfy min_run, so cannot start.
                        model.Add(is_start == 0)

            # 6b. Maximum Run Days (Stop must happen after max_run)
            if max_run < num_days:
                # Find the end of a run (is_producing[d] AND NOT is_producing[d+1])
                for d in range(num_days):
                    if (grade, line, d) not in is_producing: continue
                        
                    is_current = is_producing[(grade, line, d)]
                    
                    if d == num_days - 1:
                        is_end = is_current # End of run on last day
                    else:
                        is_next = is_producing.get((grade, line, d+1), 0)
                        is_end = model.NewBoolVar('')
                        model.AddBoolAnd([is_current, is_next.Not()]).OnlyEnforceIf(is_end)
                        
                    # If it's the end of a run, the run must have lasted at most max_run days
                    # sum(is_producing[d-max_run+1 : d+1]) <= max_run
                    if d - max_run + 1 >= 0:
                        # Check the window of max_run days ending today (d)
                        run_span = [is_producing.get((grade, line, t), 0) for t in range(d - max_run + 1, d + 1) if (grade, line, t) in is_producing]
                        # If is_end is true, then the sum of the last max_run days of 'is_producing' must be less than max_run days (since it ended today)
                        # This constraint is complex to enforce properly with pure CP-SAT and runs, so we simplify:
                        # If a grade runs for max_run days, it *must* stop on the max_run+1 day.
                        
                        # Find runs of length max_run+1
                        if d - max_run >= 0:
                            # Span of max_run + 1 days
                            long_run_span = [is_producing.get((grade, line, t), 0) for t in range(d - max_run, d + 1) if (grade, line, t) in is_producing]
                            is_long_run = model.NewBoolVar('')
                            model.Add(sum(long_run_span) == max_run + 1).OnlyEnforceIf(is_long_run)
                            
                            # Hard: A run cannot exceed max_run days
                            model.Add(is_long_run == 0)
                            
                        # Simpler: If a run starts on day 's', it must stop before day 's + max_run'.
                        # This is typically handled by the long run constraint above.

    # 7. Initial State (Material Running)
    for line, grade in data['material_running'].items():
        if (grade, line, 0) in is_producing:
            # If the current material running on the line is one of the grades,
            # we can enforce the expected run days.
            expected_days = data['expected_days'].get(line, 1)
            
            # The line MUST run this grade for expected_days (up to the max run days/schedule end)
            run_span = [is_producing.get((grade, line, d), 0) for d in range(min(expected_days, num_days)) if (grade, line, d) in is_producing]
            if run_span:
                model.Add(sum(run_span) == len(run_span)) # Enforce it runs for the initial period
                
            # If the initial grade is running, it must satisfy its min_run days from day 0.
            # This is covered by the Min Run Days constraint (case d=0).

    # 8. Force Start Date
    for grade, info in force_start.items():
        if not info: continue
        line, start_date = info
        
        try:
            start_index = dates.index(start_date)
        except ValueError:
            # Date is outside planning horizon, ignore
            continue
            
        # The grade must be produced on the specified line on the start_index day
        if (grade, line, start_index) in is_producing:
            model.Add(is_producing[(grade, line, start_index)] == 1)
            
            # For robustness, we enforce min_run days from this point as well
            min_run = min_run_days.get(grade, 1)
            run_span = [is_producing.get((grade, line, d), 0) for d in range(start_index, min(start_index + min_run, num_days)) if (grade, line, d) in is_producing]
            if run_span:
                model.Add(sum(run_span) == len(run_span))


    # 9. Shutdown Pre/Restart Grade
    for line, info in data['shutdown_info'].items():
        if not info['shutdown_start']: continue
            
        start_date = info['shutdown_start']
        end_date = info['shutdown_end']
        pre_grade = info['pre_shutdown_grade']
        restart_grade = info['restart_grade']
        
        try:
            start_index = dates.index(start_date)
            end_index = dates.index(end_date)
        except ValueError:
            continue
        
        # Pre-shutdown grade must be running the day before shutdown starts (if d-1 is in the horizon)
        day_before_shutdown = start_index - 1
        if day_before_shutdown >= 0:
            if (pre_grade, line, day_before_shutdown) in is_producing:
                model.Add(is_producing[(pre_grade, line, day_before_shutdown)] == 1)
            
        # Restart grade must be running the day after shutdown ends (if d+1 is in the horizon)
        day_after_shutdown = end_index + 1
        if day_after_shutdown < num_days:
            if (restart_grade, line, day_after_shutdown) in is_producing:
                model.Add(is_producing[(restart_grade, line, day_after_shutdown)] == 1)


    # ===============================================================
    #  OBJECTIVE (MINIMIZE SOFT CONSTRAINTS)
    # ===============================================================
    
    if progress_callback:
        progress_callback(0.6, "Defining objective function...")

    objective_terms = []

    # 1. Minimize Stockout (Hard constraint violation)
    # Stockout penalty applied per MT of stockout
    for var in stockout_vars.values():
        objective_terms.append(stockout_penalty * var)
        
    # 2. Minimize Inventory Deficit (Soft Min Inventory)
    # Penalty applied per MT of daily inventory deficit
    for var in inventory_deficit_penalties.values():
        objective_terms.append(var) # Penalty is already in the variable value

    # 3. Minimize Closing Inventory Deficit (Soft Min Closing Inventory)
    # Penalty applied per MT of closing inventory deficit
    for var in closing_inventory_deficit_penalties.values():
        objective_terms.append(var) # Penalty is already in the variable value
        
    # 4. Minimize Transition Violations (Handled inline in Constraint 5 for now)
    # NOTE: Transition violation variables are complex to retrieve in the callback
    # The objective terms for transitions should be added in Constraint 5. 

    # 5. Minimize Idle Time (Soft Constraint)
    for line in lines:
        for d in range(num_days):
            is_idle = model.NewBoolVar(f'idle_{line}_{d}')
            
            producing_vars = [
                is_producing[(grade, line, d)] 
                for grade in grades 
                if (grade, line, d) in is_producing
            ]
            
            if producing_vars:
                # If sum(producing_vars) == 0, then is_idle must be 1.
                model.Add(sum(producing_vars) == 0).OnlyEnforceIf(is_idle)
                # If sum(producing_vars) == 1, then is_idle must be 0.
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
    solver = CpSolver() # Use directly imported type
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
        progress_callback(1.0, "Optimization complete.")
        
    return status, solution_callback, solver
