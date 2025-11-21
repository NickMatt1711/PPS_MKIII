"""
Polymer Production Scheduler (PPS_MKIII)
=========================================

A production scheduling optimization system for multi-plant polymer manufacturing.

Features:
- Multi-plant production optimization
- Inventory management with min/max constraints
- Grade transition matrix support
- Shutdown period handling
- Force start date constraints
- Run length optimization (min/max days)

Version: 3.0.0
Author: PPS Development Team
License: MIT
"""

__version__ = "3.0.0"
__author__ = "PPS Development Team"

# Module exports
from . import constants
from . import data_loader
from . import solver_cp_sat
from . import postprocessing
from . import preview_tables
from . import ui_components

__all__ = [
    "constants",
    "data_loader",
    "solver_cp_sat",
    "postprocessing",
    "preview_tables",
    "ui_components",
]
