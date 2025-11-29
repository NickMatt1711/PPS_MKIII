"""
Material 3 Corporate Theme - PROPERLY INTEGRATED UI Components
"""

import streamlit as st
from constants import THEME_COLORS  # Import the theme colors

def apply_custom_css():
    """Apply Material 3 Corporate theme with proper color integration."""
    
    st.markdown(
        f"""
        <style>
        /* =============================================
        MATERIAL 3 CORPORATE THEME - USING CONSTANTS
        ============================================= */
        
        /* CSS Variables from constants.py */
        :root {{
            /* Primary Colors */
            --md-primary: {THEME_COLORS['primary']} !important;
            --md-on-primary: {THEME_COLORS['on_primary']} !important;
            --md-primary-container: {THEME_COLORS['primary_container']} !important;
            
            /* Surface Colors */
            --md-surface: {THEME_COLORS['surface']} !important;
            --md-on-surface: {THEME_COLORS['on_surface']} !important;
            --md-surface-variant: {THEME_COLORS['surface_variant']} !important;
            --md-on-surface-variant: {THEME_COLORS['on_surface_variant']} !important;
            --md-background: {THEME_COLORS['background']} !important;
            --md-on-background: {THEME_COLORS['on_background']} !important;
            
            /* Semantic Colors */
            --md-error: {THEME_COLORS['error']} !important;
            --md-error-container: {THEME_COLORS['error_container']} !important;
            --md-success: {THEME_COLORS['success']} !important;
            --md-success-container: {THEME_COLORS['success_container']} !important;
            --md-warning: {THEME_COLORS['warning']} !important;
            --md-warning-container: {THEME_COLORS['warning_container']} !important;
            
            /* Border & Outline */
            --md-outline: {THEME_COLORS['outline']} !important;
            --md-outline-variant: {THEME_COLORS['outline_variant']} !important;
        }}

        /* =============================================
        GLOBAL OVERRIDES
        ============================================= */
        
        .stApp, .main, [data-testid="stAppViewContainer"] {{
            background-color: var(--md-background) !important;
            color: var(--md-on-background) !important;
        }}

        /* Force text colors */
        .stApp * {{
            color: var(--md-on-background) !important;
        }}

        /* =============================================
        HEADER STYLES
        ============================================= */
        .app-header {{
            background: var(--md-primary) !important;
            color: var(--md-on-primary) !important;
            padding: 2rem 1.5rem !important;
            border-radius: 16px !important;
            margin: 1rem 0 2rem 0 !important;
            box-shadow: 0 4px 12px rgba(94, 124, 226, 0.15) !important;
            text-align: center !important;
        }}
        
        .app-header h1 {{
            color: var(--md-on-primary) !important;
            margin: 0 !important;
            font-size: 2.25rem !important;
            font-weight: 400 !important;
        }}
        
        .app-header p {{
            color: var(--md-on-primary) !important;
            opacity: 0.9 !important;
        }}

        /* =============================================
        BUTTONS - WHITE TEXT ENFORCED
        ============================================= */
        
        /* ALL buttons */
        .stButton > button,
        .stDownloadButton > button,
        .stDownloadButton > a,
        section[data-testid="stFileUploader"] button,
        div[data-testid="stBaseButton-secondary"] > button {{
            background: var(--md-primary) !important;
            color: var(--md-on-primary) !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
            box-shadow: 0 1px 3px rgba(94, 124, 226, 0.3) !important;
            transition: all 0.2s ease !important;
        }}

        /* Force white text in button content */
        .stButton > button *,
        .stDownloadButton > button *,
        .stDownloadButton > a *,
        section[data-testid="stFileUploader"] button *,
        div[data-testid="stBaseButton-secondary"] > button * {{
            color: var(--md-on-primary) !important;
        }}

        /* Button hover states */
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stDownloadButton > a:hover,
        section[data-testid="stFileUploader"] button:hover,
        div[data-testid="stBaseButton-secondary"] > button:hover {{
            background: #4A67D6 !important; /* Darker blue */
            box-shadow: 0 4px 12px rgba(94, 124, 226, 0.4) !important;
            transform: translateY(-1px) !important;
            color: var(--md-on-primary) !important;
        }}

        /* =============================================
        FILE UPLOADER - LIGHT THEME
        ============================================= */
        section[data-testid="stFileUploader"] {{
            background: var(--md-surface) !important;
            border: 2px dashed var(--md-outline) !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            margin: 1rem 0 !important;
        }}
        
        section[data-testid="stFileUploader"]:hover {{
            border-color: var(--md-primary) !important;
            background: var(--md-primary-container) !important;
        }}
        
        section[data-testid="stFileUploader"] * {{
            color: var(--md-on-surface-variant) !important;
        }}

        /* =============================================
        DATAFRAMES - LIGHT THEME
        ============================================= */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrameContainer"] {{
            background: var(--md-surface) !important;
            border: 1px solid var(--md-outline-variant) !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        }}
        
        div[data-testid="stDataFrame"] th {{
            background: var(--md-surface-variant) !important;
            color: var(--md-on-surface-variant) !important;
            font-weight: 500 !important;
        }}
        
        div[data-testid="stDataFrame"] td {{
            background: var(--md-surface) !important;
            color: var(--md-on-surface) !important;
        }}

        /* =============================================
        PROGRESS INDICATOR
        ============================================= */
        .stage-container {{
            background: var(--md-surface) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin-bottom: 2rem !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        }}
        
        .stage-circle {{
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            border: 2px solid !important;
        }}
        
        .stage-circle.inactive {{
            background: var(--md-surface) !important;
            border-color: var(--md-outline-variant) !important;
            color: var(--md-on-surface-variant) !important;
        }}
        
        .stage-circle.active {{
            background: var(--md-primary) !important;
            border-color: var(--md-primary) !important;
            color: var(--md-on-primary) !important;
        }}
        
        .stage-circle.completed {{
            background: var(--md-success) !important;
            border-color: var(--md-success) !important;
            color: var(--md-on-primary) !important;
        }}
        
        .stage-label {{
            color: var(--md-on-surface-variant) !important;
            font-size: 0.75rem !important;
        }}
        
        .stage-label.active {{
            color: var(--md-on-surface) !important;
            font-weight: 600 !important;
        }}

        /* =============================================
        CARDS AND METRICS
        ============================================= */
        .card, .metric-card {{
            background: var(--md-surface) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        }}
        
        .metric-label {{
            color: var(--md-on-surface-variant) !important;
            font-size: 0.875rem !important;
        }}
        
        .metric-value {{
            color: var(--md-primary) !important;
            font-size: 2rem !important;
            font-weight: 600 !important;
        }}

        /* =============================================
        ALERTS
        ============================================= */
        div[data-testid="stAlert"] {{
            border-radius: 12px !important;
            border: none !important;
            padding: 1rem 1.5rem !important;
            margin: 1rem 0 !important;
        }}
        
        .alert-success {{
            background: var(--md-success-container) !important;
            color: var(--md-success) !important;
        }}
        
        .alert-info {{
            background: var(--md-primary-container) !important;
            color: var(--md-primary) !important;
        }}
        
        .alert-warning {{
            background: var(--md-warning-container) !important;
            color: var(--md-warning) !important;
        }}
        
        .alert-error {{
            background: var(--md-error-container) !important;
            color: var(--md-error) !important;
        }}

        /* =============================================
        INPUT FIELDS
        ============================================= */
        .stTextInput input,
        .stNumberInput input {{
            background: var(--md-surface) !important;
            border: 1px solid var(--md-outline) !important;
            border-radius: 8px !important;
            color: var(--md-on-surface) !important;
            padding: 0.75rem 1rem !important;
        }}

        /* =============================================
        TABS
        ============================================= */
        .stTabs {{
            background: var(--md-surface) !important;
            border-radius: 12px !important;
        }}
        
        button[data-baseweb="tab"] {{
            color: var(--md-on-surface-variant) !important;
        }}
        
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: var(--md-primary) !important;
            border-bottom-color: var(--md-primary) !important;
        }}

        </style>
        """, 
        unsafe_allow_html=True
    )


def render_header(title: str, subtitle: str = ""):
    """Render corporate app header."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{title}</h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stage_progress(current_stage: int) -> None:
    """Render clean stage progress indicator."""
    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"), 
        ("3", "Results")
    ]

    total = len(stages)
    current_stage = max(0, min(current_stage, total - 1))

    html = '<div class="stage-row">'
    
    for idx, (num, label) in enumerate(stages):
        status = "inactive"
        icon = num
        
        if idx == current_stage:
            status = "active"
        elif idx < current_stage:
            status = "completed"
            icon = "✓"
        
        html += '<div class="stage-step">'
        html += f"""
            <div class="stage-circle {status}">{icon}</div>
            <div class="stage-label {'active' if idx == current_stage else ''}">
                {label}
            </div>
        """
        html += '</div>'
        
        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            html += f'<div class="stage-connector {connector_class}"></div>'

    html += '</div>'

    st.markdown(
        f"""
        <div class="stage-container">
            {html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card(title: str, icon: str = ""):
    """Open a Material 3 card container."""
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        f"""
        <div class="card">
            <div class="card-header">{icon_html}{title}</div>
        """,
        unsafe_allow_html=True,
    )


def close_card():
    """Close the card container."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, col):
    """Render a Material 3 metric card."""
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_alert(message: str, alert_type: str = "info"):
    """Render a Material 3 alert box."""
    icons = {
        "success": "✓",
        "info": "ℹ", 
        "warning": "⚠",
        "error": "✕"
    }
    st.markdown(
        f"""
        <div class="alert alert-{alert_type}">
            <strong>{icons.get(alert_type, "ℹ")}</strong>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_divider():
    """Render a subtle divider."""
    st.markdown('<div style="margin: 2rem 0; border-top: 1px solid var(--md-outline-variant);"></div>', unsafe_allow_html=True)


def render_download_template_button():
    """Render download template button."""
    try:
        # Create placeholder template data
        template_data = b"Template file content"
        
        st.download_button(
            label="📥 Download Template",
            data=template_data,
            file_name="polymer_production_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the Excel template file",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Template download error: {e}")
