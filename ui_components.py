"""
UI components and styling for Polymer Production Scheduler.

This module provides:
- Modern Material Design styling
- Reusable Streamlit components
- Step indicators and progress tracking
- Responsive layouts
"""

import streamlit as st
from typing import Dict, Any, Tuple

from .constants import APP_TITLE, APP_SUBTITLE, STEP_LABELS


def inject_custom_css():
    """Inject modern Material Design CSS into Streamlit app."""
    st.markdown("""
    <style>
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
        
        .step-indicator {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 2rem 0 3rem 0;
            position: relative;
        }
        
        .step {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            flex: 1;
            max-width: 200px;
        }
        
        .step-circle {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1.125rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 2;
            background: white;
            border: 3px solid #e0e0e0;
            color: #9e9e9e;
        }
        
        .step-circle.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: #667eea;
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            transform: scale(1.1);
        }
        
        .step-circle.completed {
            background: #4caf50;
            border-color: #4caf50;
            color: white;
        }
        
        .step-label {
            margin-top: 0.75rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: #757575;
            text-align: center;
        }
        
        .step-label.active {
            color: #667eea;
            font-weight: 600;
        }
        
        .step-label.completed {
            color: #4caf50;
        }
        
        .step-line {
            position: absolute;
            top: 24px;
            left: 50%;
            right: -50%;
            height: 3px;
            background: #e0e0e0;
            z-index: 1;
        }
        
        .step-line.completed {
            background: #4caf50;
        }
        
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
            display: flex;
            align-items: center;
            justify-content: center; 
        }
        
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
            background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%);
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
        
        .chip {
            display: inline-flex;
            align-items: center;
            padding: 0.375rem 0.875rem;
            border-radius: 16px;
            font-size: 0.8125rem;
            font-weight: 500;
            margin: 0.25rem;
        }
        
        .chip.success {
            background: #e8f5e9;
            color: #2e7d32;
        }
        
        .chip.warning {
            background: #fff3e0;
            color: #e65100;
        }
        
        .chip.info {
            background: #e3f2fd;
            color: #1565c0;
        }
        
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
        
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }
        
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }
        
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
        
        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
            margin: 2rem 0;
        }
        
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


def render_header():
    """Render application header with title and subtitle."""
    st.markdown(f"""
    <div class="app-bar">
        <h1>{APP_TITLE}</h1>
        <p>{APP_SUBTITLE}</p>
    </div>
    """, unsafe_allow_html=True)


def render_step_indicator(current_step: int):
    """
    Render step indicator for multi-step workflow.
    
    Args:
        current_step: Current step number (1, 2, or 3)
    """
    step_status = [
        'active' if current_step == 1 else 'completed',
        'active' if current_step == 2 else ('completed' if current_step > 2 else ''),
        'active' if current_step == 3 else ''
    ]
    
    st.markdown(f"""
    <div class="step-indicator">
        <div class="step">
            <div class="step-circle {step_status[0]}">
                {'✓' if current_step > 1 else '1'}
            </div>
            <div class="step-label {step_status[0]}">{STEP_LABELS[1]}</div>
            <div class="step-line {step_status[0] if current_step > 1 else ''}"></div>
        </div>
        <div class="step">
            <div class="step-circle {step_status[1]}">
                {'✓' if current_step > 2 else '2'}
            </div>
            <div class="step-label {step_status[1]}">{STEP_LABELS[2]}</div>
            <div class="step-line {step_status[1] if current_step > 2 else ''}"></div>
        </div>
        <div class="step">
            <div class="step-circle {step_status[2]}">3</div>
            <div class="step-label {step_status[2]}">{STEP_LABELS[3]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, subtitle: str = "", card_type: str = "primary"):
    """
    Render a metric card.
    
    Args:
        label: Metric label
        value: Metric value (formatted)
        subtitle: Optional subtitle text
        card_type: Card style type (primary, success, warning, info)
    """
    subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ''
    
    return f"""
    <div class="metric-card {card_type}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {subtitle_html}
    </div>
    """


def render_material_card(title: str, content: str):
    """
    Render a material design card.
    
    Args:
        title: Card title
        content: Card content (HTML)
    """
    return f"""
    <div class="material-card">
        <div class="card-title">{title}</div>
        {content}
    </div>
    """


def render_chip(text: str, chip_type: str = "info"):
    """
    Render a chip/badge.
    
    Args:
        text: Chip text
        chip_type: Chip style (success, warning, info)
    """
    return f'<span class="chip {chip_type}">{text}</span>'


def render_alert(message: str, alert_type: str = "info"):
    """
    Render an alert box.
    
    Args:
        message: Alert message
        alert_type: Alert style (info, success, warning)
    """
    return f'<div class="alert-box {alert_type}">{message}</div>'


def render_divider():
    """Render a horizontal divider."""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def render_optimization_params_form() -> Dict[str, Any]:
    """
    Render optimization parameters form and return selected values.
    
    Returns:
        Dictionary with parameter values
    """
    st.markdown("""
    <div class="material-card">
        <div class="card-title">⚙️ Optimization Parameters</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Core Settings")
        time_limit_min = st.number_input(
            "⏱️ Time Limit (minutes)",
            min_value=1,
            max_value=120,
            value=10,
            help="Maximum solver runtime"
        )
        
        buffer_days = st.number_input(
            "📅 Planning Buffer (days)",
            min_value=0,
            max_value=7,
            value=3,
            help="Additional days for safety planning"
        )
    
    with col2:
        st.markdown("#### Objective Weights")
        stockout_penalty = st.number_input(
            "🎯 Stockout Penalty (per MT)",
            min_value=1,
            value=1000,
            help="Cost weight for inventory shortages - CRITICAL for sales"
        )
        
        transition_penalty = st.number_input(
            "🔄 Transition Penalty (per changeover)",
            min_value=1,
            value=100,
            help="Cost weight for grade changeovers - IMPORTANT for operations"
        )
    
    st.info("💡 **Business Priority**: Stockouts (sales impact) > Transitions (operations cost). Stockout penalty should typically be 5-10x higher than transition penalty.")
    
    return {
        'time_limit_min': time_limit_min,
        'buffer_days': buffer_days,
        'stockout_penalty': stockout_penalty,
        'transition_penalty': transition_penalty
    }


def render_footer():
    """Render application footer."""
    render_divider()
    st.markdown("""
    <div style="text-align: center; color: #9e9e9e; font-size: 0.875rem; padding: 1rem 0;">
        <strong>Polymer Production Scheduler</strong> • Powered by OR-Tools & Streamlit<br>
        Modern Architecture • Hierarchical Objectives • v3.0
    </div>
    """, unsafe_allow_html=True)
