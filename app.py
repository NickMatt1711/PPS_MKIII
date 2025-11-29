"""
Polymer Production Scheduler - Main Application (refactored)
A wizard-based Streamlit app for multi-plant production optimization
"""

import streamlit as st
import io
from datetime import timedelta
from typing import Optional

# OR-Tools import (used by solver module)
from ortools.sat.python import cp_model

# Import modules (expect these to be present in the repo)
from constants import *
from ui_components import *
from data_loader import *
from preview_tables import *
from solver_cp_sat import build_and_solve_model
from postprocessing import *  # uses compatibility wrapper get_or_create_grade_colors

import pandas as pd


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_custom_css()

# Initialize required session state keys (safe defaults)
st.session_state.setdefault(SS_STAGE, 0)
st.session_state.setdefault(SS_UPLOADED_FILE, None)
st.session_state.setdefault(SS_EXCEL_DATA, None)
st.session_state.setdefault(SS_SOLUTION, None)
st.session_state.setdefault(SS_GRADE_COLORS, {})

st.session_state.setdefault(SS_OPTIMIZATION_PARAMS, {
    'time_limit_min': DEFAULT_TIME_LIMIT_MIN,
    'buffer_days': DEFAULT_BUFFER_DAYS,
    'stockout_penalty': DEFAULT_STOCKOUT_PENALTY,
    'transition_penalty': DEFAULT_TRANSITION_PENALTY,
    'continuity_bonus': DEFAULT_CONTINUITY_BONUS,
})


# ========== STAGE 0: UPLOAD ==========
def render_upload_stage():
    """Stage 0: File upload"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Multi-Plant Optimization with Shutdown Management")
    render_stage_progress(st.session_state.get(SS_STAGE, 0))  # Render progress based on current stage

    st.markdown("### 📤 Upload Production Data")
    st.markdown("Upload an Excel file containing your production planning data.")
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=ALLOWED_EXTENSIONS,
            help="Upload an Excel file with Plant, Inventory, and Demand sheets"
        )

        if uploaded_file is not None:
            # store raw uploaded file
            st.session_state[SS_UPLOADED_FILE] = uploaded_file
            render_alert("File uploaded successfully! Processing...", "success")

            # read file into buffer and load
            try:
                file_buffer = io.BytesIO(uploaded_file.read())
                loader = ExcelDataLoader(file_buffer)
                success, data, errors, warnings = loader.load_and_validate()

                if success:
                    st.session_state[SS_EXCEL_DATA] = data
                    st.session_state[SS_STAGE] = 1  # Move to preview stage
                    st.success("File validated. Proceeding to preview.")
                    st.rerun()
                else:
                    for err in errors:
                        render_alert(err, "error")
            except Exception as e:
                render_alert(f"Failed to read uploaded file: {e}", "error")

    with col2:
        st.markdown("#### 📥 Template")
        render_download_template_button()

    # Navigation buttons
    if st.button("Next: Preview Data →", disabled=(st.session_state[SS_UPLOADED_FILE] is None), use_container_width="True"):
        if st.session_state[SS_EXCEL_DATA] is not None:
            st.session_state[SS_STAGE] = 1  # Move to preview stage
        else:
            render_alert("Please upload and validate a file first.", "warning")
        st.rerun()


# ========== STAGE 1: PREVIEW & CONFIGURE ==========
def render_preview_stage():
    """Stage 1: Preview data and configure parameters"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Review data and configure optimization")
    render_stage_progress(st.session_state.get(SS_STAGE, 1))  # Render progress based on current stage

    excel_data = st.session_state.get(SS_EXCEL_DATA)
    if not excel_data:
        render_alert("No data found. Please upload a file first.", "error")
        if st.button("← Back to Upload"):
            st.session_state[SS_STAGE] = 0
            st.rerun()
        return

    st.markdown("### 📊 Data Preview")
    # Data preview logic...

    render_section_divider()

    # Configuration parameters
    st.markdown("### ⚙️ Optimization Parameters")
    # Optimization parameter configuration...

    # After preview and configuration, go to Optimization stage (Stage 1.5)
    if st.button("🎯 Run Optimization"):
        st.session_state[SS_STAGE] = 1.5  # Intermediate stage: Optimization In Progress
        st.rerun()


# ========== STAGE 1.5: OPTIMIZATION IN PROGRESS ==========
def render_optimization_stage():
    """Stage 1.5: Show optimization in progress with animation"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Optimization in Progress")
    render_stage_progress(st.session_state.get(SS_STAGE, 1.5))  # Render progress based on current stage

    st.markdown("""
        <div class="optimization-container">
            <div class="spinner"></div>
            <div class="optimization-text">⚡ Optimizing Production Schedule...</div>
            <div class="optimization-subtext">Running solver — progress will be shown below.</div>
        </div>
    """, unsafe_allow_html=True)

    excel_data = st.session_state.get(SS_EXCEL_DATA)
    if not excel_data:
        render_alert("No uploaded data found. Please upload file.", "error")
        if st.button("← Back to Upload"):
            st.session_state[SS_STAGE] = 0
            st.rerun()
        return

    params = st.session_state[SS_OPTIMIZATION_PARAMS]
    progress_bar = st.progress(0.0)
    status_text = st.empty()

    try:
        status_text.info("🔄 Processing plant data...")
        plant_data = process_plant_data(excel_data['Plant'])
        progress_bar.progress(0.1)

        status_text.info("🔄 Processing inventory data...")
        inventory_data = process_inventory_data(excel_data['Inventory'], plant_data['lines'])
        progress_bar.progress(0.2)

        status_text.info("🔄 Processing demand data...")
        demand_data, dates, num_days = process_demand_data(excel_data['Demand'], params['buffer_days'])
        # also keep formatted dates as strings for the solver if needed
        formatted_dates = [d.strftime('%d-%b-%y') for d in dates]
        progress_bar.progress(0.3)

        status_text.info("🔄 Processing shutdown periods...")
        shutdown_periods = process_shutdown_dates(plant_data.get('shutdown_periods', {}), dates)
        progress_bar.progress(0.35)

        status_text.info("🔄 Processing transition rules...")
        transition_dfs = {k: v for k, v in excel_data.items() if k.startswith('Transition_')}
        transition_rules = process_transition_rules(transition_dfs)
        progress_bar.progress(0.4)

        status_text.info("⚡ Running optimization (solver)...")

        # progress callback for solver to update UI
        def progress_callback(pct: float, msg: str):
            try:
                progress_bar.progress(0.4 + float(pct) * 0.6)
                status_text.info(f"⚡ {msg}")
            except Exception:
                # ignore UI update errors from callback
                pass

        # Run solver (replace this with your actual solver logic)
        status, solution_callback, solver = build_and_solve_model(
            grades=inventory_data['grades'],
            lines=plant_data['lines'],
            dates=dates,
            formatted_dates=formatted_dates,
            num_days=num_days,
            capacities=plant_data['capacities'],
            initial_inventory=inventory_data['initial_inventory'],
            min_inventory=inventory_data['min_inventory'],
            max_inventory=inventory_data['max_inventory'],
            min_closing_inventory=inventory_data['min_closing_inventory'],
            demand_data=demand_data,
            allowed_lines=inventory_data['allowed_lines'],
            min_run_days=inventory_data['min_run_days'],
            max_run_days=inventory_data['max_run_days'],
            force_start_date=inventory_data.get('force_start_date', {}),
            rerun_allowed=inventory_data.get('rerun_allowed', {}),
            material_running_info=plant_data.get('material_running', {}),
            shutdown_periods=shutdown_periods,
            transition_rules=transition_rules,
            buffer_days=params['buffer_days'],
            stockout_penalty=params['stockout_penalty'],
            transition_penalty=params['transition_penalty'],
            continuity_bonus=params['continuity_bonus'],
            time_limit_min=params['time_limit_min'],
            progress_callback=progress_callback
        )

        # mark 100% progress
        progress_bar.progress(1.0)

        # Check if solver provided a solution object/ callback object: be defensive
        num_found = 0
        try:
            num_found = int(solution_callback.num_solutions()) if hasattr(solution_callback, 'num_solutions') else 0
        except Exception:
            try:
                num_found = len(getattr(solution_callback, 'solutions', []))
            except Exception:
                num_found = 0

        if num_found > 0:
            status_text.success("✅ Optimization completed successfully!")
            # Extract the latest solution (defensive)
            last_solution = None
            try:
                last_solution = solution_callback.solutions[-1]
            except Exception:
                # maybe solution_callback itself is a dict-like result
                last_solution = solution_callback if isinstance(solution_callback, dict) else {}

            # Compose solution payload stored in session
            st.session_state[SS_SOLUTION] = {
                'status': status,
                'solution': last_solution,
                'solver': solver,
                'solve_time': getattr(last_solution, 'get', lambda k, d=None: d)('time', 0) if isinstance(last_solution, dict) else 0,
                'production_vars': getattr(solution_callback, 'production', {}) if hasattr(solution_callback, 'production') else {},
                'data': {
                    'grades': inventory_data['grades'],
                    'lines': plant_data['lines'],
                    'dates': dates,
                    'num_days': num_days,
                    'buffer_days': params['buffer_days'],
                    'shutdown_periods': shutdown_periods,
                    'allowed_lines': inventory_data['allowed_lines'],
                    'min_inventory': inventory_data['min_inventory'],
                    'max_inventory': inventory_data['max_inventory'],
                    'initial_inventory': inventory_data['initial_inventory'],
                }
            }

            st.session_state[SS_STAGE] = 2
            st.success("Optimization complete! Redirecting to results...")
            st.rerun()
        else:
            status_text.error("❌ No feasible solution found.")
            render_alert("No feasible solution found. Please check your constraints.", "error")

    except Exception as e:
        status_text.error("❌ Optimization failed.")
        render_alert(f"Error during optimization: {str(e)}", "error")
        # show exception stacktrace in debug mode
        st.exception(e)


# ========== STAGE 2: RESULTS ==========
def render_results_stage():
    """Stage 2: Display results"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Optimization Results")
    render_stage_progress(st.session_state.get(SS_STAGE, 2))  # Render progress based on current stage

    solution_data = st.session_state.get(SS_SOLUTION)
    if not solution_data:
        render_alert("No solution available. Please run an optimization first.", "error")
        if st.button("← Back to Configuration"):
            st.session_state[SS_STAGE] = 1
            st.rerun()
        return

    solution = solution_data.get('solution', {}) or {}
    data = solution_data.get('data', {})
    solve_time = solution_data.get('solve_time', 0)

    # Grade colors (compatibility wrapper available in postprocessing)
    grade_colors = get_or_create_grade_colors(data.get('grades', []))

    # KPIs
    st.markdown("### 📊 Key Performance Metrics")
    c1, c2, c3, c4 = st.columns(4)

    objective_val = solution.get('objective', 0) if isinstance(solution, dict) else 0
    transitions_total = solution.get('transitions', {}).get('total', 0) if isinstance(solution, dict) else 0

    # compute stockouts safely
    total_stockouts = 0
    try:
        for g in data.get('grades', []):
            total_stockouts += sum(solution.get('stockout', {}).get(g, {}).values())
    except Exception:
        total_stockouts = 0

    render_metric_card("Objective Value", f"{objective_val:,.0f}", c1)
    render_metric_card("Total Transitions", str(transitions_total), c2)
    render_metric_card("Total Stockouts", f"{total_stockouts:,.0f} MT", c3)
    render_metric_card("Time Elapsed", f"{solve_time:.1f}s", c4)

    render_section_divider()

    # Results tabs
    tab1, tab2, tab3 = st.tabs(["📅 Production Schedule", "📦 Inventory Analysis", "📊 Summary Tables"])

    # --- Production Schedule tab ---
    with tab1:
        st.markdown("### 📅 Production Schedule")

        for line in data.get('lines', []):
            st.markdown(f"#### 🏭 {line}")

            # Gantt chart (may return None)
            try:
                fig = create_gantt_chart(solution, line, data.get('dates', []), data.get('shutdown_periods', {}), grade_colors)
            except Exception as e:
                fig = None
                st.error(f"Failed to build gantt chart for {line}: {e}")

            if fig:
                st.plotly_chart(fig)

    # --- Inventory Analysis tab ---
    with tab2:
        st.markdown("### 📦 Inventory Analysis")
        # Show inventory analysis summary
        # You can display this as graphs or tables depending on your needs.

    # --- Summary Tables tab ---
    with tab3:
        st.markdown("### 📊 Summary Tables")
        st.write(solution)


# ========== MAIN APP ==========
def main():
    """Main application controller"""
    current_stage = st.session_state.get(SS_STAGE, 0)

    if current_stage == 0:
        render_upload_stage()
    elif current_stage == 1:
        render_preview_stage()
    elif current_stage == 1.5:
        render_optimization_stage()
    elif current_stage == 2:
        render_results_stage()
    else:
        render_alert("Unknown application stage. Resetting to start.", "warning")
        st.session_state[SS_STAGE] = 0
        st.rerun()


if __name__ == "__main__":
    main()
