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

def render_sidebar_inputs(default_transition=10, default_stockout=10, default_timelimit=10, default_buffer=3):
    """
    Enhanced sidebar with min inventory penalty controls
    """
    st.sidebar.header("⚙️ Solver Parameters")
    
    # Original parameters
    transition_penalty = st.sidebar.slider(
        "Transition Penalty",
        min_value=1,
        max_value=20,
        value=default_transition,
        help="Cost penalty for changing grades on a production line"
    )
    
    stockout_penalty = st.sidebar.slider(
        "Stockout Penalty", 
        min_value=1,
        max_value=20,
        value=default_stockout,
        help="Cost penalty per unit of unmet demand"
    )
    
    # NEW: Min inventory penalty parameters
    min_inv_penalty = st.sidebar.slider(
        "Min Inventory Violation Penalty",
        min_value=1,
        max_value=15,
        value=5,
        help="Cost penalty per unit below minimum inventory level"
    )
    
    min_closing_penalty = st.sidebar.slider(
        "Min Closing Inventory Penalty",
        min_value=1,
        max_value=20,
        value=8,
        help="Cost penalty per unit below minimum closing inventory"
    )
    
    time_limit = st.sidebar.slider(
        "Time Limit (minutes)",
        min_value=1,
        max_value=30,
        value=default_timelimit
    )
    
    buffer_days = st.sidebar.slider(
        "Buffer Days",
        min_value=0,
        max_value=7,
        value=default_buffer,
        help="Days at end of period excluded from high/low inventory calculations"
    )
    
    return transition_penalty, stockout_penalty, time_limit, buffer_days, min_inv_penalty, min_closing_penalty

# Simple function for run button message
def render_run_button_message():
    st.info("Click the 'Run Optimization' button to start the enhanced solver with inventory penalties and rerun constraints.")
