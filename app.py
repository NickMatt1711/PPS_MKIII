"""
Polymer Production Scheduler - Main Application
================================================

A production-grade Streamlit application for multi-plant polymer production scheduling.
"""

import streamlit as st
import time
from pathlib import Path
import io

# Import PPS modules
try:
    from pps_mkiii.constants import (
        DEFAULT_TIME_LIMIT,
        DEFAULT_BUFFER_DAYS,
        DEFAULT_STOCKOUT_PENALTY,
        DEFAULT_TRANSITION_PENALTY,
        get_error_message,
        get_success_message
    )
    from pps_mkiii.data_loader import load_excel_data, add_buffer_days
    from pps_mkiii.preview_tables import show_data_preview_tabs, show_validation_summary
    from pps_mkiii.ui_components import (
        inject_custom_css,
        render_header,
        render_step_indicator,
        render_optimization_params_form,
        render_metric_card,
        render_divider,
        render_footer,
        render_alert
    )
    from pps_mkiii.solver_cp_sat import solve
    from pps_mkiii.postprocessing import (
        convert_solver_output_to_display,
        plot_production_visuals,
        plot_inventory_charts
    )
except ImportError:
    # Fallback for development
    st.error("Error importing PPS modules. Ensure package structure is correct.")
    st.stop()


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

if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: Upload, 2: Configure, 3: Results

if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'instance' not in st.session_state:
    st.session_state.instance = None

if 'optimization_params' not in st.session_state:
    st.session_state.optimization_params = {
        'buffer_days': DEFAULT_BUFFER_DAYS,
        'time_limit_min': DEFAULT_TIME_LIMIT,
        'stockout_penalty': DEFAULT_STOCKOUT_PENALTY,
        'transition_penalty': DEFAULT_TRANSITION_PENALTY
    }

if 'solver_result' not in st.session_state:
    st.session_state.solver_result = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sample_template():
    """Load sample template from same directory."""
    try:
        current_dir = Path(__file__).parent
        template_path = current_dir / "polymer_production_template.xlsx"
        
        if template_path.exists():
            with open(template_path, "rb") as f:
                return io.BytesIO(f.read())
        else:
            st.warning("Sample template not found.")
            return None
    except Exception as e:
        st.warning(f"Could not load template: {e}")
        return None


# ============================================================================
# UI RENDERING
# ============================================================================

# Inject custom CSS
inject_custom_css()

# Render header
render_header()

# Render step indicator
render_step_indicator(st.session_state.step)


# ============================================================================
# STEP 1: FILE UPLOAD
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
            st.success(get_success_message("file_uploaded"))
            time.sleep(0.5)
            
            # Load data
            try:
                with st.spinner("Loading data..."):
                    instance = load_excel_data(uploaded_file)
                    st.session_state.instance = instance
                    st.session_state.step = 2
                    st.rerun()
            except Exception as e:
                st.error(f"Error loading data: {e}")
                st.session_state.uploaded_file = None
    
    with col2:
        sample_workbook = get_sample_template()
        if sample_workbook:
            st.download_button(
                label="📥 Download Template",
                data=sample_workbook,
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    # Quick start guide
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="material-card">
            <div class="card-title">📋 Quick Start Guide</div>
            <div class="card-subtitle">Follow these simple steps to get started</div>
            <ol class="styled-list">
                <li>Download the Excel template</li>
                <li>Fill in your production data</li>
                <li>Upload your completed file</li>
                <li>Configure optimization parameters</li>
                <li>Run optimization and analyze results</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="material-card">
            <div class="card-title">✨ Key Capabilities</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                <div>
                    <div style="font-weight: 600; color: #667eea; margin-bottom: 0.5rem;">🏭 Multi-Plant</div>
                    <div style="font-size: 0.875rem; color: #757575;">Optimize across multiple production lines</div>
                </div>
                <div>
                    <div style="font-weight: 600; color: #667eea; margin-bottom: 0.5rem;">📦 Inventory Control</div>
                    <div style="font-size: 0.875rem; color: #757575;">Maintain optimal stock levels</div>
                </div>
                <div>
                    <div style="font-weight: 600; color: #667eea; margin-bottom: 0.5rem;">🔄 Transition Rules</div>
                    <div style="font-size: 0.875rem; color: #757575;">Grade changeover optimization</div>
                </div>
                <div>
                    <div style="font-weight: 600; color: #667eea; margin-bottom: 0.5rem;">🔧 Shutdown Handling</div>
                    <div style="font-size: 0.875rem; color: #757575;">Plan around maintenance periods</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# STEP 2: CONFIGURE & PREVIEW
# ============================================================================

elif st.session_state.step == 2:
    instance = st.session_state.instance
    
    if instance is None:
        st.error("No data loaded. Please upload a file.")
        if st.button("← Back to Upload"):
            st.session_state.step = 1
            st.rerun()
        st.stop()
    
    # Data preview tabs
    st.markdown("### 📊 Data Preview")
    show_data_preview_tabs(instance)
    
    render_divider()
    
    # Validation summary
    show_validation_summary(instance)
    
    render_divider()
    
    # Optimization parameters form
    params = render_optimization_params_form()
    
    # Update session state with parameters
    st.session_state.optimization_params.update(params)
    
    render_divider()
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Upload", use_container_width=True):
            st.session_state.step = 1
            st.session_state.instance = None
            st.rerun()
    
    with col2:
        if st.button("🚀 Run Optimization", type="primary", use_container_width=True):
            st.session_state.step = 3
            st.rerun()


# ============================================================================
# STEP 3: OPTIMIZATION & RESULTS
# ============================================================================

elif st.session_state.step == 3:
    instance = st.session_state.instance
    params = st.session_state.optimization_params
    
    if instance is None:
        st.error("No data loaded.")
        if st.button("← Back to Start"):
            st.session_state.step = 1
            st.rerun()
        st.stop()
    
    # Show optimization progress
    st.markdown("""
    <div class="material-card">
        <div class="card-title">⚡ Running Optimization</div>
    </div>
    """, unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    time.sleep(0.5)
    
    # Add buffer days to instance
    status_text.markdown(render_alert("📊 Preprocessing data...", "info"), unsafe_allow_html=True)
    progress_bar.progress(10)
    
    instance = add_buffer_days(instance, params['buffer_days'])
    
    time.sleep(0.5)
    progress_bar.progress(30)
    status_text.markdown(render_alert("🔧 Building optimization model...", "info"), unsafe_allow_html=True)
    
    time.sleep(0.5)
    progress_bar.progress(50)
    status_text.markdown(render_alert("⚡ Solving optimization problem...", "info"), unsafe_allow_html=True)
    
    # Run solver
    try:
        start_time = time.time()
        solver_result = solve(instance, params)
        solve_time = time.time() - start_time
        
        progress_bar.progress(100)
        
        # Check status
        if solver_result['status'] in ['OPTIMAL', 'FEASIBLE']:
            status_text.markdown(
                render_alert(get_success_message("optimal_solution" if solver_result['status'] == 'OPTIMAL' else "feasible_solution"), "success"),
                unsafe_allow_html=True
            )
            
            time.sleep(0.5)
            render_divider()
            
            # Extract display data
            display_result = convert_solver_output_to_display(solver_result, instance)
            
            # Performance metrics
            st.markdown("""
            <div class="material-card">
                <div class="card-title">📊 Optimization Results</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(
                    render_metric_card(
                        "Objective Value",
                        f"{display_result['objective']:,.0f}",
                        "Lower is Better",
                        "primary"
                    ),
                    unsafe_allow_html=True
                )
            
            with col2:
                transitions = display_result.get('transitions', {}).get('total', 0)
                st.markdown(
                    render_metric_card(
                        "Transitions",
                        str(transitions),
                        "Grade Changeovers",
                        "info"
                    ),
                    unsafe_allow_html=True
                )
            
            with col3:
                stockouts = sum(
                    sum(display_result['stockout'].get(g, {}).values())
                    for g in instance['grades']
                )
                st.markdown(
                    render_metric_card(
                        "Stockouts",
                        f"{stockouts:,.0f}",
                        "MT Unmet Demand",
                        "success" if stockouts == 0 else "warning"
                    ),
                    unsafe_allow_html=True
                )
            
            with col4:
                st.markdown(
                    render_metric_card(
                        "Solve Time",
                        f"{solve_time:.1f}s",
                        "Computation Time",
                        "info"
                    ),
                    unsafe_allow_html=True
                )
            
            render_divider()
            
            # Results tabs
            tab1, tab2, tab3 = st.tabs([
                "📅 Production Schedule",
                "📊 Summary Analytics",
                "📦 Inventory Trends"
            ])
            
            with tab1:
                plot_production_visuals(display_result, instance, params)
            
            with tab2:
                st.markdown("Production summary tables and transition statistics")
                # Implementation in postprocessing.py
            
            with tab3:
                plot_inventory_charts(display_result, instance, params)
            
            render_divider()
            
            # Action buttons
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("🔄 New Optimization", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state.uploaded_file = None
                    st.session_state.instance = None
                    st.rerun()
            
            with col2:
                if st.button("🔧 Adjust Parameters", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()
        
        else:
            # No feasible solution
            status_text.markdown(
                render_alert("⚠️ No feasible solution found. Please review constraints.", "warning"),
                unsafe_allow_html=True
            )
            
            with st.expander("🔍 Troubleshooting Guide", expanded=True):
                st.markdown("""
                ### Common Causes & Solutions
                
                #### 🔴 Capacity Issues
                - **Problem**: Total demand exceeds production capacity
                - **Solution**: Increase plant capacity or reduce demand forecasts
                
                #### 🔴 Constraint Conflicts
                - **Problem**: Minimum run days too long for available windows
                - **Solution**: Reduce minimum run day requirements
                
                #### 🔴 Inventory Issues
                - **Problem**: Cannot meet minimum closing inventory targets
                - **Solution**: Increase opening inventory or lower targets
                
                #### 🔴 Shutdown Conflicts
                - **Problem**: Shutdown periods block critical production
                - **Solution**: Reschedule shutdowns or increase opening inventory
                """)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🔄 Try Again", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state.uploaded_file = None
                    st.session_state.instance = None
                    st.rerun()
            
            with col2:
                if st.button("⚙️ Adjust Settings", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error during optimization: {e}")
        
        with st.expander("View Technical Details"):
            import traceback
            st.code(traceback.format_exc())
        
        if st.button("← Return to Start"):
            st.session_state.step = 1
            st.session_state.uploaded_file = None
            st.session_state.instance = None
            st.rerun()


# ============================================================================
# FOOTER
# ============================================================================

render_footer()
