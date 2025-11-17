def render_header():
    inject_test1_css()
    header()

def render_sidebar_inputs(default_transition, default_stockout, default_timelimit, default_buffer):
    st.sidebar.header("⚙️ Optimization Parameters")
    
    transition_penalty = st.sidebar.number_input(
        "Transition Penalty",
        min_value=1,
        max_value=100,
        value=default_transition,
        help="Penalty for changing production between different grades"
    )
    
    stockout_penalty = st.sidebar.number_input(
        "Stockout Penalty", 
        min_value=1,
        max_value=100,
        value=default_stockout,
        help="Penalty for unmet demand"
    )
    
    time_limit = st.sidebar.number_input(
        "Time Limit (minutes)",
        min_value=1,
        max_value=60,
        value=default_timelimit,
        help="Maximum solver runtime in minutes"
    )
    
    buffer_days = st.sidebar.number_input(
        "Buffer Days",
        min_value=0,
        max_value=10,
        value=default_buffer,
        help="Days at end of horizon to exclude from inventory analysis"
    )
    
    return transition_penalty, stockout_penalty, time_limit, buffer_days

def render_run_button_message():
    st.markdown("---")
    st.info("👆 Click **'Run Optimization'** to generate the production schedule")
