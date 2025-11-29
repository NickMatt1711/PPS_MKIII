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
        GLOBAL BASE - Material 3 Light
        ------------------------------------*/
        .stApp {
            background: #f8fafc !important;
        }
        
        .main {
            background: #f8fafc !important;
        }

        /* Material 3 Typography - Force light text */
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: #1e293b !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        /* ------------------------------------
        HEADER - Corporate Gradient
        ------------------------------------*/
        .app-header {
            background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
            padding: 2.5rem 2rem;
            color: white !important;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
        }
        
        .app-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            color: white !important;
            letter-spacing: -0.025em;
        }
        
        .app-header p {
            margin: 0.75rem 0 0 0;
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500;
        }

        /* ------------------------------------
        CARDS - Material 3 Elevation
        ------------------------------------*/
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
        }
        
        .card-header {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1e293b !important;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }

        /* ------------------------------------
        METRIC CARDS - Subtle Colors
        ------------------------------------*/
        .metric-card {
            padding: 1.5rem 1rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
            background: white;
            border: 1px solid #e2e8f0;
        }
        
        .metric-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1e293b !important;
            margin: 0.5rem 0;
        }

        .metric-label {
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            color: #64748b !important;
            letter-spacing: 0.05em;
        }

        /* ------------------------------------
        ALERT BOXES - Material 3
        ------------------------------------*/
        .alert {
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            border-left: 4px solid;
            font-weight: 500;
            background: white;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .alert-success {
            border-left-color: #10b981;
            background: #f0fdf4;
        }

        .alert-info {
            border-left-color: #3b82f6;
            background: #f0f9ff;
        }

        .alert-warning {
            border-left-color: #f59e0b;
            background: #fffbeb;
        }

        .alert-error {
            border-left-color: #ef4444;
            background: #fef2f2;
        }

        /* ------------------------------------
        TABS - Fixed Text Colors
        ------------------------------------*/
        .stTabs [data-baseweb="tab-list"] {
            background: white;
            padding: 0.5rem;
            border-radius: 12px;
            gap: 0.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            background: transparent;
            padding: 0.75rem 1rem;
            font-weight: 600;
            color: #64748b !important;
            transition: all 0.2s ease;
            flex: 1;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: #f1f5f9;
            color: #1e293b !important;
        }

        /* Active tabs - white text with colored backgrounds */
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            font-weight: 700;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] * {
            color: white !important;
        }

        /* Tab colors */
        .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {
            background: #1e40af !important;
        }

        .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {
            background: #059669 !important;
        }

        .stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] {
            background: #7c3aed !important;
        }

        .stTabs [data-baseweb="tab"]:nth-child(4)[aria-selected="true"] {
            background: #ea580c !important;
        }

        /* ------------------------------------
        BUTTONS - Material 3 Filled
        ------------------------------------*/
        .stButton > button {
            background: #1e40af !important;
            color: white !important;
            padding: 0.75rem 2rem;
            font-weight: 600 !important;
            border-radius: 8px;
            border: none !important;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(30, 64, 175, 0.3);
        }
        
        .stButton > button:hover {
            background: #3730a3 !important;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4);
            transform: translateY(-1px);
        }

        .stButton > button p,
        .stButton > button span,
        .stButton > button div {
            color: white !important;
            font-weight: 600 !important;
        }

        /* ------------------------------------
        FILE UPLOADER - Theme Colors
        ------------------------------------*/
        section[data-testid="stFileUploader"] {
            border: 2px dashed #1e40af !important;
            border-radius: 8px !important;
            padding: 2rem !important;
            background-color: #f8fafc !important;
        }

        section[data-testid="stFileUploader"] * {
            color: #1e293b !important;
        }

        section[data-testid="stFileUploader"] button {
            background: #1e40af !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
        }

        section[data-testid="stFileUploader"] button:hover {
            background: #3730a3 !important;
            color: white !important;
        }

        section[data-testid="stFileUploader"] button p,
        section[data-testid="stFileUploader"] button span {
            color: white !important;
            font-weight: 600 !important;
        }

        /* ------------------------------------
        DATAFRAMES & TABLES - Light Theme
        ------------------------------------*/
        .stDataFrame, 
        div[data-testid="stDataFrame"], 
        div[data-testid="stDataFrameContainer"],
        .dataframe {
            background: white !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            color: #1e293b !important;
        }

        .stDataFrame *,
        div[data-testid="stDataFrame"] *,
        div[data-testid="stDataFrameContainer"] * {
            color: #1e293b !important;
            background: white !important;
        }

        /* Table headers */
        .stDataFrame thead th,
        div[data-testid="stDataFrame"] thead th {
            background: #f1f5f9 !important;
            color: #1e293b !important;
            font-weight: 600 !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }

        /* Table cells */
        .stDataFrame tbody td,
        div[data-testid="stDataFrame"] tbody td {
            background: white !important;
            color: #1e293b !important;
            border-bottom: 1px solid #f1f5f9 !important;
        }

        /* ------------------------------------
        INPUT FIELDS - Light Theme
        ------------------------------------*/
        .stNumberInput > div > div > input,
        .stNumberInput input,
        .stTextInput > div > div > input,
        .stTextInput input,
        .stSelectbox > div > div,
        .stTextArea > div > div > textarea {
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            color: #1e293b !important;
            background: white !important;
            padding: 0.75rem !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        }

        .stNumberInput > div > div > input:focus,
        .stNumberInput input:focus,
        .stTextInput > div > div > input:focus,
        .stTextInput input:focus,
        .stSelectbox > div > div:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #1e40af !important;
            box-shadow: 0 0 0 2px rgba(30, 64, 175, 0.2) !important;
            background: white !important;
        }

        /* Input labels */
        .stNumberInput label,
        .stTextInput label,
        .stSelectbox label,
        .stTextArea label {
            color: #1e293b !important;
            font-weight: 600 !important;
        }

        /* Number input buttons */
        .stNumberInput button {
            background: white !important;
            color: #1e293b !important;
            border: 1px solid #e2e8f0 !important;
        }

        .stNumberInput button:hover {
            background: #f1f5f9 !important;
            border-color: #1e40af !important;
        }

        /* ------------------------------------
        RADIO BUTTONS & CHECKBOXES
        ------------------------------------*/
        .stRadio > div,
        .stCheckbox > div {
            background: white !important;
            color: #1e293b !important;
            border-radius: 8px !important;
            padding: 0.5rem !important;
        }

        .stRadio label,
        .stCheckbox label {
            color: #1e293b !important;
            font-weight: 500 !important;
        }

        /* ------------------------------------
        TEXT ELEMENTS - Force light colors
        ------------------------------------*/
        /* Force all text to be visible */
        .stMarkdown, .stText, .stLabel, .stSubheader {
            color: #1e293b !important;
        }

        /* Section headers */
        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 600 !important;
        }

        /* ------------------------------------
        DOWNLOAD BUTTON - Theme Colors
        ------------------------------------*/
        .stDownloadButton > button {
            background: #1e40af !important;
            color: white !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: none !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 3px rgba(30, 64, 175, 0.3) !important;
        }
        
        .stDownloadButton > button:hover {
            background: #3730a3 !important;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4) !important;
            transform: translateY(-1px) !important;
            color: white !important;
        }

        .stDownloadButton > button p,
        .stDownloadButton > button span,
        .stDownloadButton > button div {
            color: white !important;
            font-weight: 600 !important;
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

    blocks = []
    connectors = []
    
    for idx, (num, label) in enumerate(stages):
        if idx < current_stage or (idx == total - 1 and current_stage >= total - 1):
            status = "completed"
            icon = "✓"
        elif idx == current_stage:
            status = "active" 
            icon = num
        else:
            status = "inactive"
            icon = num

        blocks.append(
            f"""
            <div class="stage-step">
                <div class="stage-circle {status}">{icon}</div>
                <div class="stage-label {'active' if idx == current_stage else ''}">
                    {label}
                </div>
            </div>
            """
        )
        
        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            connectors.append(f'<div class="stage-connector {connector_class}"></div>')

    html = ""
    for i, block in enumerate(blocks):
        html += block
        if i < len(connectors):
            html += connectors[i]

    st.markdown(
        f"""
        <div class="stage-container">
            <div class="stage-row">{html}</div>
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
        st.error(f"Error loading template: {e}")
