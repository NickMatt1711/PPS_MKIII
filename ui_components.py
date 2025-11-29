"""
Material 3 Light Theme - Corporate UI Components
Clean, professional design without sidebar
"""

import streamlit as st
from constants import THEME_COLORS # Re-introducing the original import

def apply_custom_css():
    """Apply Material 3 Light theme for corporate application."""
    
    st.markdown(
        """
       <style>
        /* ------------------------------------
        MATERIAL 3 LIGHT THEME - COMPLETE REFACTOR
        ------------------------------------*/
        :root {
            /* Material 3 Color Tokens - Light Theme */
            --md-sys-color-primary: #6750A4;
            --md-sys-color-on-primary: #FFFFFF;
            --md-sys-color-primary-container: #EADDFF;
            --md-sys-color-on-primary-container: #21005D;
            
            --md-sys-color-secondary: #625B71;
            --md-sys-color-on-secondary: #FFFFFF;
            --md-sys-color-secondary-container: #E8DEF8;
            --md-sys-color-on-secondary-container: #1D192B;
            
            --md-sys-color-tertiary: #7D5260;
            --md-sys-color-on-tertiary: #FFFFFF;
            --md-sys-color-tertiary-container: #FFD8E4;
            --md-sys-color-on-tertiary-container: #31111D;
            
            --md-sys-color-surface: #FFFBFE;
            --md-sys-color-on-surface: #1C1B1F;
            --md-sys-color-surface-variant: #E7E0EC;
            --md-sys-color-on-surface-variant: #49454F;
            
            --md-sys-color-background: #F8FAFC;
            --md-sys-color-on-background: #1C1B1F;
            
            --md-sys-color-outline: #79747E;
            --md-sys-color-outline-variant: #C4C7C5;
            
            /* Semantic Colors */
            --md-sys-color-error: #B3261E;
            --md-sys-color-on-error: #FFFFFF;
            --md-sys-color-error-container: #F9DEDC;
            
            --md-sys-color-success: #0D652D;
            --md-sys-color-on-success: #FFFFFF;
            --md-sys-color-success-container: #A7F0BA;
            
            --md-sys-color-warning: #7C5800;
            --md-sys-color-on-warning: #FFFFFF;
            --md-sys-color-warning-container: #FFDEA3;
            
            /* Elevation */
            --md-elevation-1: 0px 1px 3px 1px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.30);
            --md-elevation-2: 0px 2px 6px 2px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.30);
            --md-elevation-3: 0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px 0px rgba(0, 0, 0, 0.30);
            
            /* Border Radius */
            --md-shape-corner-extra-small: 4px;
            --md-shape-corner-small: 8px;
            --md-shape-corner-medium: 12px;
            --md-shape-corner-large: 16px;
        }
        
        /* ------------------------------------
        GLOBAL RESET & BASE STYLES
        ------------------------------------*/
        .stApp, .main, html, body {
            background: var(--md-sys-color-background) !important;
            font-family: 'Roboto', 'Segoe UI', system-ui, sans-serif;
        }
        
        * {
            color: var(--md-sys-color-on-background);
        }
        
        /* ------------------------------------
        HEADER - Material 3 Style
        ------------------------------------*/
        .app-header {
            background: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary) !important;
            padding: 2rem 1.5rem;
            border-radius: var(--md-shape-corner-large);
            margin: 1rem 0 2rem 0;
            box-shadow: var(--md-elevation-1);
            text-align: center;
        }
        
        .app-header h1 {
            margin: 0;
            font-size: 2.25rem;
            font-weight: 400;
            color: var(--md-sys-color-on-primary) !important;
            letter-spacing: 0.5px;
        }
        
        .app-header p {
            color: var(--md-sys-color-on-primary) !important;
            opacity: 0.9;
            margin-top: 0.5rem;
            font-size: 1.1rem;
        }
        
        /* ------------------------------------
        WIZARD PROGRESS - Material Design
        ------------------------------------*/
        .stage-container {
            background: var(--md-sys-color-surface);
            border-radius: var(--md-shape-corner-medium);
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--md-elevation-1);
        }
        
        .stage-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            position: relative;
        }
        
        .stage-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            position: relative;
            z-index: 2;
        }
        
        .stage-circle {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 500;
            font-size: 0.875rem;
            border: 2px solid;
            background: var(--md-sys-color-surface);
            transition: all 0.2s ease;
        }
        
        .stage-label {
            font-size: 0.75rem;
            font-weight: 500;
            margin-top: 0.5rem;
            text-align: center;
            color: var(--md-sys-color-on-surface-variant);
        }
        
        /* Stage States */
        .stage-circle.inactive {
            border-color: var(--md-sys-color-outline-variant);
            color: var(--md-sys-color-outline);
        }
        
        .stage-circle.active {
            background: var(--md-sys-color-primary);
            border-color: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary);
            box-shadow: 0 0 0 4px color-mix(in srgb, var(--md-sys-color-primary) 20%, transparent);
        }
        
        .stage-circle.completed {
            background: var(--md-sys-color-success);
            border-color: var(--md-sys-color-success);
            color: var(--md-sys-color-on-success);
        }
        
        .stage-label.active {
            color: var(--md-sys-color-on-surface);
            font-weight: 600;
        }
        
        .stage-connector {
            position: absolute;
            top: 15px;
            left: 50%;
            right: 50%;
            height: 2px;
            background: var(--md-sys-color-outline-variant);
            z-index: 1;
        }
        
        .stage-connector.completed {
            background: var(--md-sys-color-success);
        }
        
        /* ------------------------------------
        CARDS & CONTAINERS
        ------------------------------------*/
        .card, .metric-card, .stTabs {
            background: var(--md-sys-color-surface);
            border-radius: var(--md-shape-corner-medium);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--md-elevation-1);
            border: none;
        }
        
        .card-header {
            color: var(--md-sys-color-on-surface) !important;
            font-size: 1.25rem;
            font-weight: 500;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--md-sys-color-outline-variant);
        }
        
        /* ------------------------------------
        BUTTONS - Material 3 Filled Style
        ------------------------------------*/
        .stButton > button,
        .stDownloadButton > button,
        .stDownloadButton > a,
        section[data-testid="stFileUploader"] button,
        div[data-testid="stBaseButton-secondary"] > button {
            background: var(--md-sys-color-primary) !important;
            color: var(--md-sys-color-on-primary) !important;
            border: none !important;
            border-radius: var(--md-shape-corner-large) !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            text-transform: none !important;
            box-shadow: var(--md-elevation-1) !important;
            transition: all 0.2s ease !important;
            min-height: 40px !important;
        }
        
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stDownloadButton > a:hover,
        section[data-testid="stFileUploader"] button:hover,
        div[data-testid="stBaseButton-secondary"] > button:hover {
            background: color-mix(in srgb, var(--md-sys-color-primary) 85%, black) !important;
            box-shadow: var(--md-elevation-2) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Ensure download links look like buttons */
        .stDownloadButton > a {
            text-decoration: none !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        /* ------------------------------------
        ALERTS - Material 3 Style
        ------------------------------------*/
        div[data-testid="stAlert"] {
            border-radius: var(--md-shape-corner-medium) !important;
            border: none !important;
            box-shadow: var(--md-elevation-1) !important;
            padding: 1rem 1.5rem !important;
            margin: 1rem 0 !important;
        }
        
        /* Base alert (info) */
        div[data-testid="stAlert"]:not([class*="alert-"]) {
            background: var(--md-sys-color-primary-container) !important;
            color: var(--md-sys-color-on-primary-container) !important;
        }
        
        /* Semantic alerts */
        .alert-success {
            background: var(--md-sys-color-success-container) !important;
            color: var(--md-sys-color-on-success-container) !important;
        }
        
        .alert-info {
            background: var(--md-sys-color-primary-container) !important;
            color: var(--md-sys-color-on-primary-container) !important;
        }
        
        .alert-warning {
            background: var(--md-sys-color-warning-container) !important;
            color: var(--md-sys-color-on-warning-container) !important;
        }
        
        .alert-error {
            background: var(--md-sys-color-error-container) !important;
            color: var(--md-sys-color-on-error) !important;
        }
        
        /* Alert text */
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] strong {
            color: inherit !important;
            margin: 0 !important;
        }
        
        /* ------------------------------------
        DATAFRAMES - Light Theme
        ------------------------------------*/
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrameContainer"] {
            background: var(--md-sys-color-surface) !important;
            border-radius: var(--md-shape-corner-small) !important;
            border: 1px solid var(--md-sys-color-outline-variant) !important;
            box-shadow: var(--md-elevation-1) !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stDataFrame"] table {
            background: var(--md-sys-color-surface) !important;
        }
        
        div[data-testid="stDataFrame"] th {
            background: var(--md-sys-color-surface-variant) !important;
            color: var(--md-sys-color-on-surface-variant) !important;
            font-weight: 500 !important;
            border-bottom: 1px solid var(--md-sys-color-outline-variant) !important;
        }
        
        div[data-testid="stDataFrame"] td {
            background: var(--md-sys-color-surface) !important;
            color: var(--md-sys-color-on-surface) !important;
            border-bottom: 1px solid var(--md-sys-color-outline-variant) !important;
        }
        
        div[data-testid="stDataFrame"] tr:hover td {
            background: color-mix(in srgb, var(--md-sys-color-primary-container) 8%, transparent) !important;
        }
        
        /* ------------------------------------
        INPUT FIELDS - Material 3 Outlined
        ------------------------------------*/
        .stTextInput input,
        .stTextInput textarea,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input,
        .stSelectbox select {
            background: var(--md-sys-color-surface) !important;
            border: 1px solid var(--md-sys-color-outline) !important;
            border-radius: var(--md-shape-corner-small) !important;
            color: var(--md-sys-color-on-surface) !important;
            padding: 0.75rem 1rem !important;
            font-size: 1rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stTextInput input:focus,
        .stTextInput textarea:focus,
        .stNumberInput input:focus,
        .stDateInput input:focus,
        .stTimeInput input:focus,
        .stSelectbox select:focus {
            border-color: var(--md-sys-color-primary) !important;
            border-width: 2px !important;
            box-shadow: 0 0 0 1px var(--md-sys-color-primary) !important;
            outline: none !important;
        }
        
        /* ------------------------------------
        FILE UPLOADER - Material 3 Style
        ------------------------------------*/
        section[data-testid="stFileUploader"] {
            background: var(--md-sys-color-surface) !important;
            border: 2px dashed var(--md-sys-color-outline) !important;
            border-radius: var(--md-shape-corner-medium) !important;
            padding: 2rem !important;
            margin: 1rem 0 !important;
            transition: all 0.2s ease !important;
        }
        
        section[data-testid="stFileUploader"]:hover {
            border-color: var(--md-sys-color-primary) !important;
            background: color-mix(in srgb, var(--md-sys-color-primary-container) 5%, transparent) !important;
        }
        
        section[data-testid="stFileUploader"] * {
            color: var(--md-sys-color-on-surface-variant) !important;
        }
        
        section[data-testid="stFileUploader"] button {
            margin-top: 1rem !important;
        }
        
        /* ------------------------------------
        TABS - Material 3 Secondary
        ------------------------------------*/
        .stTabs {
            background: var(--md-sys-color-surface) !important;
            padding: 0 !important;
            box-shadow: var(--md-elevation-1) !important;
        }
        
        button[data-baseweb="tab"] {
            background: transparent !important;
            color: var(--md-sys-color-on-surface-variant) !important;
            font-weight: 500 !important;
            padding: 1rem 1.5rem !important;
            border-bottom: 2px solid transparent !important;
            transition: all 0.2s ease !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--md-sys-color-primary) !important;
            border-bottom-color: var(--md-sys-color-primary) !important;
            background: color-mix(in srgb, var(--md-sys-color-primary) 5%, transparent) !important;
        }
        
        /* ------------------------------------
        METRIC CARDS
        ------------------------------------*/
        .metric-card {
            background: var(--md-sys-color-surface);
            padding: 1.5rem;
            border-radius: var(--md-shape-corner-medium);
            box-shadow: var(--md-elevation-1);
            text-align: center;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: var(--md-sys-color-on-surface-variant);
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 600;
            color: var(--md-sys-color-primary);
            line-height: 1;
        }
        
        /* ------------------------------------
        UTILITY CLASSES
        ------------------------------------*/
        .section-divider {
            margin: 2rem 0;
            border: none;
            border-top: 1px solid var(--md-sys-color-outline-variant);
        }
        
        /* Ensure all text uses proper colors */
        .stApp *:not(button *):not(.app-header *) {
            color: var(--md-sys-color-on-surface) !important;
        }
        
        /* Fix for any Streamlit default dark styles */
        [data-testid]:not(div[data-testid="stDataFrame"]):not(div[data-testid="stDataFrameContainer"]) {
            color: var(--md-sys-color-on-surface) !important;
        }
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
    # The current stage should be 0, 1, or 2 for the three stages
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
        
        # Start Step Block
        html += '<div class="stage-step">'
        
        # Circle
        html += f"""
            <div class="stage-circle {status}">{icon}</div>
            <div class="stage-label {'active' if idx == current_stage else ''}">
                {label}
            </div>
        """
        html += '</div>' # End stage-step
        
        # Connector (Don't add after the last step)
        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            html += f'<div class="stage-connector {connector_class}"></div>'

    html += '</div>' # End stage-row

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
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_download_template_button():
    """Render download template button."""
    import io
    from pathlib import Path
    
    # Placeholder implementation, as the file isn't available in this environment.
    try:
        # NOTE: In a real environment, you would ensure 'polymer_production_template.xlsx' 
        # is available in the appropriate directory relative to this script.
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        
        if template_path.exists():
            with open(template_path, "rb") as f:
                template_data = f.read()
            
            st.download_button(
                label="📥 Download Template",
                data=template_data,
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download the Excel template file",
                use_container_width=True
            )
        else:
            st.error("Template file not found")
    except Exception as e:
        st.error(f"Template file not found: {e}")
