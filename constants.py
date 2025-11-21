"""
Global constants and configuration for the Polymer Production Scheduler.

This module contains all application-wide constants including:
- Optimization parameters
- UI configuration
- Validation rules
- Color schemes
"""

from typing import Dict, List

# ============================================================================
# OPTIMIZATION DEFAULTS
# ============================================================================

# Solver parameters
DEFAULT_TIME_LIMIT = 10  # minutes
DEFAULT_BUFFER_DAYS = 3  # days
DEFAULT_NUM_SEARCH_WORKERS = 8
DEFAULT_RANDOM_SEED = 42

# Objective weights (hierarchical)
DEFAULT_STOCKOUT_PENALTY = 1000  # Critical: sales impact
DEFAULT_TRANSITION_PENALTY = 100  # Important: operations cost
DEFAULT_INVENTORY_HOLDING_COST = 1  # Efficiency: storage cost
DEFAULT_CLOSING_INVENTORY_MULTIPLIER = 3  # Extra weight for closing targets

# Solver advanced parameters
DEFAULT_LINEARIZATION_LEVEL = 2
DEFAULT_PROBING_LEVEL = 2
DEFAULT_SYMMETRY_LEVEL = 4

# ============================================================================
# DATA VALIDATION
# ============================================================================

# Required Excel sheet names
REQUIRED_SHEETS = ["Plant", "Inventory", "Demand"]

# Required Plant sheet columns
PLANT_REQUIRED_COLUMNS = [
    "Plant",
    "Capacity per day",
    "Material Running",
    "Expected Run Days",
    "Shutdown Start Date",
    "Shutdown End Date"
]

# Required Inventory sheet columns
INVENTORY_REQUIRED_COLUMNS = [
    "Grade Name",
    "Opening Inventory",
    "Min. Inventory",
    "Max. Inventory",
    "Min. Run Days",
    "Max. Run Days",
    "Force Start Date",
    "Lines",
    "Rerun Allowed",
    "Min. Closing Inventory"
]

# Transition sheet detection keyword
TRANSITION_KEYWORD = "transition"

# Value constraints
MAX_INVENTORY_VALUE = 1000000000
MAX_RUN_DAYS = 9999
MIN_RUN_DAYS = 1

# ============================================================================
# UI CONFIGURATION
# ============================================================================

# Color schemes for grades (Plotly qualitative palettes)
GRADE_COLOR_PALETTES = [
    "Vivid",
    "Bold",
    "Pastel",
    "Set1",
    "Set2",
    "Set3"
]

DEFAULT_COLOR_PALETTE = "Vivid"

# Chart dimensions
GANTT_HEIGHT = 350
INVENTORY_CHART_HEIGHT = 420
TABLE_HEIGHT = 300

# Date formatting
DATE_FORMAT = "%d-%b-%y"
DATE_FORMAT_LONG = "%d-%B-%Y"

# ============================================================================
# UI TEXT AND LABELS
# ============================================================================

APP_TITLE = "🏭 Polymer Production Scheduler"
APP_SUBTITLE = "Optimized Multi-Plant Production Planning"

STEP_LABELS = {
    1: "Upload Data",
    2: "Configure & Preview",
    3: "View Results"
}

TAB_LABELS = {
    "production": "📅 Production Schedule",
    "summary": "📊 Summary Analytics",
    "inventory": "📦 Inventory Trends"
}

METRIC_LABELS = {
    "objective": "Objective Value",
    "transitions": "Transitions",
    "stockouts": "Stockouts",
    "solve_time": "Solve Time"
}

# ============================================================================
# BUSINESS RULES
# ============================================================================

# Rerun allowed default values
RERUN_NOT_ALLOWED_VALUES = ["no", "n", "false", "0"]

# Transition matrix allowed values
TRANSITION_ALLOWED_VALUE = "yes"

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES = {
    "file_upload": "Please upload an Excel file to continue.",
    "missing_sheet": "Missing required sheet: {sheet_name}",
    "missing_column": "Missing required column '{column}' in sheet '{sheet}'",
    "invalid_data": "Invalid data in {location}: {details}",
    "solver_infeasible": "No feasible solution found. Please review constraints.",
    "solver_timeout": "Solver timed out. Consider increasing time limit.",
    "unknown_error": "An unexpected error occurred: {error}"
}

# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

SUCCESS_MESSAGES = {
    "file_uploaded": "✅ File uploaded successfully!",
    "optimal_solution": "✅ Optimal solution found!",
    "feasible_solution": "✅ Feasible solution found!",
    "data_validated": "✅ Data validation passed"
}

# ============================================================================
# WARNING MESSAGES
# ============================================================================

WARNING_MESSAGES = {
    "shutdown_invalid": "⚠️ Shutdown start date after end date for {plant}. Ignoring shutdown.",
    "shutdown_outside_horizon": "ℹ️ Shutdown period for {plant} is outside planning horizon",
    "no_transition_matrix": "ℹ️ No transition matrix found for {plant}. Assuming no transition constraints.",
    "invalid_force_date": "⚠️ Force start date '{date}' for grade '{grade}' on plant '{plant}' not found in demand dates"
}

# ============================================================================
# CSS CLASSES
# ============================================================================

CSS_CLASSES = {
    "metric_primary": "primary",
    "metric_success": "success",
    "metric_warning": "warning",
    "metric_info": "info",
    "chip_success": "chip success",
    "chip_warning": "chip warning",
    "chip_info": "chip info",
    "alert_info": "alert-box info",
    "alert_success": "alert-box success",
    "alert_warning": "alert-box warning"
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_error_message(key: str, **kwargs) -> str:
    """Get formatted error message."""
    return ERROR_MESSAGES.get(key, ERROR_MESSAGES["unknown_error"]).format(**kwargs)

def get_success_message(key: str) -> str:
    """Get success message."""
    return SUCCESS_MESSAGES.get(key, "")

def get_warning_message(key: str, **kwargs) -> str:
    """Get formatted warning message."""
    return WARNING_MESSAGES.get(key, "").format(**kwargs)
