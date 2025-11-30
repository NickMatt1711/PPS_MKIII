"""
Material 3 Light Theme - Corporate UI Components
Clean, professional design without sidebar
"""

import streamlit as st
from constants import THEME_COLORS

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
        WIZARD PROGRESS - HORIZONTAL LAYOUT
        ------------------------------------*/
        .stage-container {
            background: var(--md-sys-color-surface);
            border-radius: var(--md-shape-corner-medium);
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--md-elevation-1);
        }
        
        .stage-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .stage-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 2;
            flex: 0 0 auto;
        }
        
        .stage-circle {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 500;
            font-size: 1.125rem;
            border: 2px solid;
            background: var(--md-sys-color-surface);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .stage-label {
            font-size: 0.875rem;
            font-weight: 500;
            margin-top: 0.75rem;
            text-align: center;
            color: var(--md-sys-color-on-surface-variant);
            white-space: nowrap;
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
            box-shadow: 0 0 0 8px rgba(103, 80, 164, 0.12);
            transform: scale(1.05);
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
            top: 24px;
            height: 2px;
            background: var(--md-sys-color-outline-variant);
            z-index: 1;
            transition: background 0.3s ease;
        }
        
        .stage-connector.completed {
            background: var(--md-sys-color-success);
        }
        
        /* Connector positioning between steps */
        .stage-step:nth-child(1) ~ .stage-connector:nth-of-type(1) {
            left: calc(25% - 24px);
            width: calc(25% - 48px);
        }
        
        .stage-step:nth-child(3) ~ .stage-connector:nth-of-type(2) {
            left: calc(50% + 24px);
            width: calc(25% - 48px);
        }
        
        /* ------------------------------------
        CARDS & CONTAINERS
        ------------------------------------*/
        .card, .metric-card {
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
        section[data-testid="stFileUploader"] button:hover,
        div[data-testid="stBaseButton-secondary"] > button:hover {
            background: #5643A3 !important;
            box-shadow: var(--md-elevation-2) !important;
            transform: translateY(-1px) !important;
        }
        
        .stButton > button:active,
        .stDownloadButton > button:active {
            transform: translateY(0) !important;
            box-shadow: var(--md-elevation-1) !important;
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
        
        div[data-testid="stAlert"] {
            background: var(--md-sys-color-primary-container) !important;
            color: var(--md-sys-color-on-primary-container) !important;
        }
        
        .alert-success {
            background: var(--md-sys-color-success-container) !important;
            color: #0D652D !important;
        }
        
        .alert-info {
            background: var(--md-sys-color-primary-container) !important;
            color: var(--md-sys-color-on-primary-container) !important;
        }
        
        .alert-warning {
            background: var(--md-sys-color-warning-container) !important;
            color: #7C5800 !important;
        }
        
        .alert-error {
            background: var(--md-sys-color-error-container) !important;
            color: var(--md-sys-color-error) !important;
        }
        
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] strong {
            color: inherit !important;
            margin: 0 !important;
        }
        
        /* ------------------------------------
        DATAFRAMES - LIGHT THEME OVERRIDES
        ------------------------------------*/
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrameResizable"],
        .stDataFrame,
        .dataframe {
            background: var(--md-sys-color-surface) !important;
            border-radius: var(--md-shape-corner-small) !important;
            border: 1px solid var(--md-sys-color-outline-variant) !important;
            box-shadow: var(--md-elevation-1) !important;
            overflow: hidden !important;
        }
        
        /* Force light background on all dataframe elements */
        div[data-testid="stDataFrame"] *,
        div[data-testid="stDataFrameResizable"] *,
        .stDataFrame *,
        .dataframe * {
            background: var(--md-sys-color-surface) !important;
            color: var(--md-sys-color-on-surface) !important;
        }
        
        /* Table headers */
        div[data-testid="stDataFrame"] thead,
        div[data-testid="stDataFrame"] th,
        .dataframe thead,
        .dataframe th {
            background: var(--md-sys-color-surface-variant) !important;
            color: var(--md-sys-color-on-surface-variant) !important;
            font-weight: 500 !important;
            border-bottom: 1px solid var(--md-sys-color-outline-variant) !important;
            padding: 0.75rem !important;
        }
        
        /* Table cells */
        div[data-testid="stDataFrame"] tbody,
        div[data-testid="stDataFrame"] td,
        .dataframe tbody,
        .dataframe td {
            background: var(--md-sys-color-surface) !important;
            color: var(--md-sys-color-on-surface) !important;
            border-bottom: 1px solid var(--md-sys-color-outline-variant) !important;
            padding: 0.75rem !important;
        }
        
        /* Hover effect */
        div[data-testid="stDataFrame"] tr:hover,
        div[data-testid="stDataFrame"] tr:hover td,
        .dataframe tr:hover,
        .dataframe tr:hover td {
            background: rgba(103, 80, 164, 0.08) !important;
        }
        
        /* Striped rows */
        div[data-testid="stDataFrame"] tbody tr:nth-child(even),
        div[data-testid="stDataFrame"] tbody tr:nth-child(even) td,
        .dataframe tbody tr:nth-child(even),
        .dataframe tbody tr:nth-child(even) td {
            background: rgba(103, 80, 164, 0.03) !important;
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
        FILE UPLOADER - LIGHT THEME
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
            background: rgba(103, 80, 164, 0.05) !important;
        }
        
        /* File uploader text */
        section[data-testid="stFileUploader"] label,
        section[data-testid="stFileUploader"] span,
        section[data-testid="stFileUploader"] p,
        section[data-testid="stFileUploader"] small {
            color: var(--md-sys-color-on-surface-variant) !important;
        }
        
        /* File uploader button styling */
        section[data-testid="stFileUploader"] button {
            margin-top: 1rem !important;
            background: var(--md-sys-color-primary) !important;
            color: var(--md-sys-color-on-primary) !important;
        }
        
        /* Uploaded file display */
        section[data-testid="stFileUploader"] > div:last-child {
            background: var(--md-sys-color-surface) !important;
            border: 1px solid var(--md-sys-color-outline-variant) !important;
            border-radius: var(--md-shape-corner-small) !important;
            padding: 0.5rem 1rem !important;
            margin-top: 1rem !important;
        }
        
        /* ------------------------------------
        TABS - FULL WIDTH DISTRIBUTION
        ------------------------------------*/
        .stTabs {
            background: var(--md-sys-color-surface) !important;
            padding: 0 !important;
            box-shadow: var(--md-elevation-1) !important;
            border-radius: var(--md-shape-corner-medium) !important;
            overflow: hidden !important;
        }
        
        /* Tab list container - distribute tabs evenly */
        div[data-baseweb="tab-list"] {
            display: flex !important;
            width: 100% !important;
            background: var(--md-sys-color-surface) !important;
            border-bottom: 1px solid var(--md-sys-color-outline-variant) !important;
        }
        
        /* Individual tabs - equal width distribution */
        button[data-baseweb="tab"] {
            flex: 1 !important;
            background: transparent !important;
            color: var(--md-sys-color-on-surface-variant) !important;
            font-weight: 500 !important;
            padding: 1rem 1.5rem !important;
            border-bottom: 3px solid transparent !important;
            transition: all 0.2s ease !important;
            text-align: center !important;
            justify-content: center !important;
        }
        
        button[data-baseweb="tab"]:hover {
            background: rgba(103, 80, 164, 0.05) !important;
            color: var(--md-sys-color-on-surface) !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--md-sys-color-primary) !important;
            border-bottom-color: var(--md-sys-color-primary) !important;
            background: rgba(103, 80, 164, 0.08) !important;
            font-weight: 600 !important;
        }
        
        /* Tab panel content */
        div[data-baseweb="tab-panel"] {
            padding: 1.5rem !important;
            background: var(--md-sys-color-surface) !important;
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
        
        /* Force light theme text colors */
        .stApp *:not(button):not(button *):not(.app-header):not(.app-header *) {
            color: var(--md-sys-color-on-surface) !important;
        }
        
        /* Ensure markdown and text elements are light */
        .stMarkdown, .stMarkdown *, p, span, div {
            color: var(--md-sys-color-on-surface) !important;
        }
        
        /* Progress bar styling */
        .stProgress > div > div {
            background-color: var(--md-sys-color-primary) !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: var(--md-sys-color-surface) !important;
            color: var(--md-sys-color-on-surface) !important;
            border: 1px solid var(--md-sys-color-outline-variant) !important;
            border-radius: var(--md-shape-corner-small) !important;
        }
        
        .streamlit-expanderContent {
            background: var(--md-sys-color-surface) !important;
            border: 1px solid var(--md-sys-color-outline-variant) !important;
            border-top: none !important;
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
    """Render horizontal stage progress indicator."""
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
        html += f'<div class="stage-circle {status}">{icon}</div>'
        html += f'<div class="stage-label {"active" if idx == current_stage else ""}">{label}</div>'
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
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_download_template_button():
    """Render download template button."""
    import io
    from pathlib import Path
    
    try:
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
