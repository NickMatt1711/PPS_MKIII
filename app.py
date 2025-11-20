"""
Main Application Entry Point
=============================

Streamlit app following test(1).py UI style with Old Logic with Sidebar.py solver logic.
"""

import streamlit as st
import time
import io
import copy
from pathlib import Path

# Import all modules
import constants
import data_loader
import preview_tables
import ui_components
import solver_cp_sat
import postprocessing

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Polymer Production Scheduler",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Navigation
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: Upload, 2: Preview & Config, 3: Results

# The *original* clean instance loaded from Excel
if 'raw_instance' not in st.session_state:
    st.session_state.raw_instance = None

# Solver outputs
if 'solver_result' not in st.session_state:
    st.session_state.solver_result = None
if 'display_result' not in st.session_state:
    st.session_state.display_result = None

# Optimization parameters (persistent)
if 'optimization_params' not in st.session_state:
    st.session_state.optimization_params = {
        'buffer_days': 3,
        'time_limit_min': 10,
        'stockout_penalty': 10,
        'transition_penalty': 50,
    }

# Inject UI CSS
ui_components.inject_custom_css()

# ============================================================================
# HEADER
# ============================================================================

ui_components.render_header()

# ============================================================================
# STEP INDICATOR
# ============================================================================

step_status = [
    'active' if st.session_state.step == 1 else 'completed',
    'active' if st.session_state.step == 2 else ('completed' if st.session_state.step > 2 else ''),
    'active' if st.session_state.step == 3 else ''
]

# (existing step UI not shown here to save space — keep unchanged)
# --------------------------------------------------------------------

# ============================================================================
# STEP 1: UPLOAD DATA
# ============================================================================

if st.session_state.step == 1:

    col1, col2 = st.columns([4, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose Excel File",
            type=["xlsx"],
            help="Upload an Excel file with Plant, Inventory, and Demand sheets",
            label_visibility="collapsed"
        )
    
        if uploaded_file is not None:

            st.session_state.uploaded_file = uploaded_file

            # RESET ONLY solver artifacts — keep saved parameters
            st.session_state.raw_instance = None
            st.session_state.solver_result = None
            st.session_state.display_result = None

            st.success("✅ File uploaded successfully!")

            time.sleep(0.4)
            st.session_state.step = 2
            st.rerun()

    with col2:
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        if template_path.exists():
            with open(template_path, "rb") as f:
                st.download_button(
                    label="📥 Download Template",
                    data=f,
                    file_name="polymer_production_template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    # (Help cards remain unchanged)
    # --------------------------------------------------------------------

# ============================================================================
# STEP 2: PREVIEW & CONFIGURE
# ============================================================================

elif st.session_state.step == 2:
    try:

        # Load raw Excel instance if not loaded already
        if st.session_state.raw_instance is None:
            uploaded_file = st.session_state.uploaded_file
            uploaded_file.seek(0)

            with st.spinner("Loading and validating data..."):
                raw_instance = data_loader.load_excel_data(uploaded_file)
                st.session_state.raw_instance = raw_instance
                st.success("✅ Data loaded successfully!")

        raw_instance = st.session_state.raw_instance

        # === ALWAYS PREVIEW RAW (no buffer days) ===
        preview_tables.show_preview_tables(raw_instance)

        ui_components.render_divider()

        # =========================================================================
        # OPTIMIZATION PARAMETERS UI (RESTORED)
        # =========================================================================

        st.markdown("""
        <div class="material-card">
            <div class="card-title">⚙️ Optimization Parameters</div>
        </div>
        """, unsafe_allow_html=True)

        params = st.session_state.optimization_params

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Core Settings")
            params['time_limit_min'] = st.number_input(
                "⏱️ Time Limit (minutes)",
                min_value=1,
                max_value=120,
                value=params['time_limit_min'],
                help="Maximum solver runtime"
            )

            params['buffer_days'] = st.number_input(
                "📅 Planning Buffer (days)",
                min_value=0,
                max_value=7,
                value=params['buffer_days'],
                help="Additional empty buffer days for planning horizon"
            )

        with col2:
            st.markdown("#### Objective Weights")
            params['stockout_penalty'] = st.number_input(
                "🎯 Stockout Penalty",
                min_value=1,
                max_value=10000,
                value=params['stockout_penalty'],
                help="Penalty weight for inventory shortages"
            )

            params['transition_penalty'] = st.number_input(
                "🔄 Transition Penalty",
                min_value=1,
                max_value=10000,
                value=params['transition_penalty'],
                help="Penalty weight for grade transitions"
            )

        ui_components.render_divider()

        # =========================================================================
        # ACTION BUTTONS
        # =========================================================================

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("← Back to Upload", use_container_width=True):
                st.session_state.step = 1
                st.session_state.raw_instance = None
                st.rerun()

        with col2:
            if st.button("🚀 Run Optimization", type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        if st.button("← Back to Upload"):
            st.session_state.step = 1
            st.session_state.raw_instance = None
            st.rerun()

# ============================================================================
# STEP 3: OPTIMIZATION & RESULTS
# ============================================================================

elif st.session_state.step == 3:
    try:

        if st.session_state.solver_result is None:

            st.markdown("""
            <div class="material-card">
                <div class="card-title">⚡ Running Optimization</div>
            </div>
            """, unsafe_allow_html=True)

            progress = st.progress(0)
            status = st.empty()

            time.sleep(0.3)

            # Fresh copy of raw data
            raw_instance = st.session_state.raw_instance
            instance = copy.deepcopy(raw_instance)

            params = st.session_state.optimization_params

            status.markdown('<div class="alert-box info">📊 Preprocessing data...</div>', unsafe_allow_html=True)
            progress.progress(15)
            time.sleep(0.3)

            # Add buffer days ONLY ONCE to temporary copy
            instance = data_loader.add_buffer_days(instance, params['buffer_days'])

            status.markdown('<div class="alert-box info">🔧 Building optimization model...</div>', unsafe_allow_html=True)
            progress.progress(40)
            time.sleep(0.3)

            status.markdown('<div class="alert-box info">⚡ Running solver...</div>', unsafe_allow_html=True)
            progress.progress(65)

            solver_result = solver_cp_sat.solve(instance, params)
            st.session_state.solver_result = solver_result

            progress.progress(85)
            status.markdown('<div class="alert-box info">📈 Processing results...</div>', unsafe_allow_html=True)

            display_result = postprocessing.convert_solver_output_to_display(solver_result, instance)
            st.session_state.display_result = display_result

            progress.progress(100)
            time.sleep(0.3)
            status.empty()
            progress.empty()

        # ---------------------------- RESULTS DISPLAY ----------------------------
        solver_result = st.session_state.solver_result
        display_result = st.session_state.display_result
        raw_instance = st.session_state.raw_instance
        params = st.session_state.optimization_params

        ui_components.render_optimization_status(
            solver_result['status'],
            solver_result['runtime']
        )

        ui_components.render_divider()

        if display_result is None:
            st.markdown("""
            <div class="alert-box warning">
                <strong>❌ No Feasible Solution Found</strong><br>
                The optimizer could not identify a valid production schedule.
            </div>
            """, unsafe_allow_html=True)

            ui_components.render_troubleshooting_guide()

            if st.button("🔧 Adjust Parameters", use_container_width=True):
                st.session_state.step = 2
                st.session_state.solver_result = None
                st.session_state.display_result = None
                st.rerun()

        else:
            total_stockouts = sum(
                sum(display_result['stockout'].get(g, {}).values())
                for g in raw_instance['grades']
            )

            ui_components.render_summary_metrics(
                objective=display_result['objective'],
                transitions=display_result['transitions']['total'],
                stockouts=total_stockouts,
                planning_days=raw_instance['num_days']
            )

            ui_components.render_divider()

            tab1, tab2, tab3 = st.tabs(["📅 Production Schedule", "📊 Summary Analytics", "📦 Inventory Trends"])

            with tab1:
                postprocessing.plot_production_visuals(display_result, raw_instance, params)

            with tab2:
                postprocessing.render_production_summary(display_result, raw_instance)

            with tab3:
                postprocessing.plot_inventory_charts(display_result, raw_instance, params)

            ui_components.render_divider()

            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                if st.button("🔄 New Optimization", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state.raw_instance = None
                    st.session_state.solver_result = None
                    st.session_state.display_result = None
                    st.rerun()

            with col2:
                if st.button("🔧 Adjust Parameters", use_container_width=True):
                    st.session_state.step = 2
                    st.session_state.solver_result = None
                    st.session_state.display_result = None
                    st.rerun()

    except Exception as e:
        st.error(f"❌ Error During Optimization: {str(e)}")
        if st.button("← Return to Start"):
            st.session_state.step = 1
            st.session_state.raw_instance = None
            st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

ui_components.render_footer()
