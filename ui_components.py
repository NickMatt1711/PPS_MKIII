"""
UI Components Module
====================

Reusable Streamlit components matching test(1).py UI style.
"""

import streamlit as st
from typing import Tuple

import constants


def inject_custom_css() -> None:
    """Inject modern Material Design CSS - matches test(1).py."""
    st.markdown("""
    <style>
        /* Hide sidebar completely */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        .main .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }
        
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Material Design App Bar */
        .app-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 2rem 3rem;
            margin: -3rem -3rem 3rem -3rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 16px;
        }
        
        .app-bar h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        .app-bar p {
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            opacity: 0.95;
            font-weight: 400;
        }
        
        /* Material Cards */
        .material-card {
            background: #F0F2FF;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            padding: 2rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(0, 0, 0, 0.06);
        }
        
        .material-card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            text-align: center;
            color: #212121;
            margin: 0 0 1rem 0;
        }
        
        /* Metrics */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border-left: 4px solid;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }
        
        .metric-card.primary {
            border-left-color: #667eea;
            background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
        }
        
        .metric-card.success {
            border-left-color: #4caf50;
            background: linear-gradient(135deg, #f1f8f4 0%, #ffffff 100%);
        }
        
        .metric-card.warning {
            border-left-color: #ff9800;
            background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%
        }
        
        .metric-card.info {
            border-left-color: #2196f3;
            background: linear-gradient(135deg, #f0f7ff 0%, #ffffff 100%);
        }
        
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
            line-height: 1.2;
        }
        
        .metric-subtitle {
            font-size: 0.75rem;
            color: #9e9e9e;
            margin-top: 0.25rem;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stButton > button:hover {
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
            transform: translateY(-2px);
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
            border: 2px dashed #667eea;
            border-radius: 16px;
            padding: 1rem 1rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #764ba2;
            background: linear-gradient(135deg, #f0f4ff 0%, #e3e9f7 100%);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: white;
            padding: 0.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            display: flex;
            width: 100%;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            background: transparent;
            border: none;
            color: #757575;
            transition: all 0.3s ease;
            flex: 1;
            text-align: center;
            justify-content: center;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Alert boxes */
        .alert-box {
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        
        .alert-box.info {
            background: #e3f2fd;
            border-left-color: #2196f3;
            color: #1565c0;
        }
        
        .alert-box.success {
            background: #e8f5e9;
            border-left-color: #4caf50;
            color: #2e7d32;
        }
        
        .alert-box.warning {
            background: #fff3e0;
            border-left-color: #ff9800;
            color: #e65100;
        }
        
        /* Divider */
        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
            margin: 2rem 0;
        }
        
        /* Number input */
        .stNumberInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .stNumberInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Styled list */
        .styled-list {
            list-style: none;
            padding-left: 0;
        }
        
        .styled-list li {
            padding: 0.5rem 0 0.5rem 2rem;
            position: relative;
        }
        
        .styled-list li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #4caf50;
            font-weight: bold;
            font-size: 1.25rem;
        }
    </style>
    """, unsafe_allow_html=True)


def render_header() -> None:
    """Render the application header."""
    st.markdown("""
    <div class="app-bar">
        <h1>🏭 Polymer Production Scheduler</h1>
        <p>Optimized Multi-Plant Production Planning</p>
    </div>
    """, unsafe_allow_html=True)


def render_divider() -> None:
    """Render a styled divider."""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def render_summary_metrics(objective: float, transitions: int, stockouts: float, planning_days: int) -> None:
    """Render summary metrics in a grid layout."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card primary">
            <div class="metric-label">Objective Value</div>
            <div class="metric-value">{objective:,.0f}</div>
            <div class="metric-subtitle">Lower is Better</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card info">
            <div class="metric-label">Transitions</div>
            <div class="metric-value">{transitions}</div>
            <div class="metric-subtitle">Grade Changeovers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        card_type = "success" if stockouts == 0 else "warning"
        st.markdown(f"""
        <div class="metric-card {card_type}">
            <div class="metric-label">Stockouts</div>
            <div class="metric-value">{stockouts:,.0f}</div>
            <div class="metric-subtitle">MT Unmet Demand</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card info">
            <div class="metric-label">Planning Horizon</div>
            <div class="metric-value">{planning_days}</div>
            <div class="metric-subtitle">Days</div>
        </div>
        """, unsafe_allow_html=True)


def render_optimization_status(status: str, runtime: float) -> None:
    """Render optimization status with appropriate styling."""
    if status == "OPTIMAL":
        st.markdown(f'<div class="alert-box success">✅ Optimal solution found in {runtime:.1f} seconds!</div>', unsafe_allow_html=True)
    elif status == "FEASIBLE":
        st.markdown(f'<div class="alert-box success">✅ Feasible solution found in {runtime:.1f} seconds!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-box warning">⚠️ Solver status: {status} (runtime: {runtime:.1f}s)</div>', unsafe_allow_html=True)


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
        
        ### Recommended Actions
        
        1. Review and relax constraint parameters
        2. Check for data entry errors in Excel file
        3. Validate demand forecasts against capacity
        4. Consider increasing buffer days for flexibility
        """)


def render_footer() -> None:
    """Render application footer."""
    render_divider()
    st.markdown("""
    <div style="text-align: center; color: #9e9e9e; font-size: 0.875rem; padding: 1rem 0;">
        <strong>Polymer Production Scheduler</strong> • Powered by OR-Tools & Streamlit<br>
        Material Minimalism Design • Version 3.0
    </div>
    """, unsafe_allow_html=True)
