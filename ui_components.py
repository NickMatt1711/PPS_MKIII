"""
Material 3 Light Theme - Corporate UI Components
Clean, professional design without sidebar
"""

import streamlit as st
from constants import THEME_COLORS


def apply_custom_css():
    """Apply Material 3 Light theme with fully modular, maintainable CSS."""
    st.markdown(
        """
<style>

/* ============================================================
ROOT SYSTEM — Variables (Theme Constants)
============================================================ */
:root {
    --primary: #1e40af;
    --primary-hover: #3730a3;
    --success: #10b981;
    --warning: #f59e0b;
    --error:   #ef4444;
    --info:    #3b82f6;

    --text-dark: #1e293b;
    --text-medium: #64748b;
    --text-light: rgba(255,255,255,0.9);

    --bg-app: #f8fafc;
    --bg-card: #ffffff;
    --bg-muted: #f1f5f9;

    --border: #e2e8f0;
    --border-dashed: #cbd5e1;

    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 12px;

    --pad-sm: 0.5rem;
    --pad-md: 1rem;
    --pad-lg: 1.5rem;

    --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.15);
    --shadow-primary: 0 1px 3px rgba(30, 64, 175, 0.3);
}

/* ============================================================
GLOBAL
============================================================ */
.stApp, .main {
    background: var(--bg-app) !important;
}
p, span, div, label, h1, h2, h3, h4, h5, h6 {
    color: var(--text-dark) !important;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ============================================================
HEADER
============================================================ */
.app-header {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
    padding: 2.5rem 2rem;
    color: white !important;
    border-radius: var(--radius-lg);
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: var(--shadow-md);
}
.app-header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
}
.app-header p {
    margin-top: 0.75rem;
    font-size: 1.1rem;
    color: var(--text-light) !important;
}

/* ============================================================
CARDS
============================================================ */
.card {
    background: var(--bg-card);
    padding: var(--pad-lg);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-sm);
}
.card-header {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: var(--pad-md);
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--border);
}

/* ============================================================
METRIC CARDS
============================================================ */
.metric-card {
    padding: 1.5rem 1rem;
    text-align: center;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    background: var(--bg-card);
    box-shadow: var(--shadow-sm);
    transition: 0.2s ease;
}
.metric-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-dark) !important;
}
.metric-label {
    font-size: 0.875rem;
    text-transform: uppercase;
    color: var(--text-medium) !important;
    font-weight: 600;
}

/* ============================================================
ALERTS
============================================================ */
.alert {
    padding: 1rem 1.5rem;
    border-radius: var(--radius-md);
    margin-bottom: 1rem;
    display: flex; gap: 1rem; align-items: center;
    background: white;
    box-shadow: var(--shadow-sm);
    border-left: 4px solid;
}
.alert-success { border-left-color: var(--success); background: #f0fdf4; }
.alert-info    { border-left-color: var(--info);    background: #f0f9ff; }
.alert-warning { border-left-color: var(--warning); background: #fffbeb; }
.alert-error   { border-left-color: var(--error);   background: #fef2f2; }

/* ============================================================
TABS
============================================================ */
.stTabs [data-baseweb="tab-list"] {
    background: white;
    padding: 0.5rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    display: flex;
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    padding: 0.75rem 1rem;
    color: var(--text-medium) !important;
    border-radius: var(--radius-md);
    transition: 0.2s;
    text-align: center;
}
.stTabs [data-baseweb="tab"]:hover {
    background: var(--bg-muted);
}

/* Active colors rotate per tab index */
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: white !important;
    font-weight: 600;
}
.stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] { background: var(--primary) !important; }
.stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] { background: #059669 !important; }
.stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] { background: #7c3aed !important; }
.stTabs [data-baseweb="tab"]:nth-child(4)[aria-selected="true"] { background: #ea580c !important; }

/* ============================================================
BUTTONS — Primary + Download
============================================================ */
.stButton > button,
.stDownloadButton > button {
    background: var(--primary) !important;
    color: white !important;
    border-radius: var(--radius-md);
    border: none !important;
    font-weight: 600 !important;
    box-shadow: var(--shadow-primary);
    padding: 0.75rem 1.5rem !important;
    transition: 0.2s !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--primary-hover) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px);
}

/* Match uploader height */
.stDownloadButton > button {
    height: 96px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

/* ============================================================
INPUTS — Text + Number
============================================================ */
.stTextInput input,
.stNumberInput input {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.5rem 0.75rem !important;
    background: white !important;
    color: var(--text-dark) !important;
    font-weight: 500 !important;
}
.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(30,64,175,0.1) !important;
}

/* ============================================================
DATAFRAMES
============================================================ */
div[data-testid="stDataFrame"],
div[data-testid="stDataFrameContainer"] {
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}
.stDataFrame thead tr th {
    background: var(--bg-app) !important;
    font-weight: 600 !important;
}
.stDataFrame tbody tr:nth-child(even) {
    background: var(--bg-app) !important;
}

/* ============================================================
FILE UPLOADER
============================================================ */
.stFileUploader > div > div {
    background: white !important;
    border: 2px dashed var(--border-dashed) !important;
    padding: 2rem !important;
    border-radius: var(--radius-md) !important;
}
.stFileUploader > div > div:hover {
    border-color: var(--primary) !important;
    background: var(--bg-app) !important;
}
.stFileUploader button {
    background: var(--primary) !important;
    border-radius: var(--radius-md) !important;
}

/* ============================================================
STAGE PROGRESS
============================================================ */
.stage-container {
    padding: 2rem 1.5rem;
    background: white;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
}
.stage-circle.active {
    background: var(--primary);
    border-color: var(--primary);
    color: white !important;
}
.stage-circle.completed {
    background: var(--success);
    border-color: var(--success);
    color: white !important;
}

/* ============================================================
DIVIDER
============================================================ */
.section-divider {
    height: 1px;
    background: var(--border);
    margin: 2rem 0;
    border: none;
}

</style>
        """,
        unsafe_allow_html=True,
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
