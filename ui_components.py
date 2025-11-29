"""
Material 3 Light Theme - FORCEFUL UI Components
Using direct style injections and higher specificity
"""

import streamlit as st

def apply_custom_css():
    """Apply Material 3 Light theme with aggressive overrides."""
    
    st.markdown(
        """
        <style>
        /* =============================================
        NUCLEAR OPTION - DIRECT STYLE INJECTIONS
        ============================================= */
        
        /* KILL ALL DARK THEME ELEMENTS */
        .stApp {
            background-color: #f8fafc !important;
            color: #1e293b !important;
        }
        
        .main {
            background-color: #f8fafc !important;
        }
        
        /* FORCE WHITE TEXT ON ALL BUTTONS */
        button {
            color: white !important;
        }
        
        button * {
            color: white !important;
        }
        
        .stButton > button {
            background: #6750A4 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
            box-shadow: 0 1px 3px rgba(103, 80, 164, 0.3) !important;
        }
        
        .stButton > button:hover {
            background: #5A4791 !important;
            box-shadow: 0 4px 12px rgba(103, 80, 164, 0.4) !important;
            transform: translateY(-1px) !important;
            color: white !important;
        }
        
        .stButton > button * {
            color: white !important;
        }
        
        /* DOWNLOAD BUTTONS - FORCE WHITE TEXT */
        .stDownloadButton > button,
        .stDownloadButton > a {
            background: #6750A4 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
            box-shadow: 0 1px 3px rgba(103, 80, 164, 0.3) !important;
        }
        
        .stDownloadButton > button:hover,
        .stDownloadButton > a:hover {
            background: #5A4791 !important;
            color: white !important;
        }
        
        .stDownloadButton > button *,
        .stDownloadButton > a * {
            color: white !important;
        }
        
        /* FILE UPLOADER - LIGHT THEME */
        section[data-testid="stFileUploader"] {
            background: white !important;
            border: 2px dashed #79747E !important;
            border-radius: 12px !important;
            padding: 2rem !important;
        }
        
        section[data-testid="stFileUploader"] * {
            color: #49454F !important;
        }
        
        section[data-testid="stFileUploader"] button {
            background: #6750A4 !important;
            color: white !important;
        }
        
        section[data-testid="stFileUploader"] button * {
            color: white !important;
        }
        
        /* DATAFRAMES - LIGHT THEME */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrameContainer"] {
            background: white !important;
            border: 1px solid #E7E0EC !important;
            border-radius: 8px !important;
        }
        
        div[data-testid="stDataFrame"] table {
            background: white !important;
            color: #1C1B1F !important;
        }
        
        div[data-testid="stDataFrame"] th {
            background: #E7E0EC !important;
            color: #49454F !important;
            font-weight: 500 !important;
        }
        
        div[data-testid="stDataFrame"] td {
            background: white !important;
            color: #1C1B1F !important;
        }
        
        div[data-testid="stDataFrame"] * {
            color: #1C1B1F !important;
        }
        
        /* HEADER STYLES */
        .app-header {
            background: #6750A4 !important;
            color: white !important;
            padding: 2rem 1.5rem !important;
            border-radius: 16px !important;
            margin: 1rem 0 2rem 0 !important;
            text-align: center !important;
        }
        
        .app-header h1 {
            color: white !important;
            margin: 0 !important;
            font-size: 2.25rem !important;
        }
        
        .app-header p {
            color: white !important;
            opacity: 0.9 !important;
        }
        
        /* PROGRESS INDICATOR */
        .stage-container {
            background: white !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin-bottom: 2rem !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        
        .stage-circle {
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            border: 2px solid !important;
        }
        
        .stage-circle.inactive {
            background: white !important;
            border-color: #C4C7C5 !important;
            color: #79747E !important;
        }
        
        .stage-circle.active {
            background: #6750A4 !important;
            border-color: #6750A4 !important;
            color: white !important;
        }
        
        .stage-circle.completed {
            background: #0D652D !important;
            border-color: #0D652D !important;
            color: white !important;
        }
        
        .stage-label {
            color: #49454F !important;
            font-size: 0.75rem !important;
        }
        
        .stage-label.active {
            color: #1C1B1F !important;
            font-weight: 600 !important;
        }
        
        /* CARDS AND CONTAINERS */
        .card, .metric-card {
            background: white !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        
        .metric-label {
            color: #49454F !important;
            font-size: 0.875rem !important;
        }
        
        .metric-value {
            color: #6750A4 !important;
            font-size: 2rem !important;
            font-weight: 600 !important;
        }
        
        /* ALERTS */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border: none !important;
            padding: 1rem 1.5rem !important;
        }
        
        .alert-success {
            background: #A7F0BA !important;
            color: #0D652D !important;
        }
        
        .alert-info {
            background: #EADDFF !important;
            color: #21005D !important;
        }
        
        .alert-warning {
            background: #FFDEA3 !important;
            color: #7C5800 !important;
        }
        
        .alert-error {
            background: #F9DEDC !important;
            color: #B3261E !important;
        }
        
        /* INPUT FIELDS */
        .stTextInput input,
        .stNumberInput input {
            background: white !important;
            border: 1px solid #79747E !important;
            border-radius: 8px !important;
            color: #1C1B1F !important;
            padding: 0.75rem 1rem !important;
        }
        
        /* TABS */
        .stTabs {
            background: white !important;
            border-radius: 12px !important;
        }
        
        button[data-baseweb="tab"] {
            color: #49454F !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #6750A4 !important;
            border-bottom-color: #6750A4 !important;
        }
        
        /* GLOBAL TEXT COLOR OVERRIDE */
        div:not(.app-header):not(button):not(.stButton):not(.stDownloadButton) {
            color: #1C1B1F !important;
        }
        
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: #1C1B1F !important;
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
    st.markdown('<div style="margin: 2rem 0; border-top: 1px solid #E7E0EC;"></div>', unsafe_allow_html=True)


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
