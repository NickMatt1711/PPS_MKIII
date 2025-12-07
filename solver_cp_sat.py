# solver_cp_sat.py
"""
CP-SAT Solver for production optimization — full solver file.

Modes:
- Standard
- Ensure All Grades Production
- Minimize Stockouts
- Minimize Transitions

Usage:
  status, solution_callback, solver = solve_production_problem(...)

This file is self-contained but expects:
- ortools.sat.python.cp_model installed
- input data (grades, lines, capacities, demand_data, etc.) prepared outside
"""

from ortools.sat.python import cp_model
import time
from typing import Dict, List, Tuple, Optional

# Constants for solver parallelism / repeatability (can be overridden)
SOLVER_NUM_WORKERS = 8
SOLVER_RANDOM_SEED = 42


class SolutionCallback(cp_model.CpSolverSolutionCallback):
    """Callback to capture solutions during search."""
    def __init__(self, production_vars, inventory_vars, stockout_vars, is_producing_vars,
                 grades, lines, dates, formatted_dates, num_days):
        super().__init__()
        self.production = production_vars
        self.inventory = inventory_vars
        self.stockout = stockout_vars
        self.is_producing = is_producing_vars
        self.grades = grades
        self.lines = lines
        self.dates = dates
        self.formatted_dates = formatted_dates
        self.num_days = num_days
        self.solutions = []
        self.solution_times = []
        self.start_time = time.time()

    def on_solution_callback(self):
        t = time.time() - self.start_time
        self.solution_times.append(t)
        obj = self.ObjectiveValue()
        sol = {
            "time": t,
            "objective": obj,
            "production": {},
            "inventory": {},
            "stockout": {},
            "is_producing": {}
        }

        # production: sum per day per grade (only positive values)
        for grade in self.grades:
            sol["production"][grade] = {}
            for line in self.lines:
                for d in range(self.num_days):
                    key = (grade, line, d)
                    if key in self.production:
                        val = int(self.Value(self.production[key]))
                        if val > 0:
                            date_key = self.formatted_dates[d]
                            sol["production"][grade].setdefault(date_key, 0)
                            sol["production"][grade][date_key] += val

        # inventory: opening inventory for each day (grade, d)
        for grade in self.grades:
            sol["inventory"][grade] = {}
            for d in range(self.num_days + 1):
                key = (grade, d)
                if key in self.inventory:
                    val = int(self.Value(self.inventory[key]))
                    tag = self.formatted_dates[d] if d < self.num_days else "final"
                    sol["inventory"][grade][tag] = val

        # stockouts
        for grade in self.grades:
            sol["stockout"][grade] = {}
            for d in range(self.num_days):
                key = (grade, d)
                if key in self.stockout:
                    val = int(self.Value(self.stockout[key]))
                    if val > 0:
                        sol["stockout"][grade][self.formatted_dates[d]] = val

        # is_producing mapping
        for line in self.lines:
            sol["is_producing"][line] = {}
            for d in range(self.num_days):
                sol["is_producing"][line][self.formatted_dates[d]] = None
                for grade in self.grades:
                    key = (grade, line, d)
                    if key in self.is_producing and self.Value(self.is_producing[key]) == 1:
                        sol["is_producing"][line][self.formatted_dates[d]] = grade
                        break

        # transitions counting
        total_transitions = 0
        transitions_per_line = {l: 0 for l in self.lines}
        for line in self.lines:
            last = None
            for d in range(self.num_days):
                current = sol["is_producing"][line].get(self.formatted_dates[d])
                if current is not None and last is not None and current != last:
                    transitions_per_line[line] += 1
                    total_transitions += 1
                if current is not None:
                    last = current
        sol["transitions"] = {"per_line": transitions_per_line, "total": total_transitions}

        self.solutions.append(sol)

    def num_solutions(self):
        return len(self.solutions)


def solve_production_problem(
    grades: List[str],
    lines: List[str],
    dates: List,
    formatted_dates: List[str],
    num_days: int,
    capacities: Dict[str, int],
    initial_inventory: Dict[str, int],
    demand_data: Dict[str, Dict],
    allowed_lines: Dict[str, List[str]],
    min_run_days: Dict[str, int],
    max_run_days: Dict[str, Optional[int]],
    min_closing_inventory: Dict[str, int],
    shutdown_periods: Dict[str, List[int]],
    transition_rules: Dict[str, Dict[str, List[str]]],
    buffer_days: int,
    stockout_penalty: int,
    transition_penalty: int,
    run_start_penalty: int,
    time_limit_min: int,
    penalty_method: str = "Standard",
    progress_callback=None
) -> Tuple[int, SolutionCallback, cp_model.CpSolver]:
    """
    Build and solve CP-SAT model.

    penalty_method: one of "Standard", "Ensure All Grades Production", "Minimize Stockouts", "Minimize Transitions"
    """

    if progress_callback:
        progress_callback(0.0, "Building optimization model")

    model = cp_model.CpModel()

    # Decision vars
    is_producing = {}      # Bool (grade, line, day)
    production = {}        # Int production quantity (grade, line, day) = either 0 or capacities[line]
    inventory = {}         # Int opening inventory for each grade and day (grade, day) where day in 0..num_days
    stockout = {}          # Int stockout quantity (grade, day)
    run_start = {}         # Bool run start (grade, line, day)
    transition_var_list = []  # optional list for transitions if needed

    # Create variables
    for grade in grades:
        for d in range(num_days + 1):
            inv_key = (grade, d)
            # Inventory bounds: 0 .. large number
            inventory[inv_key] = model.NewIntVar(0, 10 ** 6, f"inv_{grade}_{d}")

    for grade in grades:
        for line in allowed_lines.get(grade, []):
            for d in range(num_days):
                p_key = (grade, line, d)
                is_key = (grade, line, d)
                is_producing[is_key] = model.NewBoolVar(f"is_{grade}_{line}_{d}")

                # production quantity variable: either 0 or capacity
                production[p_key] = model.NewIntVar(0, capacities[line], f"prod_{grade}_{line}_{d}")
                # link production to is_producing
                model.Add(production[p_key] == capacities[line]).OnlyEnforceIf(is_producing[is_key])
                model.Add(production[p_key] == 0).OnlyEnforceIf(is_producing[is_key].Not())

                # run start var: true if is_producing today and not producing same grade-line yesterday
                run_start[p_key] = model.NewBoolVar(f"runstart_{grade}_{line}_{d}")

    # Stockout vars
    for grade in grades:
        for d in range(num_days):
            stockout[(grade, d)] = model.NewIntVar(0, 10 ** 6, f"stockout_{grade}_{d}")

    # ---------------- HARD CONSTRAINTS ----------------

    # 1) Shutdown days: no production allowed
    for line in lines:
        for d in shutdown_periods.get(line, []):
            for grade in grades:
                if (grade, line, d) in is_producing:
                    model.Add(is_producing[(grade, line, d)] == 0)
                    model.Add(production[(grade, line, d)] == 0)

    # 2) At most one grade per line per day
    for line in lines:
        for d in range(num_days):
            vars_on_line = []
            for grade in grades:
                if (grade, line, d) in is_producing:
                    vars_on_line.append(is_producing[(grade, line, d)])
            if vars_on_line:
                model.Add(sum(vars_on_line) <= 1)

    # 3) Inventory balance:
    # inventory_{g,0} = initial_inventory[g]
    # inventory_{g,d+1} = inventory_{g,d} + delivered_production_of_g_on_day_d - demand_on_day_d + stockout_adjustment
    # We'll treat stockout as unmet demand variable: inventory can't go negative because stockout absorbs shortage.
    for grade in grades:
        # initial
        model.Add(inventory[(grade, 0)] == int(initial_inventory.get(grade, 0)))
        for d in range(num_days):
            # total production of grade on day d across allowed lines
            prod_sum = []
            for line in allowed_lines.get(grade, []):
                key = (grade, line, d)
                if key in production:
                    prod_sum.append(production[key])
            if not prod_sum:
                total_prod_expr = 0
            else:
                total_prod_expr = sum(prod_sum)

            demand = int(demand_data.get(grade, {}).get(dates[d], 0))
            # inventory next = inventory current + production - demand + stockout (stockout is >= shortfall)
            # But stockout represents unmet demand; to keep integer relations:
            # inventory_{d+1} + stockout_{d} = inventory_{d} + production_{d} - demand  with stockout >= 0
            # Rearranged: inventory_{d+1} == inventory_{d} + production_{d} - demand + stockout_{d}
            model.Add(inventory[(grade, d + 1)] == inventory[(grade, d)] + total_prod_expr - demand + stockout[(grade, d)])
            # stockout constrained >= 0 by var domain

    # 4) Minimum / maximum run length constraints (min_run_days as hard constraint)
    # If a run starts, it must last at least min_run_days for that grade-line (if defined)
    for grade in grades:
        for line in allowed_lines.get(grade, []):
            min_run = int(min_run_days.get(grade, 1))
            # We enforce min run days by forbidding starting production unless enough days remain or by a sequence trick:
            for d in range(num_days):
                # If a run starts at d, then must produce next min_run-1 days on same grade-line (if within horizon)
                start_key = (grade, line, d)
                # run start: is_producing[d] == 1 and (prev day is not producing same grade-line)
                if start_key in is_producing:
                    prev_is = None
                    if d - 1 >= 0 and (grade, line, d - 1) in is_producing:
                        prev_is = is_producing[(grade, line, d - 1)]
                    # Define run_start: is_producing[d] AND (prev_is is False or prev not exists)
                    if prev_is is not None:
                        model.AddBoolAnd([is_producing[start_key], prev_is.Not()]).OnlyEnforceIf(run_start[start_key])
                        # If prev_is true then run_start must be false:
                        model.Add(run_start[start_key] == 0).OnlyEnforceIf(prev_is)
                    else:
                        # no prev day -> run_start == is_producing[d]
                        model.Add(run_start[start_key] == is_producing[start_key])

                    # enforce min run length
                    if min_run > 1:
                        # For each possible start day ensure subsequent days are producing or the model forbids the start
                        # We'll add implication: If run_start[start_key] == 1 then is_producing for next min_run-1 days must be 1
                        next_days = []
                        for k in range(1, min_run):
                            if d + k < num_days:
                                if (grade, line, d + k) in is_producing:
                                    next_days.append(is_producing[(grade, line, d + k)])
                                else:
                                    # if cannot produce on a future day (e.g., shutdown) then disallow run_start
                                    # i.e., run_start <= 0
                                    model.Add(run_start[start_key] == 0)
                                    next_days = []
                                    break
                            else:
                                # not enough days remaining -> disallow start near horizon end
                                model.Add(run_start[start_key] == 0)
                                next_days = []
                                break
                        if next_days:
                            # enforce each next_day == 1 when run_start == 1
                            for nd in next_days:
                                model.Add(nd == 1).OnlyEnforceIf(run_start[start_key])

    # 5) Transition feasibility enforced by allowed transitions (transition_rules) as HARD constraints
    # We will not create explicit forbidden trans soft penalties here. We'll only create variables for allowed transitions to be penalized later.
    # Also create transition boolean variables for each possible change grade1->grade2 on a line between day d and d+1
    transition_vars = {}
    for line in lines:
        for d in range(num_days - 1):
            for g1 in grades:
                for g2 in grades:
                    if g1 == g2:
                        continue
                    # Check allowed lists: both grades allowed on this line
                    if line not in allowed_lines.get(g1, []) or line not in allowed_lines.get(g2, []):
                        continue
                    # Check transition_rules if present for the line (forbidden combos)
                    if transition_rules and transition_rules.get(line):
                        # If g1 in transition_rules[line] and g2 not in allowed list for g1 then skip
                        if g1 in transition_rules[line] and g2 not in transition_rules[line][g1]:
                            continue
                    # create transition var
                    tvar = model.NewBoolVar(f"trans_{line}_{d}_{g1}_to_{g2}")
                    transition_vars[(line, d, g1, g2)] = tvar
                    # Link tvar <= is_producing(g1,line,d) and <= is_producing(g2,line,d+1)
                    model.Add(tvar <= is_producing.get((g1, line, d), model.NewConstant(0)))
                    model.Add(tvar <= is_producing.get((g2, line, d + 1), model.NewConstant(0)))
                    # tvar >= is_producing(g1,d) + is_producing(g2,d+1) - 1
                    a = is_producing.get((g1, line, d), None)
                    b = is_producing.get((g2, line, d + 1), None)
                    if a is not None and b is not None:
                        model.Add(tvar >= a + b - 1)

    # ---------------- SOFT CONSTRAINTS & OBJECTIVE ----------------
    objective_terms = []

    # Base stockout penalty always applied (present in all modes)
    # But we'll scale/adjust per mode
    # For now, accumulate stockout penalty multiplication later depending on mode

    # Continuity bonus variable: reward staying on same grade on same line next day (negative term)
    continuity_bonus = 0  # default, can be set per mode

    # We'll create helper sums for useful counts
    total_stockout_expr = []
    for grade in grades:
        for d in range(num_days):
            total_stockout_expr.append(stockout[(grade, d)])

    # Count transitions total as linear sum of transition_vars
    total_transition_bools = list(transition_vars.values())

    # Count run_starts total
    run_start_bools = [run_start[k] for k in run_start]

    # Decide penalties based on mode (clean, conflict-free)
    # Defaults (user-provided values are inputs; we use them as baseline)
    base_stockout_penalty = int(stockout_penalty)
    base_transition_penalty = int(transition_penalty)
    base_run_start_penalty = int(run_start_penalty)

    # Mode-specific effective penalties and behaviors
    if penalty_method == "Standard":
        # Balanced default: moderate stockout, moderate transitions, require continuity
        eff_stockout_pen = base_stockout_penalty
        eff_transition_pen = base_transition_penalty
        eff_run_start_pen = base_run_start_penalty
        continuity_bonus = 20  # small reward to keep same grade/day-to-day

        # Apply stockout penalties
        for grade in grades:
            for d in range(num_days):
                objective_terms.append(eff_stockout_pen * stockout[(grade, d)])

        # Apply transition penalties (sum over transition bools)
        for tvar in total_transition_bools:
            objective_terms.append(eff_transition_pen * tvar)

        # Slight penalty on run starts
        for r in run_start_bools:
            objective_terms.append(eff_run_start_pen * r)

        # Optional small reward for continuity: implement via negative terms
        for line in lines:
            for d in range(num_days - 1):
                for grade in grades:
                    if (grade, line, d) in is_producing and (grade, line, d + 1) in is_producing:
                        continuity_bool = model.NewBoolVar(f"cont_{grade}_{line}_{d}")
                        model.AddBoolAnd([is_producing[(grade, line, d)], is_producing[(grade, line, d + 1)]]).OnlyEnforceIf(continuity_bool)
                        model.Add(continuity_bool == 0).OnlyEnforceIf(is_producing[(grade, line, d)].Not())
                        model.Add(continuity_bool == 0).OnlyEnforceIf(is_producing[(grade, line, d + 1)].Not())
                        objective_terms.append(-continuity_bonus * continuity_bool)

    elif penalty_method == "Ensure All Grades Production":
        # Make penalties to prefer producing every grade at least once
        # Achieve by adding a soft penalty for grades with zero total production across horizon
        eff_stockout_pen = base_stockout_penalty
        eff_transition_pen = base_transition_penalty
        eff_run_start_pen = base_run_start_penalty // 2
        continuity_bonus = 10

        # stockout still penalized
        for grade in grades:
            for d in range(num_days):
                objective_terms.append(eff_stockout_pen * stockout[(grade, d)])

        # penalize transitions lightly
        for tvar in total_transition_bools:
            objective_terms.append(eff_transition_pen * tvar)

        # run starts moderate
        for r in run_start_bools:
            objective_terms.append(eff_run_start_pen * r)

        # Add soft penalty if a grade is never produced (zero total production)
        for grade in grades:
            # create indicator produced_flag_g = 1 if grade produced at least once
            produced_flag = model.NewBoolVar(f"produced_flag_{grade}")
            production_presence_vars = []
            for line in allowed_lines.get(grade, []):
                for d in range(num_days):
                    if (grade, line, d) in is_producing:
                        production_presence_vars.append(is_producing[(grade, line, d)])
            if production_presence_vars:
                # produced_flag <= sum(production_presence_vars)
                # if any prod var is 1, produced_flag can be 1. If none, produced_flag remains 0.
                # To ensure flag is 1 when any presence var is 1:
                model.Add(sum(production_presence_vars) >= 1).OnlyEnforceIf(produced_flag)
                model.Add(produced_flag == 0).OnlyEnforceIf(sum(production_presence_vars) == 0)
                # penalize not producing: penalty_if_not_produced * (1 - produced_flag)
                penalty_for_not_produced = int(max(100, base_stockout_penalty))  # encourage producing each grade
                obj_term = model.NewIntVar(0, 10 ** 7, f"prod_missing_pen_{grade}")
                # obj_term == penalty_for_not_produced * (1 - produced_flag)
                # Implement linearization: obj_term >= penalty_for_not_produced * (1 - produced_flag)
                model.Add(obj_term >= penalty_for_not_produced * (1 - produced_flag))
                objective_terms.append(obj_term)

    elif penalty_method == "Minimize Stockouts":
        # FIXED logic:
        # - Strongly prioritize eliminating stockout quantities.
        # - Make transitions and run starts cheap so solver can switch to prevent stockouts.
        # - Permit idle (no penalty) so solver can build inventory before demand peaks.
        # - Remove previous lookahead deficits and impossible inventory shaping constraints.
        eff_stockout_pen = max(1, base_stockout_penalty * 20)    # make this large
        eff_transition_pen = max(1, base_transition_penalty // 20)  # make transitions cheap
        eff_run_start_pen = max(1, base_run_start_penalty // 20)    # make run starts cheap
        eff_idle_pen = 0
        continuity_bonus = 5  # small bonus to encourage continuity but not dominant

        # Apply stockout penalties strongly
        for grade in grades:
            for d in range(num_days):
                objective_terms.append(eff_stockout_pen * stockout[(grade, d)])

        # Make transitions cheap (so solver can switch grades to prevent shortages)
        for tvar in total_transition_bools:
            objective_terms.append(eff_transition_pen * tvar)

        # Run starts cheap
        for r in run_start_bools:
            objective_terms.append(eff_run_start_pen * r)

        # Idle days allowed: we do NOT add idle penalties here (eff_idle_pen == 0)
        # (This lets the solver intentionally leave some lines idle if that helps avoid an expensive transition
        # or to time production to build inventory for critical grades.)
        # Note: since production is full-capacity-or-zero, idling a line will free capacity to produce the other grade elsewhere
        # (depending on allowed_lines). With cheap transitions solver can rearrange schedules to reduce stockouts.

        # Small continuity bonus optional
        for line in lines:
            for d in range(num_days - 1):
                for grade in grades:
                    if (grade, line, d) in is_producing and (grade, line, d + 1) in is_producing:
                        cont_bool = model.NewBoolVar(f"cont_{grade}_{line}_{d}")
                        model.AddBoolAnd([is_producing[(grade, line, d)], is_producing[(grade, line, d + 1)]]).OnlyEnforceIf(cont_bool)
                        model.Add(cont_bool == 0).OnlyEnforceIf(is_producing[(grade, line, d)].Not())
                        model.Add(cont_bool == 0).OnlyEnforceIf(is_producing[(grade, line, d + 1)].Not())
                        objective_terms.append(-continuity_bonus * cont_bool)

    elif penalty_method == "Minimize Transitions":
        # Run-Start minimization mode:
        # - penalize run starts and transitions heavily
        # - allow some stockout penalty but prefer stable long runs
        eff_transition_pen = max(1, base_transition_penalty * 5)
        eff_run_start_pen = max(1, base_run_start_penalty * 5)
        eff_stockout_pen = max(1, base_stockout_penalty // 5)  # tolerates small stockouts to reduce transitions
        continuity_bonus = 50  # high reward for staying continuous

        # Encourage continuity strongly (negative objective terms)
        for line in lines:
            for d in range(num_days - 1):
                for grade in grades:
                    if (grade, line, d) in is_producing and (grade, line, d + 1) in is_producing:
                        cont_bool = model.NewBoolVar(f"cont_{grade}_{line}_{d}")
                        model.AddBoolAnd([is_producing[(grade, line, d)], is_producing[(grade, line, d + 1)]]).OnlyEnforceIf(cont_bool)
                        model.Add(cont_bool == 0).OnlyEnforceIf(is_producing[(grade, line, d)].Not())
                        model.Add(cont_bool == 0).OnlyEnforceIf(is_producing[(grade, line, d + 1)].Not())
                        objective_terms.append(-continuity_bonus * cont_bool)

        # Penalize run starts and transitions
        for r in run_start_bools:
            objective_terms.append(eff_run_start_pen * r)
        for tvar in total_transition_bools:
            objective_terms.append(eff_transition_pen * tvar)

        # Still penalize stockouts but lower weight
        for grade in grades:
            for d in range(num_days):
                objective_terms.append(eff_stockout_pen * stockout[(grade, d)])

    else:
        # Unknown mode — fallback to Standard
        for grade in grades:
            for d in range(num_days):
                objective_terms.append(base_stockout_penalty * stockout[(grade, d)])
        for tvar in total_transition_bools:
            objective_terms.append(base_transition_penalty * tvar)
        for r in run_start_bools:
            objective_terms.append(base_run_start_penalty * r)

    # Final objective composition
    if objective_terms:
        model.Minimize(sum(objective_terms))
    else:
        model.Minimize(0)

    if progress_callback:
        progress_callback(0.8, "Solving the optimization model")

    # Solver configuration
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max(1.0, float(time_limit_min) * 60.0)
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED
    solver.parameters.log_search_progress = False

    # Prepare callback
    solution_cb = SolutionCallback(production, inventory, stockout, is_producing,
                                   grades, lines, dates, formatted_dates, num_days)

    status = solver.Solve(model, solution_cb)

    if progress_callback:
        progress_callback(1.0, "Optimization finished")

    return status, solution_cb, solver
