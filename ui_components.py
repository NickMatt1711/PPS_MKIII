"""
UI Components Module
====================

Reusable Streamlit components for consistent UI/UX throughout the application.
"""

import streamlit as st
from typing import Tuple, Dict, Any, Optional

import constants


def inject_custom_css() -> None:
    """Inject modern Material Design CSS styling."""
    st.markdown("""
    <style>
        /* Base styling */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .main .block-container {
            padding-top: 2rem;
            max-width: 1400px;
        }
        
        /* App header */
        .app-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .app-header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 600;
        }
        
        .app-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            opacity: 0.95;
        }
        
        /* Material cards */
        .material-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 1rem;
            border: 1px solid rgba(0,0,0,0.06);
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #212121;
            margin-bottom: 1rem;
        }
        
        /* Metrics */
        .metric-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid;
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }
        
        .metric-card.primary { border-left-color: #667eea; }
        .metric-card.success { border-left-color: #4caf50; }
        .metric-card.warning { border-left-color: #ff9800; }
        .metric-card.error { border-left-color: #f44336; }
        .metric-card.info { border-left-color: #2196f3; }
        
        .metric-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #757575;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #212121;
        }
        
        .metric-subtitle {
            font-size: 0.75rem;
            color: #9e9e9e;
            margin-top: 0.25rem;
        }
        
        /* Status badges */
        .status-badge {
            display: inline-block;
            padding: 0.375rem 0.875rem;
            border-radius: 16px;
            font-size: 0.8125rem;
            font-weight: 600;
            margin: 0.25rem;
        }
        
        .status-badge.success {
            background: #e8f5e9;
            color: #2e7d32;
        }
        
        .status-badge.warning {
            background: #fff3e0;
            color: #e65100;
        }
        
        .status-badge.info {
            background: #e3f2fd;
            color: #1565c0;
        }
        
        .status-badge.error {
            background: #ffebee;
            color: #c62828;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(102,126,234,0.3);
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stButton > button:hover {
            box-shadow: 0 4px 16px rgba(102,126,234,0.4);
            transform: translateY(-2px);
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
            border: 2px dashed #667eea;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #764ba2;
            box-shadow: 0 4px 16px rgba(102,126,234,0.15);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: white;
            padding: 0.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            color: #757575;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(102,126,234,0.3);
        }
        
        /* Divider */
        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
            margin: 2rem 0;
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: #f5f5f5;
            border-radius: 8px;
            font-weight: 600;
        }
        
        .streamlit-expanderHeader:hover {
            background: #eeeeee;
        }
    </style>
    """, unsafe_allow_html=True)


def render_header() -> None:
    """Render the application header."""
    st.markdown("""
    <div class="app-header">
        <h1>🏭 Polymer Production Scheduler</h1>
        <p>Optimized Multi-Plant Production Planning with Advanced Constraint Programming</p>
    </div>
    """, unsafe_allow_html=True)


def render_divider() -> None:
    """Render a styled divider."""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def render_metric_card(label: str, value: str, subtitle: str = "", 
                       card_type: str = "primary") -> None:
    """
    Render a metric card.
    
    Args:
        label: Metric label (e.g., "Total Production")
        value: Metric value (e.g., "1,250 MT")
        subtitle: Optional subtitle text
        card_type: One of "primary", "success", "warning", "error", "info"
    """
    subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ''
    
    st.markdown(f"""
    <div class="metric-card {card_type}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(text: str, badge_type: str = "info") -> None:
    """
    Render a status badge.
    
    Args:
        text: Badge text
        badge_type: One of "success", "warning", "info", "error"
    """
    st.markdown(
        f'<span class="status-badge {badge_type}">{text}</span>',
        unsafe_allow_html=True
    )


def render_sidebar_inputs(
    default_transition: int = constants.DEFAULT_TRANSITION_PENALTY,
    default_stockout: int = constants.DEFAULT_STOCKOUT_PENALTY,
    default_timelimit: int = constants.DEFAULT_TIME_LIMIT_MIN,
    default_buffer: int = constants.DEFAULT_BUFFER_DAYS,
) -> Tuple[int, int, int, int]:
    """
    Render sidebar parameter inputs.
    
    Returns:
        Tuple of (transition_penalty, stockout_penalty, time_limit, buffer_days)
    """
    with st.sidebar:
        st.markdown("## ⚙️ Optimization Parameters")
        
        st.markdown("### Core Settings")
        time_limit = st.number_input(
            "⏱️ Time Limit (minutes)",
            min_value=1,
            max_value=120,
            value=default_timelimit,
            help="Maximum solver runtime"
        )
        
        buffer_days = st.number_input(
            "📅 Planning Buffer (days)",
            min_value=0,
            max_value=14,
            value=default_buffer,
            help="Additional days for safety planning"
        )
        
        st.markdown("### Objective Weights")
        stockout_penalty = st.number_input(
            "🎯 Stockout Penalty",
            min_value=constants.MIN_STOCKOUT_PENALTY,
            max_value=constants.MAX_STOCKOUT_PENALTY,
            value=default_stockout,
            help="Cost weight for inventory shortages"
        )
        
        transition_penalty = st.number_input(
            "🔄 Transition Penalty",
            min_value=constants.MIN_TRANSITION_PENALTY,
            max_value=constants.MAX_TRANSITION_PENALTY,
            value=default_transition,
            help="Cost weight for grade changeovers"
        )
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.info(
            "**Higher penalties** → Solver avoids that behavior more\n\n"
            "**Stockout penalty**: Increase to prioritize meeting demand\n\n"
            "**Transition penalty**: Increase to reduce changeovers"
        )
    
    return transition_penalty, stockout_penalty, time_limit, buffer_days


def render_run_button_message() -> None:
    """Render message when waiting for optimization to run."""
    st.info(
        "👆 Click **Run Optimization** in the sidebar to solve the production schedule.\n\n"
        "The solver will find the optimal production plan considering all constraints."
    )


def render_loading_spinner(message: str = "Processing...") -> None:
    """Render a loading spinner with message."""
    return st.spinner(message)


def render_progress_bar(progress: int, message: str = "") -> None:
    """
    Render a progress bar.
    
    Args:
        progress: Progress percentage (0-100)
        message: Optional status message
    """
    progress_bar = st.progress(progress)
    if message:
        st.text(message)
    return progress_bar


def render_info_box(title: str, items: list) -> None:
    """
    Render an information box with list items.
    
    Args:
        title: Box title
        items: List of items to display
    """
    st.markdown(f"""
    <div class="material-card">
        <div class="card-title">{title}</div>
        <ul style="padding-left: 1.5rem; margin: 0;">
            {''.join([f'<li style="margin: 0.5rem 0;">{item}</li>' for item in items])}
        </ul>
    </div>
    """, unsafe_allow_html=True)


def render_feature_grid(features: Dict[str, str]) -> None:
    """
    Render a grid of feature cards.
    
    Args:
        features: Dict mapping feature name to description
    """
    st.markdown("""
    <div class="material-card">
        <div class="card-title">✨ Key Capabilities</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
    """, unsafe_allow_html=True)
    
    for name, desc in features.items():
        st.markdown(f"""
            <div>
                <div style="font-weight: 600; color: #667eea; margin-bottom: 0.5rem;">{name}</div>
                <div style="font-size: 0.875rem; color: #757575;">{desc}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_summary_metrics(
    objective: float,
    transitions: int,
    stockouts: float,
    planning_days: int
) -> None:
    """
    Render summary metrics in a grid layout.
    
    Args:
        objective: Objective function value
        transitions: Total number of grade transitions
        stockouts: Total stockout quantity
        planning_days: Number of planning days
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Objective Value",
            f"{objective:,.0f}",
            "Lower is Better",
            "primary"
        )
    
    with col2:
        render_metric_card(
            "Transitions",
            f"{transitions}",
            "Grade Changeovers",
            "info"
        )
    
    with col3:
        card_type = "success" if stockouts == 0 else "warning"
        render_metric_card(
            "Stockouts",
            f"{stockouts:,.0f}",
            "MT Unmet Demand",
            card_type
        )
    
    with col4:
        render_metric_card(
            "Planning Horizon",
            f"{planning_days}",
            "Days",
            "info"
        )


def render_optimization_status(status: str, time_elapsed: float) -> None:
    """
    Render optimization status with appropriate styling.
    
    Args:
        status: Solver status (OPTIMAL, FEASIBLE, etc.)
        time_elapsed: Solver runtime in seconds
    """
    if status == "OPTIMAL":
        st.success(f"✅ Optimal solution found in {time_elapsed:.1f} seconds!")
    elif status == "FEASIBLE":
        st.success(f"✅ Feasible solution found in {time_elapsed:.1f} seconds!")
    elif status == "INFEASIBLE":
        st.error("❌ No feasible solution exists with the given constraints")
    else:
        st.warning(f"⚠️ Solver status: {status} (runtime: {time_elapsed:.1f}s)")


def render_troubleshooting_guide() -> None:
    """Render troubleshooting guide for infeasible solutions."""
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
        
        #### 🔴 Transition Restrictions
        - **Problem**: Transition matrix too restrictive
        - **Solution**: Allow more grade changeover combinations
        
        #### 🔴 Force Start Date Conflicts
        - **Problem**: Cannot start grade on specified date
        - **Solution**: Adjust force start dates or relax other constraints
        
        ### Recommended Actions
        
        1. Review and relax constraint parameters in sidebar
        2. Check for data entry errors in Excel template
        3. Validate demand forecasts against capacity
        4. Consider increasing buffer days for flexibility
        5. Review transition matrices for overly restrictive rules
        """)


def render_footer() -> None:
    """Render application footer."""
    render_divider()
    st.markdown("""
    <div style="text-align: center; color: #9e9e9e; font-size: 0.875rem; padding: 1rem 0;">
        <strong>Polymer Production Scheduler v3.0</strong> • Powered by OR-Tools & Streamlit<br>
        Advanced Constraint Programming for Manufacturing Optimization
    </div>
    """, unsafe_allow_html=True)
