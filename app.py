"""
Main Application Entry Point
=============================

Streamlit app following test(1).py UI style with Old Logic with Sidebar.py solver logic.
"""

import streamlit as st
import time
import io
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

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: Upload, 2: Preview & Config, 3: Results
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'instance' not in st.session_state:
    st.session_state.instance = None
if 'solver_result' not in st.session_state:
    st.session_state.solver_result = None
if 'display_result' not in st.session_state:
    st.session_state.display_result = None

# Initialize optimization parameters in session state
if 'optimization_params' not in st.session_state:
    st.session_state.optimization_params = {
        'buffer_days': 3,
        'time_limit_min': 10,
        'stockout_penalty': 10,
        'transition_penalty': 50,
    }

# Inject custom CSS
ui_components.inject_custom_css()

# ============================================================================
# HEADER
# ============================================================================

ui_components.render_header()

# ============================================================================
# STEP INDICATOR
# ============================================================================

step_status = ['active' if st.session_state.step == 1 else 'completed',
               'active' if st.session_state.step == 2 else ('completed' if st.session_state.step > 2 else ''),
               'active' if st.session_state.step == 3 else '']

st.markdown(f"""
<div style="display: flex; justify-content: center; margin: 2rem 0 3rem 0;">
    <div style="display: flex; align-items: center; max-width: 600px; width: 100%;">
        <div style="flex: 1; text-align: center;">
            <div style="width: 48px; height: 48px; border-radius: 50%; 
                        background: {'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' if step_status[0] == 'active' else '#4caf50' if step_status[0] == 'completed' else 'white'};
                        border: 3px solid {'#667eea' if step_status[0] == 'active' else '#4caf50' if step_status[0] == 'completed' else '#e0e0e0'};
                        color: {'white' if step_status[0] in ['active', 'completed'] else '#9e9e9e'};
                        display: inline-flex; align-items: center; justify-content: center;
                        font-weight: 600; font-size: 1.125rem; margin: 0 auto;">
                {'✓' if st.session_state.step > 1 else '1'}
            </div>
            <div style="margin-top: 0.75rem; font-size: 0.875rem; font-weight: {'600' if step_status[0] == 'active' else '500'};
                        color: {'#667eea' if step_status[0] == 'active' else '#4caf50' if step_status[0] == 'completed' else '#757575'};">
                Upload Data
            </div>
        </div>
        <div style="flex: 1; height: 3px; background: {'#4caf50' if st.session_state.step > 1 else '#e0e0e0'}; margin: 0 1rem 2rem 1rem;"></div>
        <div style="flex: 1; text-align: center;">
            <div style="width: 48px; height: 48px; border-radius: 50%; 
                        background: {'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' if step_status[1] == 'active' else '#4caf50' if step_status[1] == 'completed' else 'white'};
                        border: 3px solid {'#667eea' if step_status[1] == 'active' else '#4caf50' if step_status[1] == 'completed' else '#e0e0e0'};
                        color: {'white' if step_status[1] in ['active', 'completed'] else '#9e9e9e'};
                        display: inline-flex; align-items: center; justify-content: center;
                        font-weight: 600; font-size: 1.125rem; margin: 0 auto;">
                {'✓' if st.session_state.step > 2 else '2'}
            </div>
            <div style="margin-top: 0.75rem; font-size: 0.875rem; font-weight: {'600' if step_status[1] == 'active' else '500'};
                        color: {'#667eea' if step_status[1] == 'active' else '#4caf50' if step_status[1] == 'completed' else '#757575'};">
                Configure
            </div>
        </div>
        <div style="flex: 1; height: 3px; background: {'#4caf50' if st.session_state.step > 2 else '#e0e0e0'}; margin: 0 1rem 2rem 1rem;"></div>
        <div style="flex: 1; text-align: center;">
            <div style="width: 48px; height: 48px; border-radius: 50%; 
                        background: {'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' if step_status[2] == 'active' else 'white'};
                        border: 3px solid {'#667eea' if step_status[2] == 'active' else '#e0e0e0'};
                        color: {'white' if step_status[2] == 'active' else '#9e9e9e'};
                        display: inline-flex; align-items: center; justify-content: center;
                        font-weight: 600; font-size: 1.125rem; margin: 0 auto;">
                3
            </div>
            <div style="margin-top: 0.75rem; font-size: 0.875rem; font-weight: {'600' if step_status[2] == 'active' else '500'};
                        color: {'#667eea' if step_status[2] == 'active' else '#757575'};">
                Results
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

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
            st.success("✅ File uploaded successfully!")
            time.sleep(0.5)
            st.session_state.step = 2
            st.rerun()

    with col2:
        # Template download
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
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="material-card">
            <div class="card-title">📋 Quick Start Guide</div>
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
# STEP 2: PREVIEW & CONFIGURE
# ============================================================================

elif st.session_state.step == 2:
    try:
        # Load data if not already loaded
        if st.session_state.instance is None:
            uploaded_file = st.session_state.uploaded_file
            uploaded_file.seek(0)
            
            with st.spinner("Loading and validating data..."):
                instance = data_loader.load_excel_data(uploaded_file)
                st.session_state.instance = instance
                st.success("✅ Data loaded successfully!")
        
        instance = st.session_state.instance
        
        # Data preview
        preview_tables.show_preview_tables(instance)
        
        ui_components.render_divider()
        
        # Configuration section
        st.markdown("""
        <div class="material-card">
            <div class="card-title">⚙️ Optimization Parameters</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Core Settings")
            st.session_state.optimization_params['time_limit_min'] = st.number_input(
                "⏱️ Time Limit (minutes)",
                min_value=1,
                max_value=120,
                value=st.session_state.optimization_params['time_limit_min'],
                help="Maximum solver runtime"
            )
            
            st.session_state.optimization_params['buffer_days'] = st.number_input(
                "📅 Planning Buffer (days)",
                min_value=0,
                max_value=7,
                value=st.session_state.optimization_params['buffer_days'],
                help="Additional days for safety planning"
            )
        
        with col2:
            st.markdown("#### Objective Weights")
            st.session_state.optimization_params['stockout_penalty'] = st.number_input(
                "🎯 Stockout Penalty",
                min_value=1,
                max_value=10000,
                value=st.session_state.optimization_params['stockout_penalty'],
                help="Cost weight for inventory shortages"
            )
            
            st.session_state.optimization_params['transition_penalty'] = st.number_input(
                "🔄 Transition Penalty",
                min_value=1,
                max_value=10000,
                value=st.session_state.optimization_params['transition_penalty'],
                help="Cost weight for grade changeovers"
            )
        
        ui_components.render_divider()
        
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
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        if st.button("← Back to Upload"):
            st.session_state.step = 1
            st.session_state.instance = None
            st.rerun()

# ============================================================================
# STEP 3: OPTIMIZATION & RESULTS
# ============================================================================

elif st.session_state.step == 3:
    try:
        # Run optimization if not already done
        if st.session_state.solver_result is None:
            st.markdown("""
            <div class="material-card">
                <div class="card-title">⚡ Running Optimization</div>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            time.sleep(0.5)
            
            status_text.markdown('<div class="alert-box info">📊 Preprocessing data...</div>', unsafe_allow_html=True)
            progress_bar.progress(10)
            time.sleep(0.5)
            
            # Add buffer days
            instance = st.session_state.instance
            params = st.session_state.optimization_params
            buffer_days = params['buffer_days']
            
            instance = data_loader.add_buffer_days(instance, buffer_days)
            
            status_text.markdown('<div class="alert-box info">🔧 Building optimization model...</div>', unsafe_allow_html=True)
            progress_bar.progress(30)
            time.sleep(0.5)
            
            status_text.markdown('<div class="alert-box info">⚡ Running solver...</div>', unsafe_allow_html=True)
            progress_bar.progress(50)
            
            # Solve
            solver_result = solver_cp_sat.solve(instance, params)
            
            st.session_state.solver_result = solver_result
            
            progress_bar.progress(80)
            status_text.markdown('<div class="alert-box info">📈 Processing results...</div>', unsafe_allow_html=True)
            
            # Convert to display format
            display_result = postprocessing.convert_solver_output_to_display(solver_result, instance)
            st.session_state.display_result = display_result
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
        
        ui_components.render_divider()
        
        # Display results
        solver_result = st.session_state.solver_result
        display_result = st.session_state.display_result
        instance = st.session_state.instance
        params = st.session_state.optimization_params
        
        # Show status
        ui_components.render_optimization_status(solver_result['status'], solver_result['runtime'])
        
        time.sleep(0.5)
        ui_components.render_divider()
        
        if display_result is None:
            st.markdown("""
            <div class="alert-box warning">
                <div>
                    <strong>❌ No Feasible Solution Found</strong><br>
                    The optimization could not find a valid schedule with the given constraints.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            ui_components.render_troubleshooting_guide()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("🔄 Try Again", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state.uploaded_file = None
                    st.session_state.instance = None
                    st.session_state.solver_result = None
                    st.session_state.display_result = None
                    st.rerun()
            
            with col2:
                if st.button("⚙️ Adjust Settings", use_container_width=True):
                    st.session_state.step = 2
                    st.session_state.solver_result = None
                    st.session_state.display_result = None
                    st.rerun()
        
        else:
            # Display summary metrics
            total_stockouts = sum(
                sum(display_result['stockout'].get(g, {}).values())
                for g in instance['grades']
            )
            
            ui_components.render_summary_metrics(
                objective=display_result['objective'],
                transitions=display_result['transitions']['total'],
                stockouts=total_stockouts,
                planning_days=instance['num_days']
            )
            
            ui_components.render_divider()
            
            # Tabbed results
            tab1, tab2, tab3 = st.tabs(["📅 Production Schedule", "📊 Summary Analytics", "📦 Inventory Trends"])
            
            with tab1:
                postprocessing.plot_production_visuals(display_result, instance, params)
            
            with tab2:
                postprocessing.render_production_summary(display_result, instance)
            
            with tab3:
                postprocessing.plot_inventory_charts(display_result, instance, params)
            
            ui_components.render_divider()
            
            # Action buttons
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("🔄 New Optimization", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state.uploaded_file = None
                    st.session_state.instance = None
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
        st.markdown(f"""
        <div class="alert-box warning">
            <div>
                <strong>❌ Error During Optimization</strong><br>
                {str(e)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("View Technical Details"):
            import traceback
            st.code(traceback.format_exc())
        
        if st.button("← Return to Start"):
            st.session_state.step = 1
            st.session_state.uploaded_file = None
            st.session_state.instance = None
            st.session_state.solver_result = None
            st.session_state.display_result = None
            st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

ui_components.render_footer()
