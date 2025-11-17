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
    DEFAULT_TIME_LIMIT_MIN,
    DEFAULT_BUFFER_DAYS,
    DEFAULT_MIN_INVENTORY_PENALTY,
    DEFAULT_MIN_CLOSING_PENALTY
)

from data_loader import load_excel_data, process_rerun_and_penalty_data
from preview_tables import show_preview_tables
from ui_components import (
    header,
    footer,
    render_sidebar_inputs
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
# 1. PAGE HEADER
# ----------------------------------------
header()

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
# 3. LOAD AND PROCESS DATA
# ----------------------------------------
with st.spinner("Reading template..."):
    try:
        instance = load_excel_data(uploaded_file)
        
        # NEW: Process rerun and penalty data
        if 'inventory_df' in instance:
            rerun_allowed, min_inv_penalty, min_closing_penalty = process_rerun_and_penalty_data(instance['inventory_df'])
            instance['rerun_allowed'] = rerun_allowed
            instance['min_inv_penalty'] = min_inv_penalty
            instance['min_closing_penalty'] = min_closing_penalty
            
            # Display rerun rules
            st.sidebar.header("🔁 Rerun Rules")
            for grade, allowed in rerun_allowed.items():
                status = "✅ ALLOWED" if allowed else "❌ NOT ALLOWED"
                st.sidebar.write(f"{grade}: {status}")
                
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
# 5. ENHANCED SIDEBAR PARAMETERS
# ----------------------------------------
(
    transition_penalty,
    stockout_penalty,
    time_limit,
    buffer_days,
    min_inv_penalty,
    min_closing_penalty
) = render_sidebar_inputs(
    default_transition=DEFAULT_TRANSITION_PENALTY,
    default_stockout=DEFAULT_STOCKOUT_PENALTY,
    default_timelimit=DEFAULT_TIME_LIMIT_MIN,
    default_buffer=DEFAULT_BUFFER_DAYS,
)

# ----------------------------------------
# 6. RUN SOLVER BUTTON
# ----------------------------------------
run_clicked = st.button("🚀 Run Optimization")

if not run_clicked:
    st.info("Click the button above to run the optimization with enhanced constraints.")
    st.stop()

# ----------------------------------------
# 7. RUN ENHANCED OPTIMIZER
# ----------------------------------------
st.header("⚙️ Optimization Results")

with st.spinner("Running enhanced CP-SAT solver with inventory penalties..."):
    solver_result = solve(
        instance,
        {
            "time_limit_min": time_limit,
            "stockout_penalty": stockout_penalty,
            "transition_penalty": transition_penalty,
            "min_inventory_penalty": min_inv_penalty,
            "min_closing_penalty": min_closing_penalty,
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

# NEW: Display penalty analysis
if solver_result["best"] and 'min_inv_violations' in solver_result["best"]:
    violations = solver_result["best"]['min_inv_violations']
    closing_violations = solver_result["best"]['min_closing_violations']
    
    if violations or closing_violations:
        st.subheader("📊 Penalty Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            if violations:
                st.warning("Min Inventory Violations Detected")
                viol_df = pd.DataFrame([
                    {"Grade": g, "Day": d, "Violation": v} 
                    for (g, d), v in violations.items()
                ])
                st.dataframe(viol_df, use_container_width=True)
            else:
                st.success("✅ No min inventory violations")
        
        with col2:
            if closing_violations:
                st.warning("Min Closing Inventory Violations Detected")
                closing_df = pd.DataFrame([
                    {"Grade": g, "Violation": v} 
                    for g, v in closing_violations.items()
                ])
                st.dataframe(closing_df, use_container_width=True)
            else:
                st.success("✅ No min closing inventory violations")

# ----------------------------------------
# 8. CONVERT OUTPUT FOR VISUALIZATION
# ----------------------------------------
display_result = convert_solver_output_to_display(solver_result, instance)

# ----------------------------------------
# 9. PLOTLY VISUALS
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

# ----------------------------------------
# 10. FOOTER
# ----------------------------------------
footer()
