"""
 Polymer Production Scheduler - Main Application (Enhanced UX)
 A wizard-based Streamlit app for multi-plant production optimization
 Version 3.2.0 - Enhanced stage management and responsive design
"""
import streamlit as st
import io
from datetime import timedelta
from typing import Optional
import time

# OR-Tools import (used by solver module)
from ortools.sat.python import cp_model

# Import modules
from constants import *
from ui_components import *
from data_loader import *
from preview_tables import *
from solver_cp_sat import build_and_solve_model
from postprocessing import *
import pandas as pd


STAGE_MAP = {
    "UPLOAD": 0,
    "PREVIEW": 1,
    "OPTIMIZING": 2,
    "RESULTS": 3
}

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)
apply_custom_css()

# Session State Keys
SS_STAGE = 'app_stage'
SS_UPLOADED_FILE = 'uploaded_file'
SS_EXCEL_DATA = 'excel_data'
SS_VALIDATION_ERRORS = 'validation_errors'
SS_VALIDATION_WARNINGS = 'validation_warnings'
SS_SHUTDOWN_PERIODS = 'shutdown_periods'
SS_TRANSITION_RULES = 'transition_rules'
SS_SOLUTION = 'solution'
SS_GRADE_COLORS = 'grade_colors'
SS_OPTIMIZATION_PARAMS = 'optimization_params'
SS_THEME = 'app_theme'


# ========== STAGE 0: UPLOAD ==========
def render_upload_stage():
    """Renders the file upload stage."""
    render_header("1. Upload Data File")
    
    col_upload, col_template = st.columns([3, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload your **Polymer Production Template** Excel file.",
            type=ALLOWED_EXTENSIONS,
            key=SS_UPLOADED_FILE,
            help=f"File must be an .xlsx file, max {MAX_FILE_SIZE_MB}MB."
        )

    with col_template:
        render_download_template_button()

    if uploaded_file:
        loader = ExcelDataLoader(io.BytesIO(uploaded_file.read()))
        success, excel_data, errors, warnings = loader.load_and_validate()
        
        if success:
            # Process derived data for the solver
            shutdown_periods = process_shutdown_periods(excel_data['Plant'], excel_data['Demand'])
            
            # Filter transition sheets
            transition_dfs = {k: v for k, v in excel_data.items() if k.startswith(OPTIONAL_SHEET_PREFIX)}
            transition_rules = process_transition_rules(transition_dfs)

            # Store processed data in session state
            st.session_state[SS_EXCEL_DATA] = excel_data
            st.session_state[SS_VALIDATION_ERRORS] = errors
            st.session_state[SS_VALIDATION_WARNINGS] = warnings
            st.session_state[SS_SHUTDOWN_PERIODS] = shutdown_periods
            st.session_state[SS_TRANSITION_RULES] = transition_rules
            
            # Get grades list for color mapping
            grades = [col for col in excel_data['Demand'].columns if col != 'Date']
            st.session_state[SS_GRADE_COLORS] = build_grade_color_map(grades)

            st.success("File uploaded and validated successfully!")
            st.button("Continue to Data Preview →", on_click=lambda: st.session_state.update({SS_STAGE: STAGE_PREVIEW}), type="primary", use_container_width=True)
        else:
            st.error("Validation failed. Please correct the errors below.")
            render_validation_messages(errors, warnings)

# ========== STAGE 1: PREVIEW & CONFIGURE ==========
def render_preview_stage():
    """Renders data preview and optimization configuration."""
    render_header("2. Data Preview & Configuration")
    
    # 1. Validation Messages
    errors = st.session_state.get(SS_VALIDATION_ERRORS, [])
    warnings = st.session_state.get(SS_VALIDATION_WARNINGS, [])
    
    if errors:
        st.error("Cannot proceed. Please fix data validation errors.")
        render_validation_messages(errors, warnings)
        
    render_validation_messages(errors, warnings)
    
    excel_data = st.session_state[SS_EXCEL_DATA]
    
    # 2. Key Metrics
    render_key_metrics(excel_data)
    
    # 3. Optimization Parameters
    render_section_divider()
    with st.expander("⚙️ **Optimization Parameters**", expanded=True):
        params = st.session_state[SS_OPTIMIZATION_PARAMS]
        
        col_time, col_stockout, col_transition = st.columns(3)
        
        with col_time:
            params['time_limit_min'] = st.number_input(
                "Solver Time Limit (minutes)",
                min_value=1,
                max_value=60,
                value=params.get('time_limit_min', DEFAULT_TIME_LIMIT_MIN),
                step=1,
                help="Maximum time the solver can run to find a better solution."
            )
        
        with col_stockout:
            params['stockout_penalty'] = st.number_input(
                "Stockout Penalty Multiplier",
                min_value=1,
                max_value=1000,
                value=params.get('stockout_penalty', DEFAULT_STOCKOUT_PENALTY),
                step=1,
                help="Higher values heavily prioritize avoiding demand shortfalls."
            )

        with col_transition:
            params['transition_penalty'] = st.number_input(
                "Transition Penalty Multiplier",
                min_value=1,
                max_value=100,
                value=params.get('transition_penalty', DEFAULT_TRANSITION_PENALTY),
                step=1,
                help="Higher values prioritize longer production runs."
            )

        st.session_state[SS_OPTIMIZATION_PARAMS] = params
        
    # 4. Sheet Previews
    render_section_divider()
    st.markdown("### Data Sheets")
    
    # Render required sheets
    render_sheet_preview('Plant', excel_data['Plant'], icon="🏭")
    render_sheet_preview('Inventory', excel_data['Inventory'], icon="📦")
    render_sheet_preview('Demand', excel_data['Demand'], icon="📈")
    
    # Render transition sheets
    for key, df in excel_data.items():
        if key.startswith(OPTIONAL_SHEET_PREFIX):
            render_sheet_preview(key, df, icon="🔄")

    # 5. Navigation
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("← Back to Upload", use_container_width=True):
            st.session_state[SS_STAGE] = STAGE_UPLOAD
            st.rerun()
    with col_nav2:
        if not errors and st.button("Run Optimization →", use_container_width=True, type="primary"):
            st.session_state[SS_STAGE] = STAGE_OPTIMIZING
            st.session_state[SS_SOLUTION] = None # Reset previous solution
            st.rerun()

# ========== STAGE 2: OPTIMIZING ==========
def render_optimization_stage():
    """Runs the solver and shows progress."""
    render_header("3. Running Optimization")

    st.info("The Constraint Programming solver is running. This may take a few minutes depending on the time limit and problem complexity.")
    
    progress_bar = st.progress(0.0, text="Initializing solver...")
    status_text = st.empty()
    
    def progress_callback(progress: float, message: str):
        """Simple progress callback function."""
        progress_bar.progress(progress, text=message)
        status_text.markdown(f"**Status:** {message}")

    try:
        start_time = time.time()
        
        progress_callback(0.1, "Processing data for CP-SAT model...")
        
        # --- Data preparation for solver ---
        excel_data = st.session_state[SS_EXCEL_DATA]
        
        # --- CALL THE NEW SOLVER ---
        # The new solver signature is much cleaner and derives all necessary indices internally.
        solution = build_and_solve_model(
            df_plant=excel_data['Plant'],
            df_inventory=excel_data['Inventory'],
            df_demand=excel_data['Demand'],
            transition_rules=st.session_state[SS_TRANSITION_RULES],
            shutdown_periods=st.session_state[SS_SHUTDOWN_PERIODS],
            params=st.session_state[SS_OPTIMIZATION_PARAMS],
            # Removed redundant/incorrect arguments: grades, progress_callback
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time

        progress_callback(1.0, f"Optimization complete in {elapsed_time:.2f} seconds.")

        if solution is not None:
            st.session_state[SS_SOLUTION] = solution
            
            # Proceed to results stage
            st.success("🎉 Optimal or Feasible solution found!")
            st.button("View Results →", on_click=lambda: st.session_state.update({SS_STAGE: STAGE_RESULTS}), type="primary", use_container_width=True)
        else:
            st.error("❌ Solver failed to find a feasible solution within the time limit.")
            st.button("Review Configuration ←", on_click=lambda: st.session_state.update({SS_STAGE: STAGE_PREVIEW}), type="secondary", use_container_width=True)

    except Exception as e:
        progress_bar.progress(1.0)
        st.session_state[SS_SOLUTION] = None
        render_error_state("Optimization Error", f"An unexpected error occurred during solving: {e}")
        st.exception(e)
        st.button("Review Configuration ←", on_click=lambda: st.session_state.update({SS_STAGE: STAGE_PREVIEW}), type="secondary", use_container_width=True)


# ========== STAGE 3: RESULTS ==========
def render_results_stage():
    """Renders the final optimization results."""
    render_header("4. Optimization Results")
    
    solution = st.session_state.get(SS_SOLUTION)
    
    if solution is None:
        render_error_state("No Solution Found", "The solver did not return a valid solution. Please check the optimization log and constraints.")
        col_nav1, col_nav3 = st.columns([1, 1])
        with col_nav1:
            if st.button("← Back to Configuration", use_container_width=True):
                st.session_state[SS_STAGE] = STAGE_PREVIEW
                st.rerun()
        return

    excel_data = st.session_state[SS_EXCEL_DATA]
    grades = [col for col in excel_data['Demand'].columns if col != 'Date']
    dates = pd.to_datetime(excel_data['Demand']['Date']).dt.date.tolist()
    
    # 1. Summary Metrics
    df_summary = create_summary_table(solution, grades, dates, st.session_state[SS_EXCEL_DATA]['Plant'])
    render_summary_metrics(df_summary, solution['objective_value'])

    render_section_divider()

    # 2. Detailed Production Schedule
    st.markdown("### Production Schedule")
    col_gantt, col_table = st.columns([2, 1])
    
    with col_gantt:
        grade_colors = st.session_state[SS_GRADE_COLORS]
        fig_gantt = create_gantt_chart(solution['production_schedule'], grade_colors)
        st.plotly_chart(fig_gantt, use_container_width=True)
    
    with col_table:
        st.dataframe(solution['production_schedule'], use_container_width=True, hide_index=True)

    render_section_divider()

    # 3. Inventory vs. Demand
    st.markdown("### Inventory and Stockout Analysis")
    
    col_chart, col_details = st.columns([3, 1])
    
    with col_chart:
        fig_inventory = create_inventory_vs_demand_chart(
            solution['inventory'], 
            excel_data['Demand'], 
            st.session_state[SS_GRADE_COLORS]
        )
        st.plotly_chart(fig_inventory, use_container_width=True)
        
    with col_details:
        st.markdown("#### Stockout Details")
        stockout_df = create_stockout_details_table(solution, grades, dates)
        
        if stockout_df.empty:
            st.success("No stockouts detected in the optimal plan. Excellent!")
        else:
            try:
                # Use st.data_editor if available for better display
                st.data_editor(stockout_df, use_container_width=True, hide_index=True)
            except Exception as e:
                # Fallback to st.dataframe
                st.dataframe(stockout_df, use_container_width=True, hide_index=True)
            
        render_section_divider()

    # Navigation - Enhanced button layout (unchanged logic)
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    with col_nav1:
        if st.button("← Back to Configuration", use_container_width=True):
            st.session_state[SS_STAGE] = STAGE_PREVIEW
            st.rerun()
    with col_nav3:
        if st.button("🔄 New Optimization", use_container_width=True, type="primary"):
            # Reset state but keep theme
            theme_val = st.session_state.get(SS_THEME, "light")
            st.session_state.clear()
            st.session_state[SS_THEME] = theme_val
            st.session_state[SS_STAGE] = STAGE_UPLOAD
            st.rerun()


# ========== MAIN APP ==========
def main():
    """Main application controller"""
    current_stage = st.session_state.get(SS_STAGE, STAGE_UPLOAD)

    if current_stage == STAGE_UPLOAD:
        render_upload_stage()
    elif current_stage == STAGE_PREVIEW:
        render_preview_stage()
    elif current_stage == STAGE_OPTIMIZING:
        render_optimization_stage()
    elif current_stage == STAGE_RESULTS:
        render_results_stage()
    else:
        st.session_state[SS_STAGE] = STAGE_UPLOAD
        st.rerun()

if __name__ == "__main__":
    main()
