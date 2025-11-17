import streamlit as st
import pandas as pd
from datetime import datetime

# === MODULE IMPORTS ===
from constants import (
    DEFAULT_STOCKOUT_PENALTY,
    DEFAULT_TRANSITION_PENALTY,
    DEFAULT_TIME_LIMIT,
    DEFAULT_BUFFER_DAYS
)
from data_loader import load_excel_data
from preview_tables import show_preview_tables
from ui_components import render_header, render_sidebar_inputs, render_run_button_message
from solver_cp_sat import solve
from postprocessing import (
    convert_solver_output_to_display,
    plot_production_visuals,
    plot_inventory_charts
)


# ----------------------------------------
# STREAMLIT PAGE CONFIG
# ----------------------------------------
st.set_page_config(
    page_title="Polymer Production Sequencer",
    layout="wide"
)

# ----------------------------------------
# 1. PAGE HEADER (From test(1).py UX)
# ----------------------------------------
render_header()

# ----------------------------------------
# 2. EXCEL UPLOAD
# ----------------------------------------
uploaded_file = st.file_uploader(
    "Upload the Polymer Production Template (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=False
)

if uploaded_file is None:
    st.info("Please upload the template to continue.")
    st.stop()

# ----------------------------------------
# 3. LOAD DATA
# ----------------------------------------
with st.spinner("Reading template..."):
    try:
        instance = load_excel_data(uploaded_file)
    except Exception as e:
        st.error(f"Error reading template: {e}")
        st.stop()

st.success("Template loaded successfully!")

# ----------------------------------------
# 4. PREVIEW INPUT TABLES
# ----------------------------------------
st.header("📄 Input Data Preview")
show_preview_tables(instance)

# ----------------------------------------
# 5. SIDEBAR PARAMETERS
# ----------------------------------------
(
    transition_penalty,
    stockout_penalty,
    time_limit,
    buffer_days
) = render_sidebar_inputs(
    default_transition=DEFAULT_TRANSITION_PENALTY,
    default_stockout=DEFAULT_STOCKOUT_PENALTY,
    default_timelimit=DEFAULT_TIME_LIMIT,
    default_buffer=DEFAULT_BUFFER_DAYS,
)

# ----------------------------------------
# 6. RUN SOLVER BUTTON
# ----------------------------------------
run_clicked = st.button("🚀 Run Optimization")

if not run_clicked:
    render_run_button_message()
    st.stop()

# ----------------------------------------
# 7. RUN OPTIMIZER
# ----------------------------------------
st.header("⚙️ Optimization Results")

with st.spinner("Running CP-SAT solver..."):
    solver_result = solve(
        instance,
        {
            "time_limit_min": time_limit,
            "stockout_penalty": stockout_penalty,
            "transition_penalty": transition_penalty,
            "buffer_days": buffer_days,
            "num_search_workers": 8,
        }
    )

st.subheader("Solver Status")
st.write(f"Status: **{solver_result['status']}**")

if solver_result["best"] is None:
    st.error("❌ Solver could not find a feasible solution.")
    st.stop()

st.success("Optimization completed successfully!")

# ----------------------------------------
# 8. CONVERT OUTPUT FOR VISUALIZATION
# ----------------------------------------
display_result = convert_solver_output_to_display(solver_result, instance)

# ----------------------------------------
# 9. PLOTLY VISUALS (UNCHANGED)
# ----------------------------------------
st.header("📊 Production & Inventory Visualizations")

# Production Gantt + schedule tables
plot_production_visuals(
    display_result,
    instance,
    {"buffer_days": buffer_days}
)

# Inventory charts per grade
st.header("📦 Inventory Charts")
plot_inventory_charts(
    display_result,
    instance,
    {"buffer_days": buffer_days}
)

st.success("📈 All visualizations rendered successfully.")
