"""
Reusable UI components with modern material design
"""

import streamlit as st
from constants import THEME_COLORS, SS_THEME


def apply_custom_css(is_dark_mode=False):
    """Apply custom CSS for modern material design with theme support"""
    
    # Theme-specific colors - IMPROVED AESTHETICS
    if is_dark_mode:
        bg_main = "#0D1117"
        bg_app = "#161B22"
        text_primary = "#E6EDF3"
        text_secondary = "#8B949E"
        card_bg = "#1C2128"
        border_color = "#30363D"
        tab_bg = "#21262D"
        primary_color = "#58A6FF"
        primary_gradient = "linear-gradient(135deg, #58A6FF 0%, #1F6FEB 100%)"
    else:
        bg_main = "#FFFFFF"
        bg_app = "#F6F8FA"
        text_primary = "#24292F"
        text_secondary = "#57606A"
        card_bg = "#FFFFFF"
        border_color = "#D0D7DE"
        tab_bg = "#F6F8FA"
        primary_color = "#0969DA"
        primary_gradient = "linear-gradient(135deg, #0969DA 0%, #033D8B 100%)"
    
    st.markdown(f"""
    <style>
        /* Global Styles - Theme Aware */
        .main {{
            background-color: {bg_main};
            color: {text_primary};
        }}
        
        .stApp {{
            background-color: {bg_app};
        }}
        
        /* Override Streamlit defaults for theme */
        .stMarkdown, p, span, div {{
            color: {text_primary} !important;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {text_primary} !important;
        }}
        
        /* Header Styles */
        .app-header {{
            background: {primary_gradient};
            color: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(9, 105, 218, 0.25);
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
            background: {card_bg};
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border: 1px solid {border_color};
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
            background: {primary_color};
            color: white;
            box-shadow: 0 4px 12px rgba(9, 105, 218, 0.35);
        }}
        
        .stage-circle.completed {{
            background: #1A7F37;
            color: white;
        }}
        
        .stage-circle.inactive {{
            background: {border_color};
            color: {text_secondary};
        }}
        
        .stage-label {{
            font-size: 0.875rem;
            font-weight: 500;
            color: {text_secondary} !important;
        }}
        
        .stage-label.active {{
            color: {primary_color} !important;
            font-weight: 600;
        }}
        
        /* Card Styles */
        .card {{
            background: {card_bg};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            margin-bottom: 1.5rem;
            border: 1px solid {border_color};
        }}
        
        .card-header {{
            font-size: 1.25rem;
            font-weight: 600;
            color: {text_primary} !important;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* Metric Cards */
        .metric-card {{
            background: {primary_gradient};
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(9, 105, 218, 0.25);
            transition: transform 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(9, 105, 218, 0.35);
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
            border-left: 4px solid #1A7F37;
            color: #0E4429;
        }}
        
        .alert-info {{
            background: {THEME_COLORS['primary_light']};
            border-left: 4px solid {primary_color};
            color: #0550AE;
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
            background: {primary_color};
            color: white;
        }}
        
        .stButton>button:hover {{
            background: #0550AE;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(9, 105, 218, 0.35);
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
            background: {tab_bg};
            padding: 0.5rem;
            border-radius: 12px;
            display: flex;
            width: 100%;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            padding: 0 24px;
            background: {card_bg};
            border-radius: 8px;
            font-weight: 600;
            border: 2px solid {border_color};
            color: {text_secondary};
            flex: 1 1 0;
            min-width: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {primary_color};
            color: white;
            border-color: {primary_color};
        }}
        
        /* Progress Bar */
        .stProgress > div > div > div > div {{
            background: {primary_color};
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
            background: {card_bg};
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            margin: 2rem 0;
        }}
        
        .spinner {{
            border: 4px solid {border_color};
            border-top: 4px solid {primary_color};
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
            color: {text_primary} !important;
            margin-bottom: 0.5rem;
        }}
        
        .optimization-subtext {{
            font-size: 0.95rem;
            color: {text_secondary} !important;
        }}
        
        /* Theme Toggle Button */
        .theme-toggle {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            background: {THEME_COLORS['primary']};
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}
        
        .theme-toggle:hover {{
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
    </style>
    """, unsafe_allow_html=True)


def render_theme_toggle():
    """Render theme toggle button"""
    # Initialize theme in session state
    if SS_THEME not in st.session_state:
        st.session_state[SS_THEME] = "light"
    
    # Create toggle in main area (top right corner)
    current_theme = st.session_state[SS_THEME]
    
    # Add button using columns to position it
    col1, col2 = st.columns([6, 1])
    with col2:
        button_label = "🌙 Dark" if current_theme == "light" else "☀️ Light"
        if st.button(button_label, key="theme_toggle", use_container_width=True):
            st.session_state[SS_THEME] = "dark" if current_theme == "light" else "light"
            st.rerun()


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
        'success': '✔',
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
