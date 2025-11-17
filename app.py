mport os
print("WORKING DIR:", os.getcwd())
print("FILES:", os.listdir())

try:
    import streamlit as st
    import pandas as pd
    from datetime import datetime
    
    # Try to import ortools to check if it's available
    from ortools.sat.python import cp_model
    
except ImportError as e:
    import streamlit as st
    st.error(f"Missing dependency: {e}")
    st.info("Please make sure all requirements are installed. Check the requirements.txt file.")
    st.stop()

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
    page_title="Polymer Production Scheduler",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------
# 1. PAGE HEADER
# ----------------------------------------
render_header()

# ----------------------------------------
# 2. SIDEBAR PARAMETERS (Before upload for better UX)
# ----------------------------------------
st.sidebar.markdown("### 📋 Data Input")

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
# 3. EXCEL UPLOAD
# ----------------------------------------
uploaded_file = st.file_uploader(
    "📤 Upload the Polymer Production Template (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=False,
    help="Upload an Excel file with Plant, Inventory, and Demand sheets"
)

if uploaded_file is None:
    st.markdown("""
    <div class="info-box" style="margin-top: 2rem;">
        <h3>🚀 Getting Started</h3>
        <ol>
            <li>Upload your production template Excel file above</li>
            <li>Review and validate the input data</li>
            <li>Adjust optimization parameters in the sidebar if needed</li>
            <li>Click "Run Optimization" to generate the schedule</li>
        </ol>
        <p><strong>Need a template?</strong> Make sure your Excel file contains:
        <ul>
            <li><strong>Plant</strong> sheet: Plant capacities and shutdown schedules</li>
            <li><strong>Inventory</strong> sheet: Grade parameters and constraints</li>
            <li><strong>Demand</strong> sheet: Daily demand forecasts by grade</li>
            <li><strong>Transition_[PlantName]</strong> sheets (optional): Transition rules</li>
        </ul>
        </p>
    </div>
    """, unsafe_allow_html=True)
    footer()
    st.stop()

st.success("✅ File uploaded successfully!")

# ----------------------------------------
# 4. LOAD DATA
# ----------------------------------------
with st.spinner("📖 Reading template..."):
    try:
        instance = load_excel_data(uploaded_file)
    except Exception as e:
        st.error(f"❌ Error reading template: {e}")
        import traceback
        with st.expander("🔍 View Error Details"):
            st.code(traceback.format_exc())
        st.stop()

st.success("✅ Template loaded and validated successfully!")

# ----------------------------------------
# 5. PREVIEW INPUT TABLES
# ----------------------------------------
st.markdown("---")
show_preview_tables(instance)

# ----------------------------------------
# 6. RUN SOLVER BUTTON
# ----------------------------------------
st.markdown("---")
run_clicked = st.button("🚀 Run Optimization", type="primary", use_container_width=True)

if not run_clicked:
    render_run_button_message()
    footer()
    st.stop()

# ----------------------------------------
# 7. RUN OPTIMIZER
# ----------------------------------------
st.markdown("---")
st.markdown('<div class="section-header">⚙️ Optimization Results</div>', unsafe_allow_html=True)

progress_bar = st.progress(0)
status_text = st.empty()

status_text.markdown('<div class="info-box">🔄 Preprocessing data...</div>', unsafe_allow_html=True)
progress_bar.progress(10)

with st.spinner("⚡ Running CP-SAT solver..."):
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
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Solver error: {e}")
        import traceback
        with st.expander("🔍 View Error Details"):
            st.code(traceback.format_exc())
        st.stop()

progress_bar.progress(100)

# ----------------------------------------
# 8. CHECK SOLVER STATUS
# ----------------------------------------
st.subheader("📋 Solver Status")
status = solver_result['status']

if status == 'OPTIMAL':
    status_text.markdown('<div class="success-box">✅ Optimization completed optimally!</div>', unsafe_allow_html=True)
    st.success(f"✅ Status: **{status}** (Optimal solution found)")
elif status == 'FEASIBLE':
    status_text.markdown('<div class="success-box">✅ Optimization completed with feasible solution!</div>', unsafe_allow_html=True)
    st.info(f"ℹ️ Status: **{status}** (Feasible solution found, may not be optimal)")
else:
    status_text.markdown('<div class="info-box">⚠️ Optimization ended without proven optimal solution.</div>', unsafe_allow_html=True)
    st.warning(f"⚠️ Status: **{status}**")

if solver_result["best"] is None:
    st.error("❌ Solver could not find a feasible solution.")
    st.info("""
    **Common issues that cause infeasibility:**
    - Demand is too high compared to production capacity
    - Minimum run days are too long for the available production days
    - Minimum closing inventory requirements are too high
    - Shutdown periods conflict with mandatory production requirements
    - Transition rules are too restrictive
    - Force start dates conflict with other constraints
    
    **Suggestions:**
    - Reduce minimum run days requirements
    - Lower minimum closing inventory targets  
    - Increase production capacity
    - Reduce demand forecasts
    - Adjust shutdown periods
    - Review force start date constraints
    """)
    footer()
    st.stop()

# ----------------------------------------
# 9. DISPLAY KEY METRICS
# ----------------------------------------
st.markdown("---")
st.markdown("### 📈 Key Metrics")

best_sol = solver_result['best']
objective = best_sol.get('objective', 0)

# Calculate total stockouts
total_stockouts = sum(best_sol.get('unmet', {}).values())

# Calculate transitions (count changes in assignment)
transitions = 0
for line in instance['lines']:
    prev_grade = None
    for d in range(instance['num_days']):
        curr_grade = best_sol.get('assign', {}).get((line, d))
        if curr_grade and prev_grade and curr_grade != prev_grade:
            transitions += 1
        if curr_grade:
            prev_grade = curr_grade

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Objective Value</div>
            <div class="metric-value">{objective:,.0f}</div>
            <div style="font-size: 0.75rem; opacity: 0.8; margin-top: 0.25rem;">↓ Lower is Better</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Transitions</div>
            <div class="metric-value">{transitions}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Stockouts</div>
            <div class="metric-value">{total_stockouts:,.0f} MT</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Planning Horizon</div>
            <div class="metric-value">{instance['num_days']} days</div>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------------------
# 10. CONVERT OUTPUT FOR VISUALIZATION
# ----------------------------------------
display_result = convert_solver_output_to_display(solver_result, instance)

# ----------------------------------------
# 11. PLOTLY VISUALS
# ----------------------------------------
st.markdown("---")
st.markdown('<div class="section-header">📊 Production & Inventory Visualizations</div>', unsafe_allow_html=True)

# Production Gantt + schedule tables
with st.expander("📅 Production Schedules", expanded=True):
    plot_production_visuals(
        display_result,
        instance,
        {"buffer_days": buffer_days}
    )

# Inventory charts per grade
st.markdown("---")
st.markdown('<div class="section-header">📦 Inventory Charts</div>', unsafe_allow_html=True)

with st.expander("📈 View Inventory Trends", expanded=True):
    plot_inventory_charts(
        display_result,
        instance,
        {"buffer_days": buffer_days}
    )

st.success("🎉 All visualizations rendered successfully!")

# ----------------------------------------
# 12. FOOTER
# ----------------------------------------
st.markdown("---")
footer()
