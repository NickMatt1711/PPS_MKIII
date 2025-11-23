"""
Reusable UI components with modern material design
"""

import streamlit as st
from constants import THEME_COLORS


def apply_custom_css():
    """Apply custom CSS for modern material design - LIGHT MODE"""
    st.markdown(f"""
    <style>
        /* Global Styles - Light Mode */
        .main {{
            background-color: #FFFFFF;
        }}
        
        .stApp {{
            background-color: #F5F7FA;
        }}
        
        /* Header Styles */
        .app-header {{
            background: linear-gradient(135deg, {THEME_COLORS['primary']} 0%, #4A5FC1 100%);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 16px rgba(94, 124, 226, 0.2);
        }}
        
        .app-header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 600;
            letter-spacing: -0.5px;
        }}
        
        .app-header p {{
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            opacity: 0.95;
            font-weight: 400;
        }}
        
        /* Stage Progress Bar */
        .stage-container {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border: 1px solid {THEME_COLORS['border_light']};
        }}
        
        .stage-progress {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            margin-bottom: 1rem;
        }}
        
        .stage-step {{
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 2;
            flex: 1;
        }}
        
        .stage-circle {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
        }}
        
        .stage-circle.active {{
            background: {THEME_COLORS['primary']};
            color: white;
            box-shadow: 0 4px 12px rgba(94, 124, 226, 0.3);
        }}
        
        .stage-circle.completed {{
            background: {THEME_COLORS['success']};
            color: white;
        }}
        
        .stage-circle.inactive {{
            background: {THEME_COLORS['border_light']};
            color: {THEME_COLORS['text_secondary']};
        }}
        
        .stage-label {{
            font-size: 0.875rem;
            font-weight: 500;
            color: #374151 !important;  /* Force dark gray color */
        }}
        
        .stage-label.active {{
            color: {THEME_COLORS['primary']} !important;
            font-weight: 600;
        }}
        
        /* Card Styles */
        .card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            margin-bottom: 1.5rem;
            border: 1px solid {THEME_COLORS['border_light']};
        }}
        
        .card-header {{
            font-size: 1.25rem;
            font-weight: 600;
            color: {THEME_COLORS['text_primary']};
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* Metric Cards */
        .metric-card {{
            background: linear-gradient(135deg, {THEME_COLORS['primary']} 0%, #4A5FC1 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(94, 124, 226, 0.2);
            transition: transform 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(94, 124, 226, 0.3);
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Alert Boxes */
        .alert {{
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }}
        
        .alert-success {{
            background: {THEME_COLORS['success_light']};
            border-left: 4px solid {THEME_COLORS['success']};
            color: #2D5016;
        }}
        
        .alert-info {{
            background: {THEME_COLORS['primary_light']};
            border-left: 4px solid {THEME_COLORS['primary']};
            color: #1E3A8A;
        }}
        
        .alert-warning {{
            background: {THEME_COLORS['warning_light']};
            border-left: 4px solid {THEME_COLORS['warning']};
            color: #7C4A03;
        }}
        
        .alert-error {{
            background: {THEME_COLORS['error_light']};
            border-left: 4px solid {THEME_COLORS['error']};
            color: #7F1D1D;
        }}
        
        /* Buttons */
        .stButton>button {{
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease;
            background: {THEME_COLORS['primary']};
            color: white;
        }}
        
        .stButton>button:hover {{
            background: #4A5FC1;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(94, 124, 226, 0.3);
        }}
        
        /* DataFrames */
        .dataframe {{
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid {THEME_COLORS['border_light']} !important;
        }}
        
        /* File Uploader */
        .uploadedFile {{
            border: 2px dashed {THEME_COLORS['primary']} !important;
            border-radius: 12px !important;
            background: {THEME_COLORS['primary_light']} !important;
        }}
        
        /* Equal width tabs - FIX FOR DISTRIBUTED WIDTH */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: {THEME_COLORS['bg_light']};
            padding: 0.5rem;
            border-radius: 12px;
            display: flex;
            width: 100%;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            padding: 0 24px;
            background: white;
            border-radius: 8px;
            font-weight: 600;
            border: 2px solid transparent;
            color: {THEME_COLORS['text_regular']};
            flex: 1 1 0;
            min-width: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {THEME_COLORS['primary']};
            color: white;
        }}
        
        /* Progress Bar */
        .stProgress > div > div > div > div {{
            background: {THEME_COLORS['primary']};
        }}
        
        /* Section Divider */
        .section-divider {{
            height: 1px;
            background: {THEME_COLORS['border_light']};
            margin: 2rem 0;
        }}
        
        /* Optimization Animation Container */
        .optimization-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            margin: 2rem 0;
        }}
        
        .spinner {{
            border: 4px solid {THEME_COLORS['border_light']};
            border-top: 4px solid {THEME_COLORS['primary']};
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin-bottom: 1.5rem;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .optimization-text {{
            font-size: 1.25rem;
            font-weight: 600;
            color: {THEME_COLORS['text_primary']};
            margin-bottom: 0.5rem;
        }}
        
        .optimization-subtext {{
            font-size: 0.95rem;
            color: {THEME_COLORS['text_secondary']};
        }}
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = ""):
    """Render application header"""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
        <div class="app-header">
            <h1>{title}</h1>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)


def render_stage_progress(current_stage: int):
    """Render wizard stage progress indicator"""
    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"),
        ("3", "Results")
    ]
    
    circles_html = ""
    for idx, (num, label) in enumerate(stages):
        if idx < current_stage:
            status = "completed"
            icon = "✓"
        elif idx == current_stage:
            status = "active"
            icon = num
        else:
            status = "inactive"
            icon = num
        
        label_class = "active" if idx == current_stage else ""
        
        circles_html += f"""
            <div class="stage-step">
                <div class="stage-circle {status}">{icon}</div>
                <div class="stage-label {label_class}">{label}</div>
            </div>
        """
    
    st.markdown(f"""
        <div class="stage-container">
            <div class="stage-progress">
                {circles_html}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_card(title: str, icon: str = ""):
    """Context manager for card layout"""
    icon_html = f"{icon} " if icon else ""
    st.markdown(f"""
        <div class="card">
            <div class="card-header">{icon_html}{title}</div>
    """, unsafe_allow_html=True)


def close_card():
    """Close card div"""
    st.markdown("</div>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, col):
    """Render a metric card in a column"""
    with col:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)


def render_alert(message: str, alert_type: str = "info"):
    """Render an alert box"""
    icons = {
        'success': '✓',
        'info': 'ℹ',
        'warning': '⚠',
        'error': '✕'
    }
    icon = icons.get(alert_type, 'ℹ')
    
    st.markdown(f"""
        <div class="alert alert-{alert_type}">
            <span style="font-size: 1.25rem; font-weight: bold;">{icon}</span>
            <span>{message}</span>
        </div>
    """, unsafe_allow_html=True)


def render_section_divider():
    """Render a section divider"""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
