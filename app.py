"""
 Polymer Production Scheduler - Main Application (Enhanced UX)
 A wizard-based Streamlit app for multi-plant production optimization
 Version 3.2.0 - Enhanced stage management and responsive design
"""
import streamlit as st
import io
from datetime import timedelta
from typing import Optional

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

# Initialize required session state keys
st.session_state.setdefault(SS_STAGE, STAGE_UPLOAD)
st.session_state.setdefault(SS_UPLOADED_FILE, None)
st.session_state.setdefault(SS_EXCEL_DATA, None)
st.session_state.setdefault(SS_SOLUTION, None)
st.session_state.setdefault(SS_GRADE_COLORS, {})
st.session_state.setdefault(SS_OPTIMIZATION_PARAMS, {
    'time_limit_min': DEFAULT_TIME_LIMIT_MIN,
    'buffer_days': DEFAULT_BUFFER_DAYS,
    'stockout_penalty': DEFAULT_STOCKOUT_PENALTY,
    'transition_penalty': DEFAULT_TRANSITION_PENALTY,
})


# ========== STAGE 0: UPLOAD ==========
def render_upload_stage():
    """Stage 0: Enhanced file upload with clean layout (desktop-optimized)"""
    
    # Header and stage progress
    render_header(f"{APP_ICON} {APP_TITLE}", "Multi-Plant Optimization with Shutdown Management")
    render_stage_progress(STAGE_MAP.get(STAGE_UPLOAD, 0))

    # Two-column layout: Upload section (wider) + Quick Start Card (narrower)
    col1, col2 = st.columns([2, 1])

    # ========== LEFT COLUMN: Upload Section (No Card) ==========
    with col1:
        # Section title
        st.markdown('<div class="upload-section-title">📤 Upload Production Data</div>', unsafe_allow_html=True)
        
        # Uploader container
        st.markdown('<div class="uploader-container">', unsafe_allow_html=True)
        
        # Visual upload indicator
        st.markdown("""
        <div class="upload-indicator">
            <div class="upload-icon">📁</div>
            <div class="upload-text">Drag & Drop Excel File</div>
            <div class="upload-subtext">or click to browse</div>
            <div class="upload-specs">Limit: 200MB per file • Format: .XLSX</div>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload your input files here",
            type=ALLOWED_EXTENSIONS,
            help="Upload an Excel file with Plant, Inventory, Demand, and Transition sheets",
            label_visibility="collapsed"
        )

        # Processing logic
        if uploaded_file is not None:
            st.session_state[SS_UPLOADED_FILE] = uploaded_file
            render_alert("File uploaded successfully! Processing...", "success")

            try:
                file_buffer = io.BytesIO(uploaded_file.read())
                loader = ExcelDataLoader(file_buffer)
                success, data, errors, warnings = loader.load_and_validate()

                if success:
                    st.session_state[SS_EXCEL_DATA] = data
                    render_alert("File validated successfully!", "success")
                    for warn in warnings:
                        render_alert(warn, "warning")
                    st.session_state[SS_STAGE] = STAGE_PREVIEW
                    st.rerun()
                else:
                    for err in errors:
                        render_alert(err, "error")
                    for warn in warnings:
                        render_alert(warn, "warning")
            except Exception as e:
                render_error_state("Upload Failed", f"Failed to read uploaded file: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)  # close uploader-container

        # Download template section (in a subtle card)
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        st.markdown('<h3>📥 Don\'t have the template?</h3>', unsafe_allow_html=True)
        render_download_template_button()
        
        # Required sheets notice
        st.markdown("""
        <div class="required-sheets-notice" style="margin-top: 1rem; background: transparent; padding: 1rem 0; border: none;">
            <strong>⚠️ Required Sheets:</strong>
            <ul style="margin: 0.5rem 0 0 0; padding-left: 1.25rem; color: #856404;">
                <li>Plant</li>
                <li>Inventory</li>
                <li>Demand</li>
                <li>Transition_[PlantName]</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)  # close download-section

    # ========== RIGHT COLUMN: Quick Start Guide (In Card) ==========
    with col2:
        st.markdown('<div class="upload-card card-quickstart">', unsafe_allow_html=True)
        st.markdown('<h2>🚀 Quick Start Guide</h2>', unsafe_allow_html=True)
        st.markdown('<div class="upload-card-body">', unsafe_allow_html=True)
        
        # Clean step list without individual cards
        st.markdown("""
        <div class="quick-start-steps-clean">
            <div class="step-item-clean">
                <div class="step-number-clean">1</div>
                <div class="step-content-clean">
                    <strong>Download Template</strong>
                    <span>Get the pre-formatted Excel structure with all required sheets</span>
                </div>
            </div>
            <div class="step-divider-clean"></div>
            
            <div class="step-item-clean">
                <div class="step-number-clean">2</div>
                <div class="step-content-clean">
                    <strong>Fill Data</strong>
                    <span>Complete Plant, Inventory, Demand, and Transition sheets with your data</span>
                </div>
            </div>
            <div class="step-divider-clean"></div>
            
            <div class="step-item-clean">
                <div class="step-number-clean">3</div>
                <div class="step-content-clean">
                    <strong>Upload File</strong>
                    <span>Drag & drop or browse to upload your completed Excel file</span>
                </div>
            </div>
            <div class="step-divider-clean"></div>
            
            <div class="step-item-clean">
                <div class="step-number-clean">4</div>
                <div class="step-content-clean">
                    <strong>Configure & Run</strong>
                    <span>Set optimization parameters and generate your production schedule</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # close card-body
        st.markdown('</div>', unsafe_allow_html=True)  # close upload-card

    # ========== FULL-WIDTH: Variable & Constraint Details ==========
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    
    with st.expander("📄 Variable and Constraint Details", expanded=False):
        detail_tabs = st.tabs(["🏭 Plant Sheet", "📦 Inventory Sheet", "📈 Demand Sheet", "🔄 Transition Sheets"])
        
        with detail_tabs[0]:
            st.markdown("""
            ### Plant Sheet Configuration
            
            | Column | Description | Example |
            |--------|-------------|---------|
            | **Plant** | Plant identifier | Line_A |
            | **Capacity per day** | Maximum daily output (MT) | 500 |
            | **Material Running** | Currently producing grade | Grade_X |
            | **Expected Run Days** | Days before changeover | 3 |
            | **Shutdown Start Date** | Start of planned downtime | 15-Jan-25 |
            | **Shutdown End Date** | End of planned downtime | 17-Jan-25 |
            | **Pre-Shutdown Grade** | Grade before shutdown | Grade_A |
            | **Restart Grade** | Grade after shutdown | Grade_B |
            """)
        
        with detail_tabs[1]:
            st.markdown("""
            ### Inventory Sheet Configuration
            
            | Column | Description | Constraint Type |
            |--------|-------------|-----------------|
            | **Grade Name** | Product identifier | - |
            | **Opening Inventory** | Starting stock (MT) | Hard |
            | **Min. Inventory** | Safety stock level | Soft (penalty) |
            | **Max. Inventory** | Maximum storage capacity | Hard |
            | **Min. Closing Inventory** | End-period target | Soft (3x penalty) |
            | **Min. Run Days** | Minimum consecutive days | Hard |
            | **Max. Run Days** | Maximum consecutive days | Hard |
            | **Force Start Date** | Mandatory start date | Hard |
            | **Lines** | Plants where grade can run | Hard |
            | **Rerun Allowed** | Can repeat grade (Yes/No) | Hard |
            """)
        
        with detail_tabs[2]:
            st.markdown("""
            ### Demand Sheet Configuration
            
            | Column | Description |
            |--------|-------------|
            | **Date** | Planning horizon (daily) |
            | **Grade Columns** | Daily demand quantity (MT) for each grade |
            
            **Note:** Each grade should have its own column with daily demand values.
            """)
        
        with detail_tabs[3]:
            st.markdown("""
            ### Transition Sheets Configuration
            
            **Sheet Naming:** `Transition_[PlantName]`  
            **Example:** `Transition_Line_A`, `Transition_Line_B`
            
            **Matrix Structure:**
            - **Rows:** Previous grade (Grade running on day D)
            - **Columns:** Next grade (Grade to run on day D+1)
            - **Values:** `Yes` (allowed) or `No` (forbidden)
            
            | From → To | Grade_A | Grade_B | Grade_C |
            |-----------|---------|---------|---------|
            | **Grade_A** | Yes | Yes | No |
            | **Grade_B** | No | Yes | Yes |
            | **Grade_C** | Yes | No | Yes |
            
            **Constraint Type:** Hard (forbidden transitions are blocked)
            """)


# ========== STAGE 1: PREVIEW ==========
def render_preview_stage():
    """Stage 1: Preview data and configure parameters"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Review data and configure optimization")
    render_stage_progress(STAGE_MAP.get(STAGE_PREVIEW, 1))

    excel_data = st.session_state.get(SS_EXCEL_DATA)
    if not excel_data:
        render_alert("No data found. Please upload a file first.", "error")
        if st.button("← Back to Upload"):
            st.session_state[SS_STAGE] = STAGE_UPLOAD
            st.rerun()
        return

    st.markdown("### 📊 Data Preview")

    # Required sheets and transition detection
    required_sheets = ['Plant', 'Inventory', 'Demand']
    transition_sheets = [k for k in excel_data.keys() if k.startswith('Transition_')]

    # Create tabs for required sheets + transition
    all_sheets = required_sheets + (['Transition Matrices'] if transition_sheets else [])
    tabs = st.tabs(all_sheets)

    # Render each required sheet
    for idx, sheet_name in enumerate(required_sheets):
        with tabs[idx]:
            if sheet_name in excel_data:
                df_display = excel_data[sheet_name].copy()
                # Format datetime columns
                try:
                    if sheet_name == 'Plant':
                        for col in df_display.select_dtypes(include=['datetime']).columns[:2]:
                            df_display[col] = df_display[col].dt.strftime('%d-%b-%y')
                    elif sheet_name == 'Inventory':
                        for col in df_display.select_dtypes(include=['datetime']).columns[:2]:
                            df_display[col] = df_display[col].dt.strftime('%d-%b-%y')
                    elif sheet_name == 'Demand':
                        for col in df_display.select_dtypes(include=['datetime']).columns[:1]:
                            df_display[col] = df_display[col].dt.strftime('%d-%b-%y')
                except Exception:
                    pass
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info(f"Sheet {sheet_name} not found in uploaded file.")

    # Render transition matrices
    if transition_sheets:
        with tabs[-1]:
            for sheet_name in transition_sheets:
                st.markdown(f"**{sheet_name}**")
                df_display = excel_data[sheet_name].copy()

                # Style transition matrix
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
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                except Exception:
                    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("---")
    render_section_divider()

    # Configuration parameters (unchanged logic)
    st.markdown("### ⚙️ Optimization Parameters")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        time_limit = st.number_input(
            "Time limit (minutes)",
            min_value=1,
            max_value=120,
            value=int(st.session_state[SS_OPTIMIZATION_PARAMS]['time_limit_min']),
            step=1,
            help="Maximum time for solver to find optimal solution"
        )
    with col2:
        buffer_days = st.number_input(
            "Buffer days",
            min_value=0,
            max_value=7,
            value=int(st.session_state[SS_OPTIMIZATION_PARAMS]['buffer_days']),
            step=1,
            help="Additional days added to planning horizon for safety stock"
        )
    with col3:
        priority = st.select_slider(
            "Optimization Priority",
            options=[
                "Minimize Stockouts Only",
                "Favor Fewer Stockouts",
                "Balanced",
                "Favor Fewer Transitions",
                "Minimize Transitions Only"
            ],
            value="Balanced",
            help="Balance between avoiding stockouts vs. minimizing production changeovers"
        )

    # Map to penalty values (existing map retained)
    priority_map = {
        "Minimize Stockouts Only": (1000, 1),
        "Favor Stockouts": (10, 1),
        "Balanced": (10, 5),
        "Favor Fewer Transitions": (10, 8),
        "Minimize Transitions Only": (1, 1000)
    }
    stockout_penalty, transition_penalty = priority_map[priority]

    # Update parameters in session (unchanged)
    st.session_state[SS_OPTIMIZATION_PARAMS] = {
        'time_limit_min': int(time_limit),
        'buffer_days': int(buffer_days),
        'stockout_penalty': float(stockout_penalty),
        'transition_penalty': float(transition_penalty),
        'priority_label': priority  # Store user-friendly label
    }

    render_section_divider()

    # Navigation buttons (unchanged)
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    with col_nav1:
        if st.button("← Back to Upload", use_container_width=True):
            st.session_state[SS_STAGE] = STAGE_UPLOAD
            st.rerun()
    with col_nav3:
        if st.button("🎯 Run Optimization →", use_container_width=True, type="primary"):
            st.session_state[SS_STAGE] = STAGE_OPTIMIZING
            st.rerun()


# ========== STAGE 2: OPTIMIZATION IN PROGRESS ==========
def render_optimization_stage():
    """Stage 2: Show optimization in progress with animation"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Optimization in Progress")
    render_stage_progress(2)

    st.markdown("""
        <div class="optimization-container">
            <div class="spinner"></div>
            <div class="optimization-text">⚡ Optimizing Production Schedule...</div>
            <div class="optimization-subtext">Running solver — progress will be shown below.</div>
        </div>
    """, unsafe_allow_html=True)

    excel_data = st.session_state.get(SS_EXCEL_DATA)
    if not excel_data:
        render_error_state("No Data Found", "Please upload a file first.")
        if st.button("← Back to Upload"):
            st.session_state[SS_STAGE] = STAGE_UPLOAD
            st.rerun()
        return

    params = st.session_state[SS_OPTIMIZATION_PARAMS]
    progress_bar = st.progress(0.0)
    status_text = st.empty()

    try:
        status_text.info("📄 Processing plant data...")
        plant_data = process_plant_data(excel_data['Plant'])
        progress_bar.progress(0.1)

        status_text.info("📄 Processing inventory data...")
        inventory_data = process_inventory_data(excel_data['Inventory'], plant_data['lines'])
        progress_bar.progress(0.2)

        status_text.info("📄 Processing demand data...")
        demand_data, dates, num_days = process_demand_data(excel_data['Demand'], params['buffer_days'])
        formatted_dates = [d.strftime('%d-%b-%y') for d in dates]
        progress_bar.progress(0.3)

        status_text.info("📄 Validating shutdown constraints...")
        # Validate pre-shutdown and restart grades
        invalid_grades_warning = []
        for line, grade in plant_data.get('pre_shutdown_grades', {}).items():
            if grade not in inventory_data['grades']:
                invalid_grades_warning.append(f"Pre-shutdown grade '{grade}' for line '{line}' is not a valid grade.")
            elif line not in inventory_data['allowed_lines'][grade]:
                invalid_grades_warning.append(f"Pre-shutdown grade '{grade}' for line '{line}' is not allowed on that line.")
        for line, grade in plant_data.get('restart_grades', {}).items():
            if grade not in inventory_data['grades']:
                invalid_grades_warning.append(f"Restart grade '{grade}' for line '{line}' is not a valid grade.")
            elif line not in inventory_data['allowed_lines'][grade]:
                invalid_grades_warning.append(f"Restart grade '{grade}' for line '{line}' is not allowed on that line.")
        if invalid_grades_warning:
            for warning in invalid_grades_warning:
                render_alert(warning, "warning")
            st.warning("⚠️ Invalid shutdown/restart grades may cause infeasible solutions.")

        status_text.info("📄 Processing shutdown periods...")
        shutdown_periods = process_shutdown_dates(plant_data.get('shutdown_periods', {}), dates)
        progress_bar.progress(0.35)

        status_text.info("📄 Processing transition rules...")
        transition_dfs = {k: v for k, v in excel_data.items() if k.startswith('Transition_')}
        transition_rules = process_transition_rules(transition_dfs)
        progress_bar.progress(0.4)

        status_text.info("⚡ Running optimization solver...")

        # Progress callback for solver
        def progress_callback(pct: float, msg: str):
            try:
                progress_bar.progress(0.4 + float(pct) * 0.6)
                status_text.info(f"⚡ {msg}")
            except Exception:
                pass

        # Run solver (unchanged parameters/logic)
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
            pre_shutdown_grades=plant_data.get('pre_shutdown_grades', {}),
            # NEW restart grades already in original logic (left untouched)
            restart_grades=plant_data.get('restart_grades', {}),
            transition_rules=transition_rules,
            buffer_days=params['buffer_days'],
            stockout_penalty=params['stockout_penalty'],
            transition_penalty=params['transition_penalty'],
            time_limit_min=params['time_limit_min'],
            progress_callback=progress_callback
        )

        progress_bar.progress(1.0)

        # Check solution
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
            # Extract solution
            last_solution = None
            try:
                last_solution = solution_callback.solutions[-1]
            except Exception:
                last_solution = solution_callback if isinstance(solution_callback, dict) else {}

            # Store solution (unchanged structure)
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
                    'pre_shutdown_grades': plant_data.get('pre_shutdown_grades', {}),
                    'restart_grades': plant_data.get('restart_grades', {}),
                    'capacities': plant_data.get('capacities', {}),
                }
            }

            st.session_state[SS_STAGE] = STAGE_RESULTS
            st.success("Optimization complete! Redirecting to results...")
            st.rerun()
        else:
            status_text.error("❌ No feasible solution found.")
            render_error_state(
                "No Solution Found",
                "The solver could not find a feasible solution. Please check your constraints and try again."
            )
            # Provide navigation back
            if st.button("← Back to Configuration"):
                st.session_state[SS_STAGE] = STAGE_PREVIEW
                st.rerun()

    except Exception as e:
        status_text.error("❌ Optimization failed.")
        render_error_state("Optimization Error", f"An error occurred: {str(e)}")
        st.exception(e)
        # Navigation back
        if st.button("← Back to Configuration"):
            st.session_state[SS_STAGE] = STAGE_PREVIEW
            st.rerun()


# ========== STAGE 3: RESULTS ==========
def render_results_stage():
    """Stage 3: Display results"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Optimization Results")
    render_stage_progress(STAGE_MAP.get(STAGE_RESULTS, 3))

    solution_data = st.session_state.get(SS_SOLUTION)
    if not solution_data:
        render_error_state("No Solution Available", "Please run an optimization first.")
        if st.button("← Back to Configuration"):
            st.session_state[SS_STAGE] = STAGE_PREVIEW
            st.rerun()
        return

    solution = solution_data.get('solution', {}) or {}
    data = solution_data.get('data', {})
    solve_time = solution_data.get('solve_time', 0)

    # Grade colors
    grade_colors = get_or_create_grade_colors(data.get('grades', []))

    # KPIs - Responsive layout
    st.markdown("### 📊 Key Performance Metrics")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    objective_val = solution.get('objective', 0) if isinstance(solution, dict) else 0
    transitions_total = solution.get('transitions', {}).get('total', 0) if isinstance(solution, dict) else 0

    # Compute stockouts
    total_stockouts = 0
    try:
        for g in data.get('grades', []):
            total_stockouts += sum(solution.get('stockout', {}).get(g, {}).values())
    except Exception:
        total_stockouts = 0

    render_metric_card("Objective Value", f"{objective_val:,.0f}", col1, 0)
    render_metric_card("Total Transitions", str(transitions_total), col2, 1)
    render_metric_card("Total Stockouts", f"{total_stockouts:,.0f} MT", col3, 2)
    render_metric_card("Time Elapsed", f"{solve_time:.1f}s", col4, 3)

    render_section_divider()

    # Results tabs - Combined into Summary
    tab1, tab2, tab3 = st.tabs(["📅 Production Schedule", "📦 Inventory Analysis", "📊 Summary Tables"])

    # --- Production Schedule tab ---
    with tab1:
        st.markdown("### 📅 Production Schedule")
        for line in data.get('lines', []):
            st.markdown(f"#### 🏭 {line}")
            # Gantt chart
            try:
                fig = create_gantt_chart(
                    solution, line, data.get('dates', []),
                    data.get('shutdown_periods', {}),
                    grade_colors
                )
            except Exception as e:
                fig = None
                st.error(f"Failed to build gantt chart for {line}: {e}")

            if fig is None:
                st.info(f"No production timeline available for {line}.")
            else:
                st.plotly_chart(fig, use_container_width=True)

            # Schedule table
            try:
                schedule_df = create_schedule_table(
                    solution, 
                    line, 
                    data.get('dates', []), 
                    grade_colors,
                    shutdown_periods=data.get('shutdown_periods', {})  # ADD THIS
                )
            except Exception as e:
                schedule_df = pd.DataFrame()
                st.error(f"Failed to build schedule table for {line}: {e}")

            if not schedule_df.empty:
                def style_grade_column(val):
                    if val in grade_colors:
                        return f'background-color: {grade_colors[val]}; color: white; font-weight: bold; text-align: center;'
                    return ''
                try:
                    styled_df = schedule_df.style.applymap(
                        lambda v: style_grade_column(v), subset=['Grade']
                    )
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                except Exception:
                    st.dataframe(schedule_df, use_container_width=True, hide_index=True)

        render_section_divider()

    # --- Inventory Analysis tab ---
    with tab2:
        st.markdown("### 📦 Inventory Analysis")
        for grade in sorted(data.get('grades', [])):
            st.markdown(f"#### {grade}")
            allowed_lines = data.get('allowed_lines', {})
            try:
                fig = create_inventory_chart(
                    solution, grade, data.get('dates', []),
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
        col_summary1, col_summary2, col_summary3 = st.columns([2, 1, 1])

        with col_summary1:
            st.markdown("### 📊 Production Summary")
            try:
                summary_df = create_production_summary(
                    solution,
                    solution_data.get('production_vars', {}),
                    solution_data.get('solver'),
                    data.get('grades', []),
                    data.get('lines', []),
                    data.get('num_days', 0),
                    buffer_days=data.get('buffer_days', 0)
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
                    styled_summary = summary_df.style.applymap(
                        lambda v: style_summary_grade(v), subset=['Grade']
                    )
                    st.dataframe(styled_summary, use_container_width=True, hide_index=True)
                except Exception:
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
            else:
                st.info("No production summary available.")

        with col_summary2:
            st.markdown("### 🔄 Transitions by Line")
            try:
                transitions = solution.get('transitions', {}).get('per_line', {}) if isinstance(solution, dict) else {}
                transitions_data = [{'Line': l, 'Transitions': c} for l, c in transitions.items()]
                transitions_df = pd.DataFrame(transitions_data)
                st.dataframe(transitions_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Failed to render transitions table: {e}")

        with col_summary3:
            st.markdown("### ⚠️ Stockout Summary")
            try:
                stockout_df = create_stockout_details_table(
                    solution, data.get('grades', []), data.get('dates', []),
                    buffer_days=data.get('buffer_days', 0)
                )
            except Exception as e:
                stockout_df = pd.DataFrame()
                st.error(f"Failed to create stockout details table: {e}")

            if not stockout_df.empty:
                def style_summary_grade(val):
                       if val in grade_colors:
                           return f'background-color: {grade_colors[val]}; color: white; font-weight: bold; text-align: center;'
                       return ''
                try:
                    styled_stockout = stockout_df.style.applymap(
                        lambda v: style_summary_grade(v), subset=['Grade']
                    )
                    st.dataframe(styled_stockout, use_container_width=True, hide_index=True)
                except Exception as e:
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
        render_alert("Unknown application stage. Resetting to start.", "warning")
        st.session_state[SS_STAGE] = STAGE_UPLOAD
        st.rerun()


if __name__ == "__main__":
    main()
