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

# Initialize theme state
if SS_THEME not in st.session_state:
    st.session_state[SS_THEME] = "light"

# Apply custom CSS with theme
is_dark = st.session_state[SS_THEME] == "dark"
apply_custom_css(is_dark_mode=is_dark)

# Render theme toggle
render_theme_toggle()

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
    render_stage_progress(0)

    st.markdown("### 📤 Upload Production Data")
    st.markdown("Upload an Excel file containing your production planning data.")

    col1, col2 = st.columns([2, 1])

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
                    st.session_state[SS_STAGE] = 1
                    st.success("File validated. Proceeding to preview.")
                    st.rerun()
                else:
                    for err in errors:
                        render_alert(err, "error")
            except Exception as e:
                render_alert(f"Failed to read uploaded file: {e}", "error")

    with col2:
        st.markdown("#### 📋 Required Sheets")
        st.markdown(f"✓ Plant")
        st.markdown(f"✓ Inventory")
        st.markdown(f"✓ Demand")
        st.markdown(f"✓ Transition")

    # Navigation buttons
    if st.button("Next: Preview Data →", disabled=(st.session_state[SS_UPLOADED_FILE] is None),use_container_width="True"):
        # move forward only if a file is uploaded and validated already
        if st.session_state[SS_EXCEL_DATA] is not None:
            st.session_state[SS_STAGE] = 1
        else:
            render_alert("Please upload and validate a file first.", "warning")
        st.rerun()


# ========== STAGE 1: PREVIEW & CONFIGURE ==========
def render_preview_stage():
    """Stage 1: Preview data and configure parameters"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Review data and configure optimization")
    render_stage_progress(1)

    excel_data = st.session_state.get(SS_EXCEL_DATA)
    if not excel_data:
        render_alert("No data found. Please upload a file first.", "error")
        if st.button("← Back to Upload"):
            st.session_state[SS_STAGE] = 0
            st.rerun()
        return

    st.markdown("### 📊 Data Preview")

    # required sheets and transition detection
    required_sheets = ['Plant', 'Inventory', 'Demand']
    transition_sheets = [k for k in excel_data.keys() if k.startswith('Transition_')]

    # create tabs for required sheets + transition
    all_sheets = required_sheets + (['Transition Matrices'] if transition_sheets else [])
    tabs = st.tabs(all_sheets)

    # Render each required sheet
    for idx, sheet_name in enumerate(required_sheets):
        with tabs[idx]:
            if sheet_name in excel_data:
                df_display = excel_data[sheet_name].copy()

                # basic date formatting heuristics
                try:
                    if sheet_name == 'Plant':
                        # attempt to format the first few datetime columns
                        for col in df_display.select_dtypes(include=['datetime']).columns[:2]:
                            df_display[col] = df_display[col].dt.strftime('%d-%b-%y')
                    elif sheet_name == 'Inventory':
                        for col in df_display.select_dtypes(include=['datetime']).columns[:2]:
                            df_display[col] = df_display[col].dt.strftime('%d-%b-%y')
                    elif sheet_name == 'Demand':
                        for col in df_display.select_dtypes(include=['datetime']).columns[:1]:
                            df_display[col] = df_display[col].dt.strftime('%d-%b-%y')
                except Exception:
                    # skip formatting if any issue
                    pass

                st.dataframe(df_display, use_container_width=True)
            else:
                st.info(f"Sheet {sheet_name} not found in uploaded file.")

    # Render transition matrices in last tab if present
    if transition_sheets:
        with tabs[-1]:
            for sheet_name in transition_sheets:
                st.markdown(f"**{sheet_name}**")
                df_display = excel_data[sheet_name].copy()

                # Style transition matrix: highlight yes/no
                def highlight_transitions(val):
                    if pd.notna(val):
                        val_str = str(val).strip().lower()
                        if val_str == 'yes':
                            return 'background-color: #C6EFCE; color: #006100; font-weight: bold;'
                        elif val_str == 'no':
                            return 'background-color: #FFC7CE; color: #9C0006; font-weight: bold;'
                    return ''

                try:
                    styled_df = df_display.style.applymap(highlight_transitions)
                    st.dataframe(styled_df, use_container_width=True)
                except Exception:
                    st.dataframe(df_display, use_container_width=True)

                st.markdown("---")

    render_section_divider()

    # Configuration parameters
    st.markdown("### ⚙️ Optimization Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⏱️ Solver Configuration")
        time_limit = st.number_input(
            "Time limit (minutes)",
            min_value=1,
            max_value=120,
            value=int(st.session_state[SS_OPTIMIZATION_PARAMS]['time_limit_min']),
            step=1
        )
        
        buffer_days = st.number_input(
            "Buffer days",
            min_value=0,
            max_value=7,
            value=int(st.session_state[SS_OPTIMIZATION_PARAMS]['buffer_days']),
            step=1
        )
    
    with col2:
        st.markdown("#### 🎯 Objective Weights")
        stockout_penalty = st.number_input(
            "Stockout penalty",
            min_value=1,
            value=int(st.session_state[SS_OPTIMIZATION_PARAMS]['stockout_penalty']),
            step=1
        )
        
        transition_penalty = st.number_input(
            "Transition penalty",
            min_value=1,
            value=int(st.session_state[SS_OPTIMIZATION_PARAMS]['transition_penalty']),
            step=1
        )
        
        continuity_bonus = st.number_input(
            "Continuity bonus",
            min_value=0,
            value=int(st.session_state[SS_OPTIMIZATION_PARAMS]['continuity_bonus']),
            step=1
        )


    # persist parameters
    st.session_state[SS_OPTIMIZATION_PARAMS] = {
        'time_limit_min': int(time_limit),
        'buffer_days': int(buffer_days),
        'stockout_penalty': float(stockout_penalty),
        'transition_penalty': float(transition_penalty),
        'continuity_bonus': float(continuity_bonus),
    }

    render_section_divider()

    # Navigation buttons
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("← Back to Upload"):
            st.session_state[SS_STAGE] = 0
            st.rerun()

    with c3:
        if st.button("🎯 Run Optimization"):
            st.session_state[SS_STAGE] = 1.5
            st.rerun()


# ========== STAGE 1.5: OPTIMIZATION IN PROGRESS ==========
def render_optimization_stage():
    """Stage 1.5: Show optimization in progress with animation"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Optimization in Progress")
    render_stage_progress(1)

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

        # run solver
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
    render_stage_progress(2)

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

            if fig is None:
                st.info(f"No production timeline available for {line}.")
            else:
                st.plotly_chart(fig, use_container_width=True)

            # schedule table
            try:
                schedule_df = create_schedule_table(solution, line, data.get('dates', []), grade_colors)
            except Exception as e:
                schedule_df = pd.DataFrame()
                st.error(f"Failed to build schedule table for {line}: {e}")

            if not schedule_df.empty:
                def style_grade_column(val):
                    if val in grade_colors:
                        return f'background-color: {grade_colors[val]}; color: white; font-weight: bold; text-align: center;'
                    return ''

                try:
                    styled_df = schedule_df.style.applymap(lambda v: style_grade_column(v), subset=['Grade'])
                    st.dataframe(styled_df, use_container_width=True)
                except Exception:
                    st.dataframe(schedule_df, use_container_width=True)

            render_section_divider()

    # --- Inventory Analysis tab ---
    with tab2:
        st.markdown("### 📦 Inventory Analysis")

        for grade in sorted(data.get('grades', [])):
            st.markdown(f"#### {grade}")

            # allowed_lines may be dict or list; pass through as-is (postprocessing handles both)
            allowed_lines = data.get('allowed_lines', {})
            try:
                fig = create_inventory_chart(
                    solution,
                    grade,
                    data.get('dates', []),
                    data.get('min_inventory', {}).get(grade),
                    data.get('max_inventory', {}).get(grade),
                    allowed_lines,
                    data.get('shutdown_periods', {}),
                    grade_colors,
                    data.get('initial_inventory', {}).get(grade, 0),
                    data.get('buffer_days', 0)
                )
            except Exception as e:
                fig = None
                st.error(f"Failed to build inventory chart for {grade}: {e}")

            if fig is None:
                st.info(f"No inventory chart available for {grade}.")
            else:
                st.plotly_chart(fig, use_container_width=True)

            render_section_divider()

    # --- Summary tab ---
    with tab3:
        st.markdown("### 📊 Production Summary")

        try:
            summary_df = create_production_summary(
                solution,
                solution_data.get('production_vars', {}),
                solution_data.get('solver'),
                data.get('grades', []),
                data.get('lines', []),
                data.get('num_days', 0)
            )
        except Exception as e:
            summary_df = pd.DataFrame()
            st.error(f"Failed to create production summary: {e}")

        if not summary_df.empty:
            def style_summary_grade(val):
                if val in grade_colors and val != 'Total':
                    return f'background-color: {grade_colors[val]}; color: white; font-weight: bold; text-align: center;'
                if val == 'Total':
                    return 'background-color: #909399; color: white; font-weight: bold; text-align: center;'
                return ''

            try:
                styled_summary = summary_df.style.applymap(lambda v: style_summary_grade(v), subset=['Grade'])
                st.dataframe(styled_summary, use_container_width=True)
            except Exception:
                st.dataframe(summary_df, use_container_width=True)
        else:
            st.info("No production summary available.")

        st.markdown("### 🔄 Transitions by Line")
        try:
            transitions = solution.get('transitions', {}).get('per_line', {}) if isinstance(solution, dict) else {}
            transitions_data = [{'Line': l, 'Transitions': c} for l, c in transitions.items()]
            transitions_df = pd.DataFrame(transitions_data)
            st.dataframe(transitions_df, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to render transitions table: {e}")

    render_section_divider()

    # Navigation
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("← Back to Configuration"):
            st.session_state[SS_STAGE] = 1
            st.rerun()

    with c2:
        if st.button("🔄 New Optimization"):
            # Reset state but keep theme
            theme_val = st.session_state.get(SS_THEME, "light")
            st.session_state.clear()
            st.session_state[SS_THEME] = theme_val
            st.rerun()


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
