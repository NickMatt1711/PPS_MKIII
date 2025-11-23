"""
Reusable UI components with modern material design and dark mode support
"""

import streamlit as st
from constants import THEME_COLORS

# Define color schemes for both modes
LIGHT_THEME = {
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F5F7FA',
    'bg_card': '#FFFFFF',
    'text_primary': '#1A1A1A',
    'text_secondary': '#666666',
    'text_regular': '#333333',
    'border_light': '#E0E0E0',
    'primary_light': '#E8EAF6',
    'success_light': '#E8F5E8',
    'warning_light': '#FFF3E0',
    'error_light': '#FFEBEE'
}

DARK_THEME = {
    'bg_primary': '#121212',
    'bg_secondary': '#1E1E1E',
    'bg_card': '#2D2D2D',
    'text_primary': '#FFFFFF',
    'text_secondary': '#CCCCCC',
    'text_regular': '#E0E0E0',
    'border_light': '#424242',
    'primary_light': '#2D3A6B',
    'success_light': '#1B3A1B',
    'warning_light': '#332A1A',
    'error_light': '#3F1A1D'
}

def init_theme():
    """Initialize theme in session state"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def toggle_theme():
    """Toggle between light and dark mode"""
    st.session_state.dark_mode = not st.session_state.dark_mode

def get_current_theme():
    """Get current theme colors based on mode"""
    base_colors = THEME_COLORS.copy()
    # Check if dark_mode exists in session state, default to False if not
    is_dark_mode = st.session_state.get('dark_mode', False)
    if is_dark_mode:
        base_colors.update(DARK_THEME)
    else:
        base_colors.update(LIGHT_THEME)
    return base_colors

def apply_custom_css():
    """Apply custom CSS for modern material design with dark mode support"""
    colors = get_current_theme()
    
    st.markdown(f"""
    <style>
        /* Global Styles */
        .main {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
        }}
        
        .stApp {{
            background-color: {colors['bg_secondary']};
        }}
        
        /* Text Colors */
        .stMarkdown, .stText, .stTitle, .stHeader {{
            color: {colors['text_primary']} !important;
        }}
        
        /* Header Styles */
        .app-header {{
            background: linear-gradient(135deg, {colors['primary']} 0%, #4A5FC1 100%);
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
            color: white;
        }}
        
        .app-header p {{
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            opacity: 0.95;
            font-weight: 400;
            color: white;
        }}
        
        /* Theme Toggle */
        .theme-toggle-container {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }}
        
        .theme-toggle {{
            background: {colors['bg_card']};
            border: 1px solid {colors['border_light']};
            border-radius: 20px;
            padding: 8px 16px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
            color: {colors['text_primary']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        /* Stage Progress Bar */
        .stage-container {{
            background: {colors['bg_card']};
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border: 1px solid {colors['border_light']};
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
            background: {colors['primary']};
            color: white;
            box-shadow: 0 4px 12px rgba(94, 124, 226, 0.3);
        }}
        
        .stage-circle.completed {{
            background: {colors['success']};
            color: white;
        }}
        
        .stage-circle.inactive {{
            background: {colors['border_light']};
            color: {colors['text_secondary']};
        }}
        
        .stage-label {{
            font-size: 0.875rem;
            font-weight: 500;
            color: {colors['text_regular']};
        }}
        
        .stage-label.active {{
            color: {colors['primary']};
            font-weight: 600;
        }}
        
        /* Card Styles */
        .card {{
            background: {colors['bg_card']};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            margin-bottom: 1.5rem;
            border: 1px solid {colors['border_light']};
        }}
        
        .card-header {{
            font-size: 1.25rem;
            font-weight: 600;
            color: {colors['text_primary']};
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* Metric Cards */
        .metric-card {{
            background: linear-gradient(135deg, {colors['primary']} 0%, #4A5FC1 100%);
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
            background: {colors['success_light']};
            border-left: 4px solid {colors['success']};
            color: {colors['text_primary']};
        }}
        
        .alert-info {{
            background: {colors['primary_light']};
            border-left: 4px solid {colors['primary']};
            color: {colors['text_primary']};
        }}
        
        .alert-warning {{
            background: {colors['warning_light']};
            border-left: 4px solid {colors['warning']};
            color: {colors['text_primary']};
        }}
        
        .alert-error {{
            background: {colors['error_light']};
            border-left: 4px solid {colors['error']};
            color: {colors['text_primary']};
        }}
        
        /* Buttons */
        .stButton>button {{
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease;
            background: {colors['primary']};
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
            border: 1px solid {colors['border_light']} !important;
            background: {colors['bg_card']} !important;
        }}
        
        /* Input Fields */
        .stTextInput>div>div>input {{
            background: {colors['bg_card']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_light']};
        }}
        
        .stNumberInput>div>div>input {{
            background: {colors['bg_card']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_light']};
        }}
        
        .stSelectbox>div>div {{
            background: {colors['bg_card']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_light']};
        }}
        
        /* File Uploader */
        .uploadedFile {{
            border: 2px dashed {colors['primary']} !important;
            border-radius: 12px !important;
            background: {colors['primary_light']} !important;
        }}
        
        /* Equal width tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: {colors['bg_light']};
            padding: 0.5rem;
            border-radius: 12px;
            display: flex;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            padding: 0 24px;
            background: {colors['bg_card']};
            border-radius: 8px;
            font-weight: 600;
            border: 2px solid transparent;
            color: {colors['text_regular']};
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {colors['primary']};
            color: white;
        }}
        
        /* Progress Bar */
        .stProgress > div > div > div > div {{
            background: {colors['primary']};
        }}
        
        /* Section Divider */
        .section-divider {{
            height: 1px;
            background: {colors['border_light']};
            margin: 2rem 0;
        }}
        
        /* Optimization Animation Container */
        .optimization-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            background: {colors['bg_card']};
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            margin: 2rem 0;
        }}
        
        .spinner {{
            border: 4px solid {colors['border_light']};
            border-top: 4px solid {colors['primary']};
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
            color: {colors['text_primary']};
            margin-bottom: 0.5rem;
        }}
        
        .optimization-subtext {{
            font-size: 0.95rem;
            color: {colors['text_secondary']};
        }}
    </style>
    """, unsafe_allow_html=True)

def render_theme_toggle():
    """Render theme toggle button"""
    is_dark_mode = st.session_state.get('dark_mode', False)
    theme_icon = "🌙" if is_dark_mode else "☀️"
    theme_text = "Dark" if is_dark_mode else "Light"
    
    st.markdown(f"""
        <div class="theme-toggle-container">
            <div class="theme-toggle" onclick="this.parentElement.querySelector('button').click()">
                <span>{theme_icon}</span>
                <span>{theme_text}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Invisible button for click handling
    if st.button("Toggle Theme", key="theme_toggle", help="Switch between light and dark mode"):
        toggle_theme()
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

def render_loading_animation(message: str = "Processing..."):
    """Render a loading animation"""
    st.markdown(f"""
        <div class="optimization-container">
            <div class="spinner"></div>
            <div class="optimization-text">{message}</div>
            <div class="optimization-subtext">Please wait while we process your request</div>
        </div>
    """, unsafe_allow_html=True)
