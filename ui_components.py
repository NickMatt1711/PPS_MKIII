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

        /* Primary Gradient for this app */
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --primary-color: #667eea;
            --primary-color-dark: #764ba2;
        }

        /* ------------------------------------
        HEADER - Corporate Gradient (Matching requested style)
        ------------------------------------*/
        .app-header {
            background: var(--primary-gradient);
            padding: 2.5rem 2rem;
            color: white !important;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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
        METRIC CARDS - Gradient (Matching requested style)
        ------------------------------------*/
        .metric-card {
            background: var(--primary-gradient);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: white !important; /* Changed to white */
            margin: 0.5rem 0;
        }

        .metric-label {
            font-size: 0.9rem; /* Slightly larger */
            font-weight: 500;
            text-transform: uppercase;
            color: rgba(255, 255, 255, 0.9) !important; /* Adjusted for contrast */
            letter-spacing: 1px;
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
            /* Matches requested success-box gradient */
            border-left-color: #155724; 
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            color: #155724 !important;
        }

        .alert-info {
            /* Matches requested info-box gradient */
            border-left-color: #0c5460; 
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            color: #0c5460 !important;
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
        TABS - Matching requested style
        ------------------------------------*/
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            box-shadow: none !important;
            border: none !important;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0 24px;
            background-color: white;
            border-radius: 8px;
            font-weight: 600;
            border: 2px solid transparent;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
            color: #1e293b !important;
        }
        .stTabs [aria-selected="true"] {
            background: var(--primary-gradient) !important;
            color: white !important;
            border-color: var(--primary-color) !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #f0f0f0;
            color: #1e293b !important;
        }
        .stTabs [aria-selected="true"]:hover {
            background: var(--primary-gradient) !important;
            color: white !important;
        }

        /* ------------------------------------
        BUTTONS - Gradient Filled (Matching requested style)
        ------------------------------------*/
        .stButton > button {
            background: var(--primary-gradient) !important;
            color: white !important;
            padding: 0.75rem 2rem;
            font-weight: 600 !important;
            border-radius: 8px;
            border: none !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
        }

        .stButton > button p,
        .stButton > button span,
        .stButton > button div {
            color: white !important;
            font-weight: 600 !important;
        }
        
        /* ------------------------------------
        STAGE PROGRESS - Clean Steps
        ------------------------------------*/
        .stage-container {
            padding: 2rem 1.5rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            border: 1px solid #e2e8f0;
        }

        .stage-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
        }

        .stage-step {
            flex: 0 0 auto;
            text-align: center;
            min-width: 100px;
        }

        .stage-connector {
            flex: 0 0 60px;
            height: 2px;
            background: #e2e8f0;
            border-radius: 1px;
        }

        .stage-connector.completed {
            background: var(--primary-color);
        }

        .stage-circle {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1rem;
            margin: 0 auto 0.5rem auto;
            transition: all 0.2s ease;
            border: 2px solid;
        }

        .stage-circle.active {
            background: var(--primary-color);
            color: white !important;
            border-color: var(--primary-color);
        }

        .stage-circle.completed {
            background: #10b981; /* Keep standard success green */
            color: white !important;
            border-color: #10b981;
        }

        .stage-circle.inactive {
            background: #f8fafc;
            color: #94a3b8 !important;
            border-color: #e2e8f0;
        }

        .stage-label {
            font-size: 0.875rem;
            color: #64748b !important;
            font-weight: 500;
        }

        .stage-label.active {
            color: var(--primary-color) !important;
            font-weight: 600;
        }

        /* ------------------------------------
        SECTION DIVIDER
        ------------------------------------*/
        .section-divider {
            height: 1px;
            background: #e2e8f0;
            margin: 2rem 0;
            border: none;
        }
        
        /* ------------------------------------
        DATAFRAME STYLING - Matching requested style
        ------------------------------------*/
        /* Target all dataframes */
        div[data-testid="stDataFrame"], 
        div[data-testid="stDataFrameContainer"],
        .stDataFrame {
            background: white !important;
            border: 1px solid #e9ecef !important; /* Lighter border */
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important; /* Requested shadow */
            overflow: hidden !important;
        }

        /* Table headers */
        .stDataFrame thead tr th {
            background: #f8fafc !important;
            color: #1e293b !important;
            font-weight: 600 !important;
            border-bottom: 1px solid #e2e8f0 !important;
            padding: 12px !important;
        }

        /* Table cells */
        .stDataFrame tbody tr {
            background: white !important;
        }

        .stDataFrame tbody tr:nth-child(even) {
            background: #f8fafc !important;
        }

        .stDataFrame tbody tr:hover {
            background: #f1f5f9 !important;
        }

        .stDataFrame tbody td {
            color: #1e293b !important;
            font-weight: 500 !important;
            border-color: #e2e8f0 !important;
            padding: 10px !important;
        }

        /* Specific fix for index column */
        .stDataFrame tbody td:first-child {
            background: #f8fafc !important;
            font-weight: 600 !important;
        }

        /* ------------------------------------
        INPUT FIELDS - Material 3 (Matching requested style)
        ------------------------------------*/
        /* Target text and number inputs */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
            color: #1e293b !important;
            background: white !important;
            padding: 0.5rem 0.75rem !important;
            box-shadow: none !important;
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
        }
        
        /* Selectbox/Dropdown */
        .stSelectbox > div > button,
        .stMultiSelect > div > button {
             border: 1px solid #e2e8f0 !important;
             border-radius: 8px !important;
             font-weight: 500 !important;
             background: white !important;
             box-shadow: none !important;
             padding: 0.5rem 0.75rem !important;
        }


        /* ------------------------------------
        FILE UPLOADER - Matching requested style
        ------------------------------------*/
        /* Uploader container */
        .stFileUploader {
            /* Create a variable to reference the uploader height */
            --uploader-min-height: 100px; 
        }

        .stFileUploader > div:first-child > div:first-child {
            background: white !important;
            border: 2px dashed var(--primary-color) !important; /* Use primary color for dashed border */
            border-radius: 8px !important;
            padding: 2rem !important;
            min-height: var(--uploader-min-height); /* Set height */
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .stFileUploader > div:first-child > div:first-child:hover {
            border-color: var(--primary-color-dark) !important;
            background: #f5f8ff !important;
        }
        
        /* Uploaded file success box (the one with the checkmark) */
        .uploadedFile {
            border: 2px dashed #28a745 !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            background-color: #f8fff9 !important;
        }

        /* Uploader text */
        .stFileUploader label,
        .stFileUploader section,
        .stFileUploader small,
        .stFileUploader div {
            color: #1e293b !important;
            font-weight: 500 !important;
        }

        /* Uploader internal button (Browse files) */
        .stFileUploader button {
            background: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            margin-top: 1rem !important;
        }

        .stFileUploader button:hover {
            background: var(--primary-color-dark) !important;
            color: white !important;
        }

        /* ------------------------------------
        DOWNLOAD BUTTON - Fixed to match uploader height
        ------------------------------------*/
        /* Download button container (needed for height alignment) */
        .stDownloadButton {
            height: 100%;
            display: flex;
            align-items: center;
        }
        
        /* Download button styling - Use same gradient */
        .stDownloadButton > button {
            background: var(--primary-gradient) !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: none !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
            width: 100% !important;
            /* Match the inner padding of the uploader box */
            min-height: calc(var(--uploader-min-height) + 4rem); /* 4rem = top/bottom padding of uploader (2rem + 2rem) */
            display: flex; /* Flexbox for internal centering */
            flex-direction: column;
            justify-content: center;
        }

        .stDownloadButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
            color: white !important;
        }

        .stDownloadButton > button p,
        .stDownloadButton > button span,
        .stDownloadButton > button div {
            color: white !important;
            font-weight: 600 !important;
        }


        /* ------------------------------------
        TEXT ELEMENTS - Force light colors
        ------------------------------------*/
        /* Force all text to be visible */
        .stMarkdown, .stText, .stLabel, .stSubheader {
            color: #1e293b !important;
        }

        /* Input labels */
        .stNumberInput label, .stTextInput label, .stSelectbox label {
            color: #1e293b !important;
            font-weight: 600 !important;
        }

        /* Section headers */
        h1, h2, h3 {
            color: #0f172a !important;
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
