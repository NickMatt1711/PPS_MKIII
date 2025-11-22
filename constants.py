"""
Configuration and constants for the Polymer Production Scheduler
"""

# Application Configuration
APP_TITLE = "Polymer Production Scheduler"
APP_ICON = "🏭"
VERSION = "3.0.0"

# Default Optimization Parameters
DEFAULT_TIME_LIMIT_MIN = 10
DEFAULT_BUFFER_DAYS = 3
DEFAULT_STOCKOUT_PENALTY = 10
DEFAULT_TRANSITION_PENALTY = 10
DEFAULT_CONTINUITY_BONUS = 1

# Solver Configuration
SOLVER_NUM_WORKERS = 8
SOLVER_RANDOM_SEED = 42

# UI Theme Colors (Material Design Palette)
THEME_COLORS = {
    'primary': '#5E7CE2',
    'primary_light': '#E8EEFF',
    'secondary': '#67C23A',
    'secondary_light': '#F0F9EB',
    'accent': '#E6A23C',
    'accent_light': '#FDF6EC',
    'error': '#F56C6C',
    'error_light': '#FEF0F0',
    'success': '#67C23A',
    'success_light': '#F0F9EB',
    'warning': '#E6A23C',
    'warning_light': '#FDF6EC',
    'info': '#909399',
    'info_light': '#F4F4F5',
    'text_primary': '#303133',
    'text_regular': '#606266',
    'text_secondary': '#909399',
    'border_base': '#DCDFE6',
    'border_light': '#E4E7ED',
    'bg_light': '#F5F7FA',
    'bg_white': '#FFFFFF',
}

# Chart Colors (Soft Material Palette)
CHART_COLORS = [
    '#5E7CE2', '#67C23A', '#E6A23C', '#F56C6C', '#409EFF',
    '#85CE61', '#EEBC59', '#EF7C8E', '#6CBFFF', '#95DE64',
    '#FFD666', '#FF9C9C', '#40C9C6', '#73D897', '#FFC069',
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

# Wizard Stage Names
STAGE_UPLOAD = "upload"
STAGE_PREVIEW = "preview"
STAGE_RESULTS = "results"

# Session State Keys
SS_STAGE = "wizard_stage"
SS_UPLOADED_FILE = "uploaded_file"
SS_EXCEL_DATA = "excel_data"
SS_OPTIMIZATION_PARAMS = "opt_params"
SS_SOLUTION = "solution"
SS_SOLVER_STATUS = "solver_status"
