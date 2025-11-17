# constants.py
"""
Global constants and small helpers.
"""

DEFAULT_STOCKOUT_PENALTY = 10
DEFAULT_TRANSITION_PENALTY = 10
DEFAULT_TIME_LIMIT = 10  # Changed from DEFAULT_TIME_LIMIT_MIN
DEFAULT_BUFFER_DAYS = 3  # Added this constant
DEFAULT_NUM_SEARCH_WORKERS = 8

# For detecting transition sheets
TRANSITION_KEYWORD = "transition"
