"""
Global Constants and Configuration
===================================

Centralized configuration for the Polymer Production Scheduler.
"""

from typing import Dict, List

# ============================================================================
# OPTIMIZATION PARAMETERS
# ============================================================================

# Default solver settings
DEFAULT_TIME_LIMIT_MIN: int = 10
DEFAULT_BUFFER_DAYS: int = 3
DEFAULT_NUM_SEARCH_WORKERS: int = 8
DEFAULT_RANDOM_SEED: int = 42

# Objective function weights
DEFAULT_STOCKOUT_PENALTY: int = 10
DEFAULT_TRANSITION_PENALTY: int = 10

# Constraint parameters
MIN_RUN_DAYS_DEFAULT: int = 1
MAX_RUN_DAYS_DEFAULT: int = 9999
MIN_INVENTORY_DEFAULT: float = 0.0
MAX_INVENTORY_DEFAULT: float = 1e9

# ============================================================================
# EXCEL TEMPLATE CONFIGURATION
# ============================================================================

# Required sheet names
SHEET_PLANT: str = "Plant"
SHEET_INVENTORY: str = "Inventory"
SHEET_DEMAND: str = "Demand"

# Plant sheet columns
PLANT_COLS: Dict[str, str] = {
    "name": "Plant",
    "capacity": "Capacity per day",
    "material_running": "Material Running",
    "expected_days": "Expected Run Days",
    "shutdown_start": "Shutdown Start Date",
    "shutdown_end": "Shutdown End Date",
}

# Inventory sheet columns
INVENTORY_COLS: Dict[str, str] = {
    "grade": "Grade Name",
    "opening_inv": "Opening Inventory",
    "min_inv": "Min. Inventory",
    "max_inv": "Max. Inventory",
    "min_run": "Min. Run Days",
    "max_run": "Max. Run Days",
    "force_start": "Force Start Date",
    "lines": "Lines",
    "rerun": "Rerun Allowed",
    "min_closing": "Min. Closing Inventory",
}

# Transition sheet naming pattern
TRANSITION_KEYWORD: str = "transition"
TRANSITION_YES_VALUES: List[str] = ["yes", "y", "true", "1"]

# ============================================================================
# UI/UX CONFIGURATION
# ============================================================================

# Color scheme - Material Design inspired
COLOR_PRIMARY: str = "#667eea"
COLOR_SECONDARY: str = "#764ba2"
COLOR_SUCCESS: str = "#4caf50"
COLOR_WARNING: str = "#ff9800"
COLOR_ERROR: str = "#f44336"
COLOR_INFO: str = "#2196f3"

# Plotly color palette for grades
GRADE_COLORS: List[str] = [
    "#667eea", "#764ba2", "#f093fb", "#4facfe",
    "#43e97b", "#fa709a", "#feca57", "#ff6348",
    "#ee5a6f", "#c44569", "#786fa6", "#f8b500",
]

# Status messages
STATUS_OPTIMAL: str = "OPTIMAL"
STATUS_FEASIBLE: str = "FEASIBLE"
STATUS_INFEASIBLE: str = "INFEASIBLE"
STATUS_UNKNOWN: str = "UNKNOWN"

# ============================================================================
# VALIDATION RULES
# ============================================================================

# File validation
MAX_FILE_SIZE_MB: int = 50
ALLOWED_FILE_EXTENSIONS: List[str] = ["xlsx"]

# Data validation
MIN_PLANNING_DAYS: int = 1
MAX_PLANNING_DAYS: int = 365
MIN_CAPACITY: float = 0.1
MAX_CAPACITY: float = 10000.0

# Constraint validation
MIN_STOCKOUT_PENALTY: int = 1
MAX_STOCKOUT_PENALTY: int = 10000
MIN_TRANSITION_PENALTY: int = 1
MAX_TRANSITION_PENALTY: int = 10000

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_MESSAGES: Dict[str, str] = {
    "missing_sheet": "Required sheet '{}' not found in Excel file",
    "missing_column": "Required column '{}' not found in sheet '{}'",
    "invalid_data": "Invalid data in column '{}': {}",
    "no_grades": "No grades found in inventory sheet",
    "no_plants": "No plants found in plant sheet",
    "invalid_date": "Invalid date format in column '{}': {}",
    "capacity_zero": "Plant '{}' has zero or negative capacity",
    "shutdown_invalid": "Shutdown dates for plant '{}' are invalid",
}

# ============================================================================
# DISPLAY CONFIGURATION
# ============================================================================

# Date format for display
DATE_FORMAT_DISPLAY: str = "%d-%b-%y"
DATE_FORMAT_INPUT: str = "%Y-%m-%d"

# Table display limits
MAX_PREVIEW_ROWS: int = 100

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL: str = "INFO"
