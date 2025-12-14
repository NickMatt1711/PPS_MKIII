# solver_cp_sat.py
"""
CP-SAT Solver for Polymer Production Planning
Standard mode only
"""

from ortools.sat.python import cp_model
from typing import Dict, List, Tuple
import time
from constants import SOLVER_NUM_WORKERS, SOLVER_RANDOM_SEED

BIG_M = 10**7


# =========================
# Solution Callback
# =========================
class SolutionCallback(cp_model.CpSolverSolutionCallback):
    def __init__(
        self,
        is_producing,
        production,
        inventory,
        stockout,
        grades,
        lines,
        dates,
        formatted_dates,
        num_days,
    ):
        super().__init__()
        self.is_producing = is_producing
        self.production = production
        self.inventory = inventory
        self.stockout = stockout
        self.grades = grades
        self.lines = lines
        self.dates = dates
        self.formatted_dates = formatted_dates
        self.num_days = num_days
        self.solutions = []
        self.start_time = time.time()

    def on_solution_callback(self):
        sol = {
            "objective": self.ObjectiveValue(),
            "production": {},
            "inventory": {},
            "stockout": {},
            "schedule": {},
        }

        for g in self.grades:
            sol["production"][g] = {}
            sol["inventory"][g] = {}
            sol["stockout"][g] = {}

            for d in range(self.num_days):
                date = self.formatted_dates[d]
                sol["inventory"][g][date] = self.Value(self.inventory[(g, d)])
                so = self.Value(self.stockout[(g, d)])
                if so > 0:
                    sol["stockout"][g][date] = so

        for l in self.lines:
            sol["schedule"][l] = {}
            for d in range(self.num_days):
                date = self.formatted_dates[d]
                sol["schedule"][l][date] = None
                for g in self.grades:
                    if (g, l, d) in self.is_producing and self.Value(self.is_producing[(g, l, d)]) == 1:
                        sol["schedule"][l][date] = g
                        break

        self.solutions.append(sol)


# =========================
# Model Builder
# =========================
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
) -> Tuple[int, SolutionCallback, cp_model.CpSolver]:

    model = cp_model.CpModel()

    # =========================
    # Decision Variables
    # =========================
    is_producing = {}
    production = {}
    start = {}

    for g in grades:
        for l in allowed_lines[g]:
            for d in range(num_days):
                is_producing[(g, l, d)] = model.NewBoolVar(f"is_prod_{g}_{l}_{d}")
                production[(g, l, d)] = model.NewIntVar(0, capacities[l], f"prod_{g}_{l}_{d}")

                model.Add(production[(g, l, d)] == capacities[l]).OnlyEnforceIf(is_producing[(g, l, d)])
                model.Add(production[(g, l, d)] == 0).OnlyEnforceIf(is_producing[(g, l, d)].Not())

                if d == 0:
                    start[(g, l, d)] = is_producing[(g, l, d)]
                else:
                    start[(g, l, d)] = model.NewBoolVar(f"start_{g}_{l}_{d}")
                    model.Add(start[(g, l, d)] >= is_producing[(g, l, d)] - is_producing[(g, l, d - 1)])

    # =========================
    # One grade per line per day
    # =========================
    for l in lines:
        for d in range(num_days):
            model.Add(
                sum(is_producing[(g, l, d)] for g in grades if (g, l, d) in is_producing) <= 1
            )

    # =========================
    # Shutdown constraints
    # =========================
    for l, days in shutdown_periods.items():
        for d in days:
            for g in grades:
                if (g, l, d) in is_producing:
                    model.Add(is_producing[(g, l, d)] == 0)

    # =========================
    # Pre / Post shutdown grade
    # =========================
    for l, days in shutdown_periods.items():
        if not days:
            continue

        if l in pre_shutdown_grades and pre_shutdown_grades[l]:
            d = days[0] - 1
            g = pre_shutdown_grades[l]
            if d >= 0 and (g, l, d) in is_producing:
                model.Add(is_producing[(g, l, d)] == 1)

        if l in restart_grades and restart_grades[l]:
            d = days[-1] + 1
            g = restart_grades[l]
            if d < num_days and (g, l, d) in is_producing:
                model.Add(is_producing[(g, l, d)] == 1)

    # =========================
    # Material running logic
    # =========================
    for l, info in material_running_info.items():
    
        # info comes from app.py as a tuple: (material, expected_days)
        g, exp = info
    
        # Safety guard (fail fast, readable error)
        if not isinstance(info, tuple) or len(info) != 2:
            raise ValueError(
                f"material_running_info[{l}] must be (material, expected_days), got {info}"
            )
    
        if exp is None or exp == 0:
            # Produce on day 0 only
            if (g, l, 0) in is_producing:
                model.Add(is_producing[(g, l, 0)] == 1)
        else:
            # Force exact run
            for d in range(min(exp, num_days)):
                if (g, l, d) in is_producing:
                    model.Add(is_producing[(g, l, d)] == 1)
    
            # Mandatory changeover
            if exp < num_days and (g, l, exp) in is_producing:
                model.Add(is_producing[(g, l, exp)] == 0)


    # =========================
    # Run-length constraints
    # =========================
    for g in grades:
        for l in allowed_lines[g]:
            for d in range(num_days):
                minr = min_run_days[g]
                maxr = max_run_days[g]

                if minr:
                    end = min(num_days, d + minr)
                    model.Add(
                        sum(is_producing[(g, l, k)] for k in range(d, end)) >= minr * start[(g, l, d)]
                    )

                if maxr and d + maxr < num_days:
                    model.Add(
                        sum(is_producing[(g, l, k)] for k in range(d, d + maxr + 1)) <= maxr
                    )

            if not rerun_allowed[g]:
                model.Add(sum(start[(g, l, d)] for d in range(num_days)) <= 1)

    # =========================
    # Forbidden transitions
    # =========================
    for l, matrix in transition_rules.items():
        for g1 in grades:
            for g2 in grades:
                if matrix.get(g1, {}).get(g2) == "No":
                    for d in range(num_days - 1):
                        if (g1, l, d) in is_producing and (g2, l, d + 1) in is_producing:
                            model.Add(
                                is_producing[(g1, l, d)] + is_producing[(g2, l, d + 1)] <= 1
                            )

    # =========================
    # Inventory & demand
    # =========================
    inventory = {}
    stockout = {}
    inventory_penalty_terms = []

    for g in grades:
        for d in range(num_days + 1):
            inventory[(g, d)] = model.NewIntVar(0, BIG_M, f"inv_{g}_{d}")

        model.Add(inventory[(g, 0)] == initial_inventory[g])

        for d in range(num_days):
            produced = sum(
                production[(g, l, d)] for l in allowed_lines[g] if (g, l, d) in production
            )
            demand = demand_data[g].get(dates[d], 0)

            supplied = model.NewIntVar(0, BIG_M, f"supply_{g}_{d}")
            stockout[(g, d)] = model.NewIntVar(0, BIG_M, f"stockout_{g}_{d}")

            model.Add(supplied <= inventory[(g, d)] + produced)
            model.Add(supplied <= demand)
            model.Add(stockout[(g, d)] == demand - supplied)

            model.Add(inventory[(g, d + 1)] == inventory[(g, d)] + produced - supplied)
            model.Add(inventory[(g, d + 1)] <= max_inventory[g])

            if min_inventory[g] is not None:
                deficit = model.NewIntVar(0, BIG_M, f"mininv_def_{g}_{d}")
                model.Add(inventory[(g, d)] + deficit >= min_inventory[g])
                inventory_penalty_terms.append(deficit)

        if min_closing_inventory[g] is not None:
            cdef = model.NewIntVar(0, BIG_M, f"close_def_{g}")
            model.Add(inventory[(g, num_days)] + cdef >= min_closing_inventory[g])
            inventory_penalty_terms.append(3 * cdef)

    # =========================
    # Transitions (penalty)
    # =========================
    transition_terms = []
    for l in lines:
        for d in range(num_days - 1):
            for g1 in grades:
                for g2 in grades:
                    if g1 != g2 and (g1, l, d) in is_producing and (g2, l, d + 1) in is_producing:
                        t = model.NewBoolVar(f"tr_{g1}_{g2}_{l}_{d}")
                        model.Add(t >= is_producing[(g1, l, d)] + is_producing[(g2, l, d + 1)] - 1)
                        transition_terms.append(t)

    # =========================
    # Objective
    # =========================
    model.Minimize(
        stockout_penalty * sum(stockout.values())
        + transition_penalty * sum(transition_terms)
        + stockout_penalty * sum(inventory_penalty_terms)
    )

    # =========================
    # Solve
    # =========================
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_min * 60
    solver.parameters.num_search_workers = SOLVER_NUM_WORKERS
    solver.parameters.random_seed = SOLVER_RANDOM_SEED

    cb = SolutionCallback(
        is_producing,
        production,
        inventory,
        stockout,
        grades,
        lines,
        dates,
        formatted_dates,
        num_days,
    )

    status = solver.SolveWithSolutionCallback(model, cb)
    return status, cb, solver
