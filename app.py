"""
Main Application Entry Point
=============================

Streamlit app orchestrating the polymer production scheduling workflow.
"""

import streamlit as st
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

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
    initial_sidebar_state="expanded"
)

# Inject custom CSS
ui_components.inject_custom_css()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'instance' not in st.session_state:
    st.session_state.instance = None
if 'solver_result' not in st.session_state:
    st.session_state.solver_result = None
if 'display_result' not in st.session_state:
    st.session_state.display_result = None

# ============================================================================
# HEADER
# ============================================================================

ui_components.render_header()

# ============================================================================
# SIDEBAR - OPTIMIZATION PARAMETERS
# ============================================================================

(
    transition_penalty,
    stockout_penalty,
    time_limit,
    buffer_days
) = ui_components.render_sidebar_inputs(
    default_transition=constants.DEFAULT_TRANSITION_PENALTY,
    default_stockout=constants.DEFAULT_STOCKOUT_PENALTY,
    default_timelimit=constants.DEFAULT_TIME_LIMIT_MIN,
    default_buffer=constants.DEFAULT_BUFFER_DAYS,
)

# ============================================================================
# FILE UPLOAD
# ============================================================================

st.markdown("## 📁 Step 1: Upload Production Template")

col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose Excel File",
        type=["xlsx"],
        help="Upload the Polymer Production Template with Plant, Inventory, and Demand sheets",
        label_visibility="collapsed"
    )

with col2:
    # Provide sample template download
    template_path = current_dir / "polymer_production_template.xlsx"
    if template_path.exists():
        with open(template_path, "rb") as f:
            st.download_button(
                label="📥 Download Template",
                data=f,
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

if uploaded_file is None:
    st.info(
        "👆 Please upload your production planning Excel file to begin.\n\n"
        "If you don't have a file ready, download the template and fill it with your data."
    )
    st.stop()

# ============================================================================
# DATA LOADING & VALIDATION
# ============================================================================

if st.session_state.instance is None or uploaded_file:
    st.markdown("## 🔍 Step 2: Data Validation")
    
    with st.spinner("Loading and validating data..."):
        try:
            # Load data
            instance = data_loader.load_excel_data(uploaded_file)
            
            # Add buffer days
            instance = data_loader.add_buffer_days(instance, buffer_days)
            
            # Store in session
            st.session_state.instance = instance
            
            st.success("✅ Data loaded and validated successfully!")
            
        except data_loader.DataLoadError as e:
            st.error(f"❌ Data validation failed: {str(e)}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error loading data: {str(e)}")
            with st.expander("View Technical Details"):
                import traceback
                st.code(traceback.format_exc())
            st.stop()

ui_components.render_divider()

# ============================================================================
# DATA PREVIEW
# ============================================================================

st.markdown("## 📋 Step 3: Review Input Data")

preview_tables.show_preview_tables(st.session_state.instance)

ui_components.render_divider()

# ============================================================================
# OPTIMIZATION
# ============================================================================

st.markdown("## 🚀 Step 4: Run Optimization")

# Show current parameter summary
col1, col2, col3, col4 = st.columns(4)
col1.metric("Time Limit", f"{time_limit} min")
col2.metric("Stockout Penalty", stockout_penalty)
col3.metric("Transition Penalty", transition_penalty)
col4.metric("Buffer Days", buffer_days)

st.markdown("---")

run_button = st.button("▶️ Run Optimization", type="primary", use_container_width=True)

if not run_button and st.session_state.solver_result is None:
    ui_components.render_run_button_message()
    st.stop()

if run_button or st.session_state.solver_result is not None:
    
    if run_button:
        # Run optimization
        with st.spinner("🔧 Building optimization model..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.info("📊 Preprocessing data...")
            progress_bar.progress(20)
            time.sleep(0.5)
            
            status_text.info("🔧 Building constraint model...")
            progress_bar.progress(40)
            time.sleep(0.5)
            
            status_text.info("⚡ Solving optimization problem...")
            progress_bar.progress(60)
            
            # Solve
            try:
                solver_result = solver_cp_sat.solve(
                    st.session_state.instance,
                    {
                        'time_limit_min': time_limit,
                        'stockout_penalty': stockout_penalty,
                        'transition_penalty': transition_penalty,
                        'buffer_days': buffer_days,
                    }
                )
                
                st.session_state.solver_result = solver_result
                
                progress_bar.progress(80)
                status_text.info("📈 Processing results...")
                
                # Convert to display format
                display_result = postprocessing.convert_solver_output_to_display(
                    solver_result,
                    st.session_state.instance
                )
                st.session_state.display_result = display_result
                
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                
            except Exception as e:
                st.error(f"❌ Optimization failed: {str(e)}")
                with st.expander("View Technical Details"):
                    import traceback
                    st.code(traceback.format_exc())
                st.stop()
    
    ui_components.render_divider()
    
    # ========================================================================
    # RESULTS DISPLAY
    # ========================================================================
    
    st.markdown("## 📊 Optimization Results")
    
    solver_result = st.session_state.solver_result
    display_result = st.session_state.display_result
    
    # Show status
    ui_components.render_optimization_status(
        solver_result['status'],
        solver_result['runtime']
    )
    
    # Check if solution exists
    if display_result is None:
        st.error("❌ No feasible solution found.")
        ui_components.render_troubleshooting_guide()
        
        # Reset button
        if st.button("🔄 Try Again with Different Parameters"):
            st.session_state.solver_result = None
            st.session_state.display_result = None
            st.rerun()
        
        st.stop()
    
    # Display summary metrics
    total_stockouts = sum(
        sum(display_result['stockout'].get(g, {}).values())
        for g in st.session_state.instance['grades']
    )
    
    ui_components.render_summary_metrics(
        objective=display_result['objective'],
        transitions=display_result['transitions']['total'],
        stockouts=total_stockouts,
        planning_days=len(st.session_state.instance['dates'])
    )
    
    ui_components.render_divider()
    
    # ========================================================================
    # VISUALIZATIONS
    # ========================================================================
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "📅 Production Schedule",
        "📦 Inventory Trends",
        "📊 Production Summary"
    ])
    
    with tab1:
        postprocessing.plot_production_visuals(
            display_result,
            st.session_state.instance,
            {'buffer_days': buffer_days}
        )
    
    with tab2:
        postprocessing.plot_inventory_charts(
            display_result,
            st.session_state.instance,
            {'buffer_days': buffer_days}
        )
    
    with tab3:
        postprocessing.render_production_summary(
            display_result,
            st.session_state.instance
        )
    
    ui_components.render_divider()
    
    # ========================================================================
    # ACTION BUTTONS
    # ========================================================================
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 New Optimization", use_container_width=True):
            st.session_state.instance = None
            st.session_state.solver_result = None
            st.session_state.display_result = None
            st.rerun()
    
    with col2:
        if st.button("⚙️ Adjust Parameters", use_container_width=True):
            st.session_state.solver_result = None
            st.session_state.display_result = None
            st.rerun()
    
    with col3:
        # Export functionality (placeholder for future)
        st.button("📥 Export Results", use_container_width=True, disabled=True)
        st.caption("Export feature coming soon")

# ============================================================================
# FOOTER
# ============================================================================

ui_components.render_footer()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Polymer Production Scheduler",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_custom_css()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'instance' not in st.session_state:
    st.session_state.instance = None
if 'solver_result' not in st.session_state:
    st.session_state.solver_result = None
if 'display_result' not in st.session_state:
    st.session_state.display_result = None

# ============================================================================
# HEADER
# ============================================================================

render_header()

# ============================================================================
# SIDEBAR - OPTIMIZATION PARAMETERS
# ============================================================================

(
    transition_penalty,
    stockout_penalty,
    time_limit,
    buffer_days
) = render_sidebar_inputs(
    default_transition=DEFAULT_TRANSITION_PENALTY,
    default_stockout=DEFAULT_STOCKOUT_PENALTY,
    default_timelimit=DEFAULT_TIME_LIMIT_MIN,
    default_buffer=DEFAULT_BUFFER_DAYS,
)

# ============================================================================
# FILE UPLOAD
# ============================================================================

st.markdown("## 📁 Step 1: Upload Production Template")

col1, col2 = st.columns([3, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose Excel File",
        type=["xlsx"],
        help="Upload the Polymer Production Template with Plant, Inventory, and Demand sheets",
        label_visibility="collapsed"
    )

with col2:
    # Provide sample template download
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

if uploaded_file is None:
    st.info(
        "👆 Please upload your production planning Excel file to begin.\n\n"
        "If you don't have a file ready, download the template and fill it with your data."
    )
    st.stop()

# ============================================================================
# DATA LOADING & VALIDATION
# ============================================================================

if st.session_state.instance is None or uploaded_file:
    st.markdown("## 🔍 Step 2: Data Validation")
    
    with st.spinner("Loading and validating data..."):
        try:
            # Load data
            instance = load_excel_data(uploaded_file)
            
            # Add buffer days
            instance = add_buffer_days(instance, buffer_days)
            
            # Store in session
            st.session_state.instance = instance
            
            st.success("✅ Data loaded and validated successfully!")
            
        except DataLoadError as e:
            st.error(f"❌ Data validation failed: {str(e)}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error loading data: {str(e)}")
            with st.expander("View Technical Details"):
                import traceback
                st.code(traceback.format_exc())
            st.stop()

render_divider()

# ============================================================================
# DATA PREVIEW
# ============================================================================

st.markdown("## 📋 Step 3: Review Input Data")

show_preview_tables(st.session_state.instance)

render_divider()

# ============================================================================
# OPTIMIZATION
# ============================================================================

st.markdown("## 🚀 Step 4: Run Optimization")

# Show current parameter summary
col1, col2, col3, col4 = st.columns(4)
col1.metric("Time Limit", f"{time_limit} min")
col2.metric("Stockout Penalty", stockout_penalty)
col3.metric("Transition Penalty", transition_penalty)
col4.metric("Buffer Days", buffer_days)

st.markdown("---")

run_button = st.button("▶️ Run Optimization", type="primary", use_container_width=True)

if not run_button and st.session_state.solver_result is None:
    render_run_button_message()
    st.stop()

if run_button or st.session_state.solver_result is not None:
    
    if run_button:
        # Run optimization
        with st.spinner("🔧 Building optimization model..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.info("📊 Preprocessing data...")
            progress_bar.progress(20)
            time.sleep(0.5)
            
            status_text.info("🔧 Building constraint model...")
            progress_bar.progress(40)
            time.sleep(0.5)
            
            status_text.info("⚡ Solving optimization problem...")
            progress_bar.progress(60)
            
            # Solve
            try:
                solver_result = solve(
                    st.session_state.instance,
                    {
                        'time_limit_min': time_limit,
                        'stockout_penalty': stockout_penalty,
                        'transition_penalty': transition_penalty,
                        'buffer_days': buffer_days,
                    }
                )
                
                st.session_state.solver_result = solver_result
                
                progress_bar.progress(80)
                status_text.info("📈 Processing results...")
                
                # Convert to display format
                display_result = convert_solver_output_to_display(
                    solver_result,
                    st.session_state.instance
                )
                st.session_state.display_result = display_result
                
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                
            except Exception as e:
                st.error(f"❌ Optimization failed: {str(e)}")
                with st.expander("View Technical Details"):
                    import traceback
                    st.code(traceback.format_exc())
                st.stop()
    
    render_divider()
    
    # ========================================================================
    # RESULTS DISPLAY
    # ========================================================================
    
    st.markdown("## 📊 Optimization Results")
    
    solver_result = st.session_state.solver_result
    display_result = st.session_state.display_result
    
    # Show status
    render_optimization_status(
        solver_result['status'],
        solver_result['runtime']
    )
    
    # Check if solution exists
    if display_result is None:
        st.error("❌ No feasible solution found.")
        render_troubleshooting_guide()
        
        # Reset button
        if st.button("🔄 Try Again with Different Parameters"):
            st.session_state.solver_result = None
            st.session_state.display_result = None
            st.rerun()
        
        st.stop()
    
    # Display summary metrics
    total_stockouts = sum(
        sum(display_result['stockout'].get(g, {}).values())
        for g in st.session_state.instance['grades']
    )
    
    render_summary_metrics(
        objective=display_result['objective'],
        transitions=display_result['transitions']['total'],
        stockouts=total_stockouts,
        planning_days=len(st.session_state.instance['dates'])
    )
    
    render_divider()
    
    # ========================================================================
    # VISUALIZATIONS
    # ========================================================================
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "📅 Production Schedule",
        "📦 Inventory Trends",
        "📊 Production Summary"
    ])
    
    with tab1:
        plot_production_visuals(
            display_result,
            st.session_state.instance,
            {'buffer_days': buffer_days}
        )
    
    with tab2:
        plot_inventory_charts(
            display_result,
            st.session_state.instance,
            {'buffer_days': buffer_days}
        )
    
    with tab3:
        render_production_summary(
            display_result,
            st.session_state.instance
        )
    
    render_divider()
    
    # ========================================================================
    # ACTION BUTTONS
    # ========================================================================
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 New Optimization", use_container_width=True):
            st.session_state.instance = None
            st.session_state.solver_result = None
            st.session_state.display_result = None
            st.rerun()
    
    with col2:
        if st.button("⚙️ Adjust Parameters", use_container_width=True):
            st.session_state.solver_result = None
            st.session_state.display_result = None
            st.rerun()
    
    with col3:
        # Export functionality (placeholder for future)
        st.button("📥 Export Results", use_container_width=True, disabled=True)
        st.caption("Export feature coming soon")

# ============================================================================
# FOOTER
# ============================================================================

render_footer()
