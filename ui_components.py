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
        COLOR VARIABLES - Single Source of Truth
        ------------------------------------*/
        :root {
            /* Primary Colors */
            --primary-500: #1e40af;
            --primary-600: #3730a3;
            --primary-100: #eff6ff;
            
            /* Semantic Colors */
            --success-500: #10b981;
            --success-100: #d1fae5;
            --info-500: #1e40af;
            --info-100: #eff6ff;
            --warning-500: #f59e0b;
            --warning-100: #fffde7;
            --error-500: #ef4444;
            --error-100: #fee2e2;
            
            /* Neutral Colors */
            --background: #f8fafc;
            --surface: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #4b5563;
            --text-muted: #64748b;
            --border-light: #e5e7eb;
            --border-medium: #d1d5db;
            --border-muted: #9ca3af;
            
            /* Component Colors */
            --inactive-bg: #f3f4f6;
            --table-header: #f9fafb;
        }
        
        /* ------------------------------------
        GLOBAL BASE - Consolidated
        ------------------------------------*/
        .stApp, .main {
            background: var(--background) !important;
        }
        
        /* Typography - Single declaration */
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        /* ------------------------------------
        HEADER - Simplified
        ------------------------------------*/
        .app-header {
            background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
        }
        
        .app-header h1 {
            margin: 0;
            font-size: 2.5rem;
            color: white !important;
        }
        
        .app-header p {
            color: rgba(255, 255, 255, 0.9) !important;
            margin-top: 0.5rem;
        }
        
        /* ------------------------------------
        WIZARD / STAGE PROGRESS - Consolidated
        ------------------------------------*/
        .stage-container {
            padding: 1rem 0;
            margin-bottom: 2rem;
            background-color: var(--surface);
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .stage-row {
            display: flex;
            justify-content: space-around;
            align-items: flex-start;
            width: 100%;
        }
        
        .stage-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex-grow: 1; 
        }
        
        .stage-circle {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: 700;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
            border: 3px solid;
            z-index: 10;
        }
        
        .stage-label {
            font-size: 0.9rem;
            text-align: center;
            font-weight: 500;
            color: var(--text-secondary) !important;
        }
        
        /* Consolidated Status Classes */
        .stage-circle.inactive {
            background-color: var(--inactive-bg);
            color: var(--border-muted);
            border-color: var(--border-medium);
        }
        
        .stage-circle.active {
            background-color: var(--primary-500);
            color: white;
            border-color: var(--primary-500);
            box-shadow: 0 0 0 5px rgba(30, 64, 175, 0.2);
        }
        
        .stage-circle.completed {
            background-color: var(--success-500);
            color: white;
            border-color: var(--success-500);
        }
        
        .stage-label.active {
            font-weight: 700;
            color: var(--text-primary) !important;
        }
        
        .stage-connector {
            height: 4px; 
            background-color: var(--border-medium); 
            flex-grow: 1;
            margin: 0 -20px; 
            position: relative;
            top: 21.5px;
            z-index: 0;
        }
        
        .stage-connector.completed {
            background-color: var(--success-500); 
        }
        
        /* ------------------------------------
        CARDS & CONTAINERS - Unified
        ------------------------------------*/
        .card, .metric-card, .stTabs {
            background: var(--surface);
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-light);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .card-header {
            color: var(--text-primary) !important;
            border-bottom: 1px solid var(--border-light);
            padding-bottom: 0.75rem;
            margin-bottom: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        /* Consolidated Alert System */
        div[data-testid="stAlert"] {
            border-radius: 4px;
            box-shadow: none;
            border-left: 5px solid !important;
        }
        
        div[data-testid="stAlert"]:not([class*="alert-"]) {
            background-color: var(--info-100) !important;
            border-left-color: var(--info-500) !important;
        }
        
        .alert-success { 
            background-color: var(--success-100) !important; 
            border-left-color: var(--success-500) !important; 
        }
        .alert-info { 
            background-color: var(--info-100) !important; 
            border-left-color: var(--info-500) !important; 
        }
        .alert-warning { 
            background-color: var(--warning-100) !important; 
            border-left-color: var(--warning-500) !important; 
        }
        .alert-error { 
            background-color: var(--error-100) !important; 
            border-left-color: var(--error-500) !important; 
        }
        
        /* Alert text colors - simplified */
        .alert-success p, .alert-success strong { color: var(--success-500) !important; }
        .alert-info p, .alert-info strong { color: var(--info-500) !important; }
        .alert-warning p, .alert-warning strong { color: var(--warning-500) !important; }
        .alert-error p, .alert-error strong { color: var(--error-500) !important; }
        
        /* ------------------------------------
        BUTTONS - Consolidated
        ------------------------------------*/
        .stButton > button, 
        .stDownloadButton > button,
        section[data-testid="stFileUploader"] button {
            background: var(--primary-500) !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: none !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 3px rgba(30, 64, 175, 0.3) !important;
            padding: 0.5rem 1rem !important;
        }
        
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        section[data-testid="stFileUploader"] button:hover {
            background: var(--primary-600) !important;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4) !important;
            transform: translateY(-1px) !important;
        }
        
        /* ------------------------------------
        DATAFRAME & INPUTS - Consolidated
        ------------------------------------*/
        div[data-testid="stDataFrame"], 
        div[data-testid="stDataFrameContainer"] {
            background-color: var(--surface) !important; 
            border: 1px solid var(--border-light);
            border-radius: 4px;
            overflow: hidden; 
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        div[data-testid="stDataFrame"] th {
            background-color: var(--table-header) !important; 
            color: var(--text-primary) !important;
            font-weight: 600;
            border-color: var(--border-light) !important;
        }
        
        div[data-testid="stDataFrame"] td {
            color: var(--text-primary) !important;
            background-color: var(--surface) !important;
            border-color: var(--inactive-bg) !important;
        }
        
        /* Input Fields - Consolidated */
        .stTextInput input,
        .stTextInput textarea,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input {
            border: 1px solid var(--border-medium) !important;
            border-radius: 4px !important;
            color: var(--text-primary) !important; 
            background: var(--surface) !important;
            padding: 0.5rem 0.75rem !important;
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.05);
        }
        
        .stTextInput input:focus, 
        .stTextInput textarea:focus,
        .stNumberInput input:focus, 
        .stDateInput input:focus,
        .stTimeInput input:focus {
            border-color: var(--primary-500) !important;
            box-shadow: 0 0 0 2px rgba(30, 64, 175, 0.3) !important;
        }
        
        /* ------------------------------------
        FILE UPLOADER & TABS
        ------------------------------------*/
        section[data-testid="stFileUploader"] {
            border: 2px dashed var(--border-muted) !important; 
            border-radius: 8px !important;
            padding: 1.5rem !important;
            background-color: var(--surface) !important; 
        }
        
        button[data-baseweb="tab"] {
            color: var(--text-muted) !important; 
            background-color: transparent !important;
            font-weight: 500;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--primary-500) !important; 
            border-bottom: 3px solid var(--primary-500) !important; 
            font-weight: 600;
        }
        
        /* ------------------------------------
        METRICS & DIVIDERS
        ------------------------------------*/
        .metric-label {
            font-size: 0.9rem;
            color: var(--text-muted) !important;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary-500) !important;
            margin-top: 0.25rem;
        }
        
        .section-divider {
            margin: 2rem 0;
            border-top: 1px solid var(--border-light);
        }
        
        /* Ensure all nested button text uses white */
        .stButton > button * {
            color: white !important;
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
