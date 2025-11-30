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

# UI Theme Colors (Material 3 Light Theme)
THEME_COLORS = {
    # Primary colors
    'primary': '#1e40af',           # Blue-700
    'primary_light': '#3b82f6',     # Blue-500
    'primary_container': '#dbeafe', # Blue-100
    'on_primary': '#ffffff',
    
    # Secondary colors
    'secondary': '#059669',         # Emerald-600
    'secondary_light': '#10b981',   # Emerald-500
    'secondary_container': '#d1fae5', # Emerald-100
    'on_secondary': '#ffffff',
    
    # Surface colors
    'surface': '#ffffff',
    'surface_variant': '#f1f5f9',   # Slate-100
    'on_surface': '#1e293b',        # Slate-800
    'on_surface_variant': '#64748b', # Slate-500
    
    # Background colors
    'background': '#f8fafc',        # Slate-50
    'on_background': '#0f172a',     # Slate-900
    
    # Border colors
    'border': '#cbd5e1',            # Slate-300
    'border_light': '#e2e8f0',      # Slate-200
    'outline': '#94a3b8',           # Slate-400
    
    # Semantic colors
    'error': '#ef4444',             # Red-500
    'error_light': '#fef2f2',       # Red-50
    'on_error': '#ffffff',
    
    'success': '#10b981',           # Emerald-500
    'success_light': '#f0fdf4',     # Green-50
    'on_success': '#ffffff',
    
    'warning': '#f59e0b',           # Amber-500
    'warning_light': '#fffbeb',     # Amber-50
    'on_warning': '#ffffff',
    
    'info': '#3b82f6',              # Blue-500
    'info_light': '#f0f9ff',        # Sky-50
    'on_info': '#ffffff',
}

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
SS_GRADE_COLORS = "grade_colors"
SS_THEME = "app_theme"
