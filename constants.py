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

# UI Theme Colors 
THEME_COLORS = {
    # Primary Colors - Blue Corporate
    'primary': '#5E7CE2',
    'on_primary': '#FFFFFF',
    'primary_container': '#E8EEFF',
    'on_primary_container': '#0D1B54',
    
    # Secondary Colors - Green
    'secondary': '#67C23A', 
    'on_secondary': '#FFFFFF',
    'secondary_container': '#F0F9EB',
    'on_secondary_container': '#1F4A0D',
    
    # Tertiary Colors - Orange/Amber
    'tertiary': '#E6A23C',
    'on_tertiary': '#FFFFFF',
    'tertiary_container': '#FDF6EC',
    'on_tertiary_container': '#4A3000',
    
    # Surface Colors
    'surface': '#FFFFFF',
    'on_surface': '#303133',
    'surface_variant': '#F5F7FA',
    'on_surface_variant': '#606266',
    
    # Background
    'background': '#F8FAFC',
    'on_background': '#303133',
    
    # Outline & Borders
    'outline': '#DCDFE6',
    'outline_variant': '#E4E7ED',
    
    # Semantic Colors
    'error': '#F56C6C',
    'on_error': '#FFFFFF',
    'error_container': '#FEF0F0',
    
    'success': '#67C23A',
    'on_success': '#FFFFFF',
    'success_container': '#F0F9EB',
    
    'warning': '#E6A23C',
    'on_warning': '#FFFFFF',
    'warning_container': '#FDF6EC',
    
    'info': '#5E7CE2',
    'on_info': '#FFFFFF',
    'info_container': '#E8EEFF',
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
SS_GRADE_COLORS = "grade_colors"  # Store consistent grade colors
SS_THEME = "app_theme"  # Store theme preference (light/dark)
