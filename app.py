"""
Polymer Production Scheduler - Main Application
A wizard-based Streamlit app for multi-plant production optimization
"""

import streamlit as st
import io
from ortools.sat.python import cp_model

# Import modules
from constants import *
from ui_components import *
from data_loader import *
from preview_tables import *
from solver_cp_sat import build_and_solve_model
from postprocessing import *


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
apply_custom_css()

# Initialize session state
if SS_STAGE not in st.session_state:
    st.session_state[SS_STAGE] = 0
if SS_UPLOADED_FILE not in st.session_state:
    st.session_state[SS_UPLOADED_FILE] = None
if SS_EXCEL_DATA not in st.session_state:
    st.session_state[SS_EXCEL_DATA] = None
if SS_OPTIMIZATION_PARAMS not in st.session_state:
    st.session_state[SS_OPTIMIZATION_PARAMS] = {
        'time_limit_min': DEFAULT_TIME_LIMIT_MIN,
        'buffer_days': DEFAULT_BUFFER_DAYS,
        'stockout_penalty': DEFAULT_STOCKOUT_PENALTY,
        'transition_penalty': DEFAULT_TRANSITION_PENALTY,
        'continuity_bonus': DEFAULT_CONTINUITY_BONUS,
    }
if SS_SOLUTION not in st.session_state:
    st.session_state[SS_SOLUTION] = None


# ========== STAGE 0: UPLOAD ==========
def render_upload_stage():
    """Stage 1: File upload"""
    
    render_header(f"{APP_ICON} {APP_TITLE}", "Multi-Plant Optimization with Shutdown Management")
    render_stage_progress(0)
    
    st.markdown("### 📤 Upload Production Data")
    st.markdown("Upload an Excel file containing your production planning data.")
    
    # Upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=ALLOWED_EXTENSIONS,
            help="Upload an Excel file with Plant, Inventory, and Demand sheets"
        )
        
        if uploaded_file is not None:
            st.session_state[SS_UPLOADED_FILE] = uploaded_file
            render_alert("File uploaded successfully! Click 'Next' to preview your data.", "success")
    
    with col2:
        st.markdown("#### 📋 Required Sheets")
        for sheet in REQUIRED_SHEETS:
            st.markdown(f"✓ **{sheet}**")
        st.markdown("#### 🔄 Optional Sheets")
        st.markdown("• Transition matrices")
    
    render_section_divider()
    
    # Information section
    with st.expander("ℹ️ What data do I need?", expanded=False):
        st.markdown("""
        Your Excel file should contain:
        
        **Plant Sheet**: Plant names, capacities, material running, shutdown periods
        
        **Inventory Sheet**: Grade names, inventory levels, run constraints, allowed lines
        
        **Demand Sheet**: Daily demand forecasts for each grade
        
        **Transition Sheets (Optional)**: Grade transition rules for each plant
        """)
    
    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("Next: Preview Data →", type="primary", disabled=uploaded_file is None, use_container_width=True):
            # Load and validate data
            file_buffer = io.BytesIO(uploaded_file.read())
            loader = ExcelDataLoader(file_buffer)
            success, data, errors, warnings = loader.load_and_validate()
            
            if success:
                st.session_state[SS_EXCEL_DATA] = data
                st.session_state[SS_STAGE] = 1
                st.rerun()
            else:
                for error in errors:
                    render_alert(error, "error")


# ========== STAGE 1: PREVIEW & CONFIGURE ==========
def render_preview_stage():
    """Stage 2: Preview data and configure parameters"""
    
    render_header(f"{APP_ICON} {APP_TITLE}", "Review data and configure optimization")
    render_stage_progress(1)
    
    excel_data = st.session_state[SS_EXCEL_DATA]
    
    # Data summary
    render_data_summary(excel_data)
    
    render_section_divider()
    
    # Tabs for preview and configuration
    tab1, tab2 = st.tabs(["📊 Data Preview", "⚙️ Optimization Settings"])
    
    with tab1:
        render_all_sheets(excel_data)
    
    with tab2:
        st.markdown("### ⚙️ Optimization Parameters")
        st.markdown("Configure the optimization solver parameters and objective weights.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⏱️ Solver Configuration")
            time_limit = st.number_input(
                "Time limit (minutes)",
                min_value=1,
                max_value=120,
                value=st.session_state[SS_OPTIMIZATION_PARAMS]['time_limit_min'],
                help="Maximum time to run the optimization"
            )
            
            buffer_days = st.number_input(
                "Buffer days",
                min_value=0,
                max_value=7,
                value=st.session_state[SS_OPTIMIZATION_PARAMS]['buffer_days'],
                help="Additional planning buffer days"
            )
        
        with col2:
            st.markdown("#### 🎯 Objective Weights")
            stockout_penalty = st.number_input(
                "Stockout penalty",
                min_value=1,
                value=st.session_state[SS_OPTIMIZATION_PARAMS]['stockout_penalty'],
                help="Penalty weight for stockouts"
            )
            
            transition_penalty = st.number_input(
                "Transition penalty",
                min_value=1,
                value=st.session_state[SS_OPTIMIZATION_PARAMS]['transition_penalty'],
                help="Penalty for production transitions"
            )
            
            continuity_bonus = st.number_input(
                "Continuity bonus",
                min_value=0,
                value=st.session_state[SS_OPTIMIZATION_PARAMS]['continuity_bonus'],
                help="Bonus for production continuity"
            )
        
        # Update parameters
        st.session_state[SS_OPTIMIZATION_PARAMS] = {
            'time_limit_min': time_limit,
            'buffer_days': buffer_days,
            'stockout_penalty': stockout_penalty,
            'transition_penalty': transition_penalty,
            'continuity_bonus': continuity_bonus,
        }
    
    render_section_divider()
    
    # Navigation and optimization button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Upload", use_container_width=True):
            st.session_state[SS_STAGE] = 0
            st.rerun()
    
    with col3:
        if st.button("🎯 Run Optimization", type="primary", use_container_width=True):
            run_optimization()


def run_optimization():
    """Execute the optimization"""
    
    excel_data = st.session_state[SS_EXCEL_DATA]
    params = st.session_state[SS_OPTIMIZATION_PARAMS]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Process plant data
        status_text.markdown("🔄 Processing plant data...")
        plant_data = process_plant_data(excel_data['Plant'])
        progress_bar.progress(0.1)
        
        # Process inventory data
        status_text.markdown("🔄 Processing inventory data...")
        inventory_data = process_inventory_data(excel_data['Inventory'], plant_data['lines'])
        progress_bar.progress(0.2)
        
        # Process demand data
        status_text.markdown("🔄 Processing demand data...")
        demand_data, dates, num_days = process_demand_data(
            excel_data['Demand'],
            params['buffer_days']
        )
        formatted_dates = [date.strftime('%d-%b-%y') for date in dates]
        progress_bar.progress(0.3)
        
        # Process shutdown periods
        status_text.markdown("🔄 Processing shutdown periods...")
        shutdown_periods = process_shutdown_dates(plant_data['shutdown_periods'], dates)
        progress_bar.progress(0.35)
        
        # Process transition rules
        status_text.markdown("🔄 Processing transition rules...")
        transition_dfs = {k: v for k, v in excel_data.items() if k.startswith('Transition_')}
        transition_rules = process_transition_rules(transition_dfs)
        progress_bar.progress(0.4)
        
        # Build and solve model
        status_text.markdown("⚡ Running optimization...")
        
        def progress_callback(pct, msg):
            progress_bar.progress(0.4 + pct * 0.6)
            status_text.markdown(f"⚡ {msg}")
        
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
            force_start_date=inventory_data['force_start_date'],
            rerun_allowed=inventory_data['rerun_allowed'],
            material_running_info=plant_data['material_running'],
            shutdown_periods=shutdown_periods,
            transition_rules=transition_rules,
            buffer_days=params['buffer_days'],
            stockout_penalty=params['stockout_penalty'],
            transition_penalty=params['transition_penalty'],
            continuity_bonus=params['continuity_bonus'],
            time_limit_min=params['time_limit_min'],
            progress_callback=progress_callback
        )
        
        progress_bar.progress(1.0)
        
        if solution_callback.num_solutions() > 0:
            status_text.markdown("✅ Optimization completed successfully!")
            
            # Store solution
            st.session_state[SS_SOLUTION] = {
                'status': status,
                'solution': solution_callback.solutions[-1],
                'solver': solver,
                'data': {
                    'grades': inventory_data['grades'],
                    'lines': plant_data['lines'],
                    'dates': dates,
                    'num_days': num_days,
                    'shutdown_periods': shutdown_periods,
                    'allowed_lines': inventory_data['allowed_lines'],
                    'min_inventory': inventory_data['min_inventory'],
                    'max_inventory': inventory_data['max_inventory'],
                }
            }
            
            st.session_state[SS_STAGE] = 2
            st.success("✅ Optimization complete! View results below.")
            st.rerun()
        else:
            status_text.markdown("❌ No solution found")
            render_alert("No feasible solution found. Please check your constraints.", "error")
    
    except Exception as e:
        status_text.markdown("❌ Optimization failed")
        render_alert(f"Error during optimization: {str(e)}", "error")
        st.exception(e)


# ========== STAGE 2: RESULTS ==========
def render_results_stage():
    """Stage 3: Display results"""
    
    render_header(f"{APP_ICON} {APP_TITLE}", "Optimization Results")
    render_stage_progress(2)
    
    solution_data = st.session_state[SS_SOLUTION]
    solution = solution_data['solution']
    data = solution_data['data']
    
    # Key metrics
    st.markdown("### 📊 Key Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    render_metric_card("Objective Value", f"{solution['objective']:,.0f}", col1)
    render_metric_card("Total Transitions", str(solution['transitions']['total']), col2)
    
    total_stockouts = sum(sum(solution['stockout'][g].values()) for g in data['grades'])
    render_metric_card("Total Stockouts", f"{total_stockouts:,.0f} MT", col3)
    render_metric_card("Planning Horizon", f"{data['num_days']} days", col4)
    
    render_section_divider()
    
    # Results tabs
    tab1, tab2, tab3 = st.tabs(["📅 Production Schedule", "📦 Inventory Analysis", "📊 Summary Tables"])
    
    with tab1:
        st.markdown("### 📅 Production Schedule")
        
        for line in data['lines']:
            st.markdown(f"#### 🏭 {line}")
            
            # Gantt chart
            fig = create_gantt_chart(solution, line, data['dates'], data['shutdown_periods'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Schedule table
            schedule_df = create_schedule_table(solution, line, data['dates'])
            if not schedule_df.empty:
                st.dataframe(schedule_df, use_container_width=True)
            
            render_section_divider()
    
    with tab2:
        st.markdown("### 📦 Inventory Analysis")
        
        for grade in sorted(data['grades']):
            st.markdown(f"#### {grade}")
            
            fig = create_inventory_chart(
                solution, grade, data['dates'],
                data['min_inventory'][grade],
                data['max_inventory'][grade],
                data['allowed_lines'][grade],
                data['shutdown_periods']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 📊 Production Summary")
        
        summary_df = create_production_summary(solution, data['grades'], data['lines'])
        st.dataframe(summary_df, use_container_width=True)
        
        st.markdown("### 🔄 Transitions by Line")
        transitions_data = []
        for line, count in solution['transitions']['per_line'].items():
            transitions_data.append({'Line': line, 'Transitions': count})
        transitions_df = pd.DataFrame(transitions_data)
        st.dataframe(transitions_df, use_container_width=True)
    
    render_section_divider()
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Configuration", use_container_width=True):
            st.session_state[SS_STAGE] = 1
            st.rerun()
    
    with col2:
        if st.button("🔄 New Optimization", use_container_width=True):
            st.session_state[SS_STAGE] = 0
            st.session_state[SS_UPLOADED_FILE] = None
            st.session_state[SS_EXCEL_DATA] = None
            st.session_state[SS_SOLUTION] = None
            st.rerun()


# ========== MAIN APP ==========
def main():
    """Main application controller"""
    
    current_stage = st.session_state[SS_STAGE]
    
    if current_stage == 0:
        render_upload_stage()
    elif current_stage == 1:
        render_preview_stage()
    elif current_stage == 2:
        render_results_stage()


if __name__ == "__main__":
    main()
