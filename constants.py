# constants.py
"""
Global constants and small helpers.
"""

DEFAULT_TIME_LIMIT_MIN = 10
DEFAULT_TIME_LIMIT = 10  # Added for compatibility
DEFAULT_STOCKOUT_PENALTY = 10
DEFAULT_TRANSITION_PENALTY = 10
DEFAULT_NUM_SEARCH_WORKERS = 8
DEFAULT_BUFFER_DAYS = 3  # Added missing constant

# For detecting transition sheets
TRANSITION_KEYWORD = "transition"
