import os
print("WORKING DIR:", os.getcwd())
print("FILES:", os.listdir())

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
from ui_components import (
    render_header,
    render_sidebar_inputs,
    render_run_button_message
)

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

# Add debug info
st.subheader("🔍 Problem Details")
st.write(f"Number of grades: {len(instance.get('grades', []))}")
st.write(f"Number of production lines: {len(instance.get('lines', []))}")
st.write(f"Planning horizon: {len(instance.get('dates', []))} days")

# Show force start dates
force_starts = instance.get('force_start_date', {})
if force_starts:
    st.write("**Force Start Dates:**")
    for grade_plant, date in force_starts.items():
        if date:  # Only show if date is not None
            grade, plant = grade_plant
            st.write(f"- {grade} on {plant}: {date}")

# Show shutdown periods
shutdowns = instance.get('shutdown_day_indices', {})
if shutdowns:
    st.write("**Shutdown Periods:**")
    for line, days in shutdowns.items():
        if days:  # Only show if there are shutdown days
            st.write(f"- {line}: {len(days)} shutdown days")

# Check demand vs capacity
total_demand = sum(instance.get('demand', {}).values())
total_capacity = sum(instance.get('capacities', {}).values()) * len(instance.get('dates', []))
st.write(f"**Capacity Analysis:**")
st.write(f"- Total demand: {total_demand:,.0f} MT")
st.write(f"- Total capacity: {total_capacity:,.0f} MT")
if total_demand > total_capacity:
    st.warning(f"⚠️ Total demand ({total_demand:,.0f} MT) exceeds total capacity ({total_capacity:,.0f} MT)")

# Create progress elements
progress_bar = st.progress(0)
status_text = st.empty()

with st.spinner("Running CP-SAT solver..."):
    # Update progress
    progress_bar.progress(30)
    status_text.markdown('<div class="info-box">🔧 Building optimization model...</div>', unsafe_allow_html=True)
    
    try:
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
        
        progress_bar.progress(100)
        
    except Exception as e:
        progress_bar.progress(0)
        status_text.markdown(f'<div class="info-box">❌ Solver error: {str(e)}</div>', unsafe_allow_html=True)
        st.stop()

st.subheader("Solver Status")
st.write(f"Status: **{solver_result['status']}**")

if solver_result["status"] == "INFEASIBLE":
    status_text.markdown('<div class="info-box">❌ Problem is infeasible</div>', unsafe_allow_html=True)
    
    st.error("❌ Problem is infeasible - constraints cannot all be satisfied")
    
    st.info("""
    **Common issues that cause infeasibility:**
    - Demand is too high compared to production capacity
    - Minimum run days are too long for the available production days
    - Minimum closing inventory requirements are too high
    - Shutdown periods conflict with mandatory production requirements
    - Transition rules are too restrictive
    - Force start dates cannot be satisfied
    
    **Suggestions:**
    - Reduce minimum run days requirements
    - Lower minimum closing inventory targets  
    - Increase production capacity
    - Reduce demand forecasts
    - Adjust shutdown periods
    - Relax force start date constraints
    """)
    
    st.stop()

if solver_result["best"] is None:
    status_text.markdown('<div class="info-box">❌ No feasible solution found</div>', unsafe_allow_html=True)
    st.error("❌ Solver could not find a feasible solution.")
    st.stop()

# Show success based on status
if solver_result["status"] == "OPTIMAL":
    status_text.markdown('<div class="success-box">✅ Optimization completed optimally!</div>', unsafe_allow_html=True)
else:
    status_text.markdown('<div class="success-box">✅ Optimization completed with feasible solution!</div>', unsafe_allow_html=True)

st.success("Optimization completed successfully!")

# Show key metrics from new solution format
if solver_result["best"] and 'transitions' in solver_result["best"]:
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Objective Value", f"{solver_result['best']['objective']:,.0f}")
    with col2:
        total_transitions = solver_result["best"]['transitions']['total']
        st.metric("Total Transitions", total_transitions)
    with col3:
        total_stockouts = sum(sum(solver_result["best"]['stockout'][g].values()) for g in instance['grades'])
        st.metric("Total Stockouts", f"{total_stockouts:,.0f} MT")
    with col4:
        st.metric("Planning Horizon", f"{len(instance['dates'])} days")

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
