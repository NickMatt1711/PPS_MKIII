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

        /* ---------------------------
        GLOBAL
        ---------------------------*/
        .stApp, .main {
            background: #f8fafc !important;
        }
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: #1e293b !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        /* ---------------------------
        HEADER
        ---------------------------*/
        .app-header {
            background: linear-gradient(135deg, #1e40af, #3730a3);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            color: white !important;
            box-shadow: 0 4px 12px rgba(30,64,175,.15);
        }
        .app-header h1 { 
            color: white !important;
        }
        .app-header p { 
            color: rgba(255,255,255,.9) !important; 
        }

        /* ---------------------------
        STREAMLIT BUTTONS (Fix black buttons)
        ---------------------------*/
        button[kind="primary"], .stButton > button {
            background: #1e40af !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: .75rem 2rem !important;
            font-weight: 600 !important;
            box-shadow: 0 1px 3px rgba(30,64,175,.3);
        }
        button[kind="primary"]:hover, .stButton > button:hover {
            background: #3730a3 !important;
            box-shadow: 0 4px 12px rgba(30,64,175,.4);
        }

        /* ---------------------------
        FILE UPLOADER (Fix black)
        ---------------------------*/
        div[data-testid="stFileUploader-dropzone"] {
            border: 2px dashed #28a745 !important;
            background: #f8fff9 !important;
            border-radius: 10px !important;
            color: #1e293b !important;
        }
        div[data-testid="stFileUploader-dropzone"] * {
            color: #1e293b !important;
        }

        /* ---------------------------
        DOWNLOAD TEMPLATE BUTTON FIX
        ---------------------------*/
        a[data-testid="stDownloadButton"] > button {
            background: #1e40af !important;
            color: white !important;
            border-radius: 8px !important;
            padding: .65rem 1.5rem !important;
            font-weight: 600 !important;
        }
        a[data-testid="stDownloadButton"] > button:hover {
            background: #3730a3 !important;
        }

        /* ---------------------------
        DATAFRAME FIX (Remove dark mode)
        ---------------------------*/
        div[data-testid="stDataFrame"] table {
            background: white !important;
            color: #1e293b !important;
            border-radius: 8px !important;
        }
        div[data-testid="stDataFrame"] th {
            background: #f1f5f9 !important;
            color: #1e293b !important;
        }
        div[data-testid="stDataFrame"] td {
            background: white !important;
            color: #1e293b !important;
        }

        /* ---------------------------
        INPUT FIELDS (Fix grey/black)
        ---------------------------*/
        input[type="number"], input[type="text"], textarea {
            background: white !important;
            color: #1e293b !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
            padding: .65rem !important;
            font-weight: 500 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,.05);
        }
        input[type="number"]:focus, input[type="text"]:focus, textarea:focus {
            border-color: #657eea !important;
            box-shadow: 0 0 0 3px rgba(102,126,234,.2) !important;
        }

        label {
            color: #1e293b !important;
            font-weight: 600 !important;
        }

        /* ---------------------------
        STAGE CIRCLES
        ---------------------------*/
        .stage-circle.active {
            background: #1e40af !important;
            color: white !important;
            border-color: #1e40af !important;
        }
        .stage-circle.completed {
            background: #10b981 !important;
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
