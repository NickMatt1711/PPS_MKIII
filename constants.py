"""
Configuration and constants for the Polymer Production Scheduler
Enhanced UX version with proper stage management
"""

# Application Configuration
APP_TITLE = "Polymer Production Scheduler"
APP_ICON = "🏭"
VERSION = "3.1.0"

# Default Optimization Parameters
DEFAULT_TIME_LIMIT_MIN = 10
DEFAULT_BUFFER_DAYS = 3
DEFAULT_STOCKOUT_PENALTY = 10
DEFAULT_TRANSITION_PENALTY = 10
DEFAULT_CONTINUITY_BONUS = 1

# Solver Configuration
SOLVER_NUM_WORKERS = 8
SOLVER_RANDOM_SEED = 42

# Stage Management (proper numeric stages)
STAGE_UPLOAD = 0
STAGE_PREVIEW = 1
STAGE_OPTIMIZING = 2
STAGE_RESULTS = 3

# Chart Colors (Soft Material Palette)
CHART_COLORS = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#06b6d4', '#14b8a6', '#f97316', '#ec4899', '#6366f1',
    '#84cc16', '#a855f7', '#22d3ee', '#fb923c', '#f43f5e',
]

# File Upload Configuration
ALLOWED_EXTENSIONS = ['xlsx']
MAX_FILE_SIZE_MB = 50

# Required Excel Sheets
REQUIRED_SHEETS = ['Plant', 'Inventory', 'Demand']
OPTIONAL_SHEET_PREFIX = 'Transition_'

# Excel Column Names
PLANT_COLUMNS = {
    'plant': 'Plant',
    'capacity': 'Capacity per day',
    'material_running': 'Material Running',
    'expected_days': 'Expected Run Days',
    'shutdown_start': 'Shutdown Start Date',
    'shutdown_end': 'Shutdown End Date',
}

INVENTORY_COLUMNS = {
    'grade': 'Grade Name',
    'opening': 'Opening Inventory',
    'min_inv': 'Min. Inventory',
    'max_inv': 'Max. Inventory',
    'min_run': 'Min. Run Days',
    'max_run': 'Max. Run Days',
    'force_start': 'Force Start Date',
    'lines': 'Lines',
    'rerun': 'Rerun Allowed',
    'min_closing': 'Min. Closing Inventory',
}

# Session State Keys
SS_STAGE = "wizard_stage"
SS_UPLOADED_FILE = "uploaded_file"
SS_EXCEL_DATA = "excel_data"
SS_OPTIMIZATION_PARAMS = "opt_params"
SS_SOLUTION = "solution"
SS_SOLVER_STATUS = "solver_status"
SS_GRADE_COLORS = "grade_colors"
SS_THEME = "app_theme"
