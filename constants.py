# constants.py
"""
Global constants and small helpers.
"""

DEFAULT_TIME_LIMIT_MIN = 10
DEFAULT_STOCKOUT_PENALTY = 10
DEFAULT_TRANSITION_PENALTY = 10
DEFAULT_NUM_SEARCH_WORKERS = 8
DEFAULT_BUFFER_DAYS = 3

# For detecting transition sheets
TRANSITION_KEYWORD = "transition"

# Enhanced penalty constants
DEFAULT_MIN_INVENTORY_PENALTY = 5
DEFAULT_MIN_CLOSING_PENALTY = 8
