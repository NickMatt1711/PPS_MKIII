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
    'switch_cost': DEFAULT_SWITCH_COST,
    'capacity_utilization_penalty': DEFAULT_CAPACITY_PENALTY,
    'max_plan_horizon_days': MAX_PLAN_HORIZON_DAYS,
})

# --- Stage Handlers ---

def render_upload_stage():
    """Renders the data upload stage with an improved centered UI."""
    
    # Use columns to center the content container
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        # Custom-styled card container
        with st.container(border=False):
            st.markdown(f'<div class="upload-card">', unsafe_allow_html=True)
            
            # Header
            st.markdown(f'<h1 class="main-title">{APP_TITLE}</h1>', unsafe_allow_html=True)
            st.subheader("Step 1: Upload Data")
            st.markdown(
                """
                Upload the Excel file containing your production constraints,
                demand forecast, inventory levels, and plant configuration.
                """
            )

            render_section_divider()

            # 1. Template Download & Instructions (Grouped)
            st.markdown("### Template & Format")
            st.info("The file **must** be an Excel file (`.xlsx`) and contain the sheets: `Configuration`, `Inventory`, `Demand`, and `Production`. Click below to download the required template.")
            
            # The download button from ui_components.py
            render_download_template_button()
            
            render_section_divider()

            # 2. File Uploader (Main Action)
            st.markdown("### Upload your Data File")
            
            # Use a slightly less busy message for the uploader
            uploaded_file = st.file_uploader(
                "Upload Excel File (.xlsx)",
                type=['xlsx'],
                accept_multiple_files=False,
                key="file_uploader_key",
                label_visibility="collapsed" # Hide default label for cleaner UI
            )
            
            # Apply custom CSS class to the uploader area for visual distinction
            st.markdown(
                """
                <style>
                    /* Target the specific container that holds the file uploader widget */
                    #file_uploader_key + div.stFileUploader {
                        border: 2px dashed var(--md-sys-color-primary-container);
                        padding: 2rem;
                        border-radius: 0.75rem;
                        background-color: var(--md-sys-color-background);
                        transition: background-color 0.3s ease;
                    }
                </style>
                """, unsafe_allow_html=True
            )
            
            # 3. Process Button
            if uploaded_file is not None:
                # Add a success message and show the next button
                st.success("File uploaded successfully! Click 'Process' to continue.")
                
                # Center the button or use full width in this section
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    if st.button("Process & Go to Configuration →", use_container_width=True, type="primary"):
                        try:
                            # Load data and store in session state
                            st.session_state[SS_UPLOADED_FILE] = uploaded_file.name
                            st.session_state[SS_EXCEL_DATA] = load_all_excel_data(uploaded_file)
                            st.session_state[SS_STAGE] = STAGE_PREVIEW
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error reading file: {e}")
                            st.exception(e)
            
            st.markdown('</div>', unsafe_allow_html=True)


def render_preview_stage():
    """Renders the data preview and parameter configuration stage."""
    # ... (rest of the render_preview_stage remains the same)
    st.title(f"{APP_TITLE} - Data Preview and Configuration")
    
    # 1. Sidebar for parameters
    with st.sidebar:
        st.header("Optimization Parameters")
        
        # ... (Parameter inputs)
        
        # st.session_state[SS_OPTIMIZATION_PARAMS]['time_limit_min'] = st.slider(...)
        
        # Logic to set parameters and run optimization (moved from original)
        if st.button("Run Optimization", use_container_width=True, type="primary"):
            st.session_state[SS_STAGE] = STAGE_OPTIMIZING
            st.rerun()

    # 2. Main content for data preview
    st.subheader("Verify Uploaded Data")
    
    # Tabs for each data table
    tab_config, tab_inv, tab_demand, tab_prod = st.tabs([
        "Plant Configuration", 
        "Initial Inventory", 
        "Demand Forecast", 
        "Production Constraints"
    ])

    excel_data = st.session_state.get(SS_EXCEL_DATA)
    if excel_data:
        # Render the custom preview tables
        with tab_config:
            render_configuration_preview(excel_data['Configuration'])
        with tab_inv:
            render_inventory_preview(excel_data['Inventory'])
        with tab_demand:
            render_demand_preview(excel_data['Demand'])
        with tab_prod:
            render_production_preview(excel_data['Production'])
            
    render_section_divider()

    # Navigation - Back button
    if st.button("← Back to Upload", use_container_width=False):
        st.session_state[SS_STAGE] = STAGE_UPLOAD
        st.rerun()


def render_optimization_stage():
    """Renders the optimization progress stage."""
    # ... (rest of the render_optimization_stage remains the same)
    st.title(f"{APP_TITLE} - Running Optimization")
    st.subheader("Model Calculation in Progress...")
    
    st.progress(0, text="Initializing Solver...")
    render_skeleton_loader(rows=5)
    
    # --- Optimization Logic Placeholder ---
    
    # In a real app, this would run the solver and update the progress bar.
    # For demonstration, we simulate the run and jump to results.
    import time
    time.sleep(1) # Simulate initial loading
    st.progress(25, text="Loading and Preprocessing Data...")
    time.sleep(1) 
    st.progress(50, text="Building CP-SAT Model...")
    time.sleep(1)
    
    # Run the actual solver (assuming it handles the status update internally or returns results)
    excel_data = st.session_state[SS_EXCEL_DATA]
    params = st.session_state[SS_OPTIMIZATION_PARAMS]
    
    solution_result = build_and_solve_model(excel_data, params)
    
    st.session_state[SS_SOLUTION] = solution_result
    st.session_state[SS_STAGE] = STAGE_RESULTS
    st.rerun()
    
    # --- End Optimization Logic Placeholder ---


def render_results_stage():
    """Renders the optimization results and visualization stage."""
    # ... (rest of the render_results_stage remains the same)
    st.title(f"{APP_TITLE} - Optimization Results")
    st.subheader("Optimal Production Schedule Generated")

    solution = st.session_state.get(SS_SOLUTION)
    excel_data = st.session_state.get(SS_EXCEL_DATA)
    
    if not solution or not excel_data:
        st.error("No solution found or data is missing. Please restart.")
        if st.button("Go to Upload"):
            st.session_state[SS_STAGE] = STAGE_UPLOAD
            st.rerun()
        return

    # Post-processing and KPI calculation
    results_df = solution['results_df']
    
    # KPI 1: Objective Value
    st.metric(
        label="Total Optimization Cost (Minimized)",
        value=f"${solution['objective_value']:,.0f}"
    )

    render_section_divider()

    # KPI 2: Stockout Summary
    total_stockouts_from_solution = results_df['Stockout_MT'].sum()
    st.subheader("Key Performance Indicators (KPIs)")
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    with col_kpi1:
        st.metric("Model Runtime", f"{solution['runtime_sec']:.1f}s")
    
    with col_kpi2:
        if total_stockouts_from_solution == 0:
            st.success("✅ Zero Stockouts Reported")
        else:
            st.warning(f"⚠️ Total Stockout: {total_stockouts_from_solution:,.0f} MT")
    
    with col_kpi3:
        # Calculate utilization
        total_capacity = excel_data['Configuration']['Daily Capacity (MT)'].sum() * len(results_df['Date'].unique())
        total_production = results_df['Production_MT'].sum()
        utilization = (total_production / total_capacity) * 100 if total_capacity else 0
        st.metric("Capacity Utilization", f"{utilization:.1f}%")

    render_section_divider()
    
    # Tabbed views for detailed results
    tab_chart, tab_tables, tab_metrics = st.tabs([
        "Production Schedule Chart", 
        "Detailed Tables", 
        "Solver Metrics"
    ])

    with tab_chart:
        st.subheader("Gantt Chart Visualization (Simulated)")
        # This function would render an interactive Gantt chart (e.g., using Altair or Plotly)
        # render_gantt_chart(results_df) 
        
        # Placeholder for the chart visualization
        st.markdown(
            '<div style="height: 300px; background-color: #f0f4f8; border-radius: 0.5rem; display: flex; align-items: center; justify-content: center; color: #5A6F8E;">'
            'Interactive Production Gantt Chart Placeholder'
            '</div>', unsafe_allow_html=True
        )


    with tab_tables:
        st.subheader("Detailed Production and Inventory Data")
        
        # The detailed results table
        st.dataframe(results_df)
        
        # Download button for the results
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="optimized_schedule.csv",
            mime="text/csv",
            use_container_width=False
        )

    with tab_metrics:
        st.subheader("Solver Performance")
        st.json(solution['solver_metrics']) # Assuming solver metrics are stored as a dict

    render_section_divider()

    # Navigation - Enhanced button layout
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

    # st.sidebar.header("Navigation") # Optionally show navigation in sidebar
    # st.sidebar.markdown(f"**Current Stage:** {list(STAGE_MAP.keys())[current_stage]}")

    if current_stage == STAGE_UPLOAD:
        render_upload_stage()
    elif current_stage == STAGE_PREVIEW:
        render_preview_stage()
    elif current_stage == STAGE_OPTIMIZING:
        render_optimization_stage()
    elif current_stage == STAGE_RESULTS:
        render_results_stage()
    else:
        st.error("Invalid application stage.")
        if st.button("Reset Application"):
            st.session_state.clear()
            st.session_state[SS_STAGE] = STAGE_UPLOAD
            st.rerun()


if __name__ == "__main__":
    main()
