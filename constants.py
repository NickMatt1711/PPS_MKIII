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
    # Primary colors (Blue-based industrial accent)
    'primary': '#3855A3',              # M3-style mid-chroma blue
    'primary_light': '#6F8CE6',        # Tone ~70 (hover states, subtle accents)
    'primary_container': '#DCE3FF',    # Tone ~90 container
    'on_primary': '#FFFFFF',

    # Secondary colors (Neutralized teal for supportive elements)
    'secondary': '#4B6B68',            # Low-chroma teal/industrial green
    'secondary_light': '#789C98',      # Tone ~70
    'secondary_container': '#DCE6E5',  # Tone ~92
    'on_secondary': '#FFFFFF',

    # Surface colors (Material 3 neutrals: warm-grey industrial surfaces)
    'surface': '#F9FAFB',              # Tone 98
    'surface_variant': '#E3E8EF',      # Tone 90 (cards, panels)
    'on_surface': '#1B1F24',           # Tone 15
    'on_surface_variant': '#5A636F',   # Tone 50

    # Background colors
    'background': '#F7F8FA',           # Slightly warm neutral
    'on_background': '#1A1D22',

    # Borders / outlines (M3 uses outline + outline-variant)
    'border': '#C6CDD7',               # Tone 80
    'border_light': '#E4E7EB',         # Tone 92
    'outline': '#9299A3',              # Tone 60

    # Error colors (Material 3 Red)
    'error': '#BA1A1A',                # Tone 40
    'error_light': '#FFEDEA',          # Tone 95
    'on_error': '#FFFFFF',

    # Success (Green but desaturated for industrial feel)
    'success': '#2F7D4F',              # Low chroma, strong contrast
    'success_light': '#E6F3EB',        # Tone 94
    'on_success': '#FFFFFF',

    # Warning (Amber, softened to match M3 tonal ramp)
    'warning': '#A66E00',              # Strong amber tone 40
    'warning_light': '#FFF4E3',        # Tone 95
    'on_warning': '#FFFFFF',

    # Info (Blue accent aligned with primary palette)
    'info': '#2E6BCF',                 # Tone 50–55 (solid contrast)
    'info_light': '#E7F0FF',           # Tone 94
    'on_info': '#FFFFFF',
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
