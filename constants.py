"""
Configuration constants, defaults, palettes and small utilities.
"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
SAMPLE_TEMPLATE = BASE_DIR / "polymer_production_template.xlsx"

DEFAULT_PARAMS = {
    "time_limit_min": 10,
    "buffer_days": 3,
    "stockout_penalty": 1000,
    "transition_penalty": 100,
    "holding_cost": 1,
}

# UI / color palette for grades (Plotly uses hex strings)
GRADE_PALETTE = [
    "#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A",
    "#19D3F3", "#FF6692", "#B6E880", "#FF97FF", "#FECB52"
]
