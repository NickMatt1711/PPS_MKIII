# ui_components.py
import streamlit as st

def inject_test1_css():
    st.markdown("""
    <style>
    .app-bar { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color: white; text-align:center; padding:1.4rem; border-radius:12px; }
    .metric-card { background:white; border-radius:12px; padding:1rem; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
    [data-testid="stFileUploader"] { background: linear-gradient(135deg,#f5f7fa 0%,#e8eef5 100%); border-radius:12px; padding:1rem; border:2px dashed #667eea; }
    .chip { display:inline-block; padding:0.3rem 0.6rem; border-radius:12px; font-weight:600; }
    </style>
    """, unsafe_allow_html=True)

def header():
    st.markdown("""
    <div class="app-bar">
        <h1>🏭 Polymer Production Scheduler</h1>
        <p style="margin-top:0.3rem; opacity:0.95;">Optimized Multi-Plant Production Planning</p>
    </div>
    """, unsafe_allow_html=True)

def footer():
    st.markdown("""
    <div style="text-align:center; color:#9e9e9e; font-size:0.9rem; padding:1rem 0;">
        <strong>Polymer Production Scheduler</strong> • Powered by OR-Tools & Streamlit
    </div>
    """, unsafe_allow_html=True)

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
