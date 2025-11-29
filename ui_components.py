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

    /* ============================================================
    ORIGINAL THEME — UNCHANGED
    ============================================================ */

    .stApp { background: #f8fafc !important; }
    .main  { background: #f8fafc !important; }

    p, span, div, label, h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }

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
    .alert-success { border-left-color: #10b981; background: #f0fdf4; }
    .alert-info    { border-left-color: #3b82f6; background: #f0f9ff; }
    .alert-warning { border-left-color: #f59e0b; background: #fffbeb; }
    .alert-error   { border-left-color: #ef4444; background: #fef2f2; }

    /* (Tabs, progress bar, cards, etc. remain unchanged...) */

    /* ============================================================
    THEME FIX — COLORS ONLY (NO LAYOUT CHANGES)
    ============================================================ */

    /* Inputs */
    .stTextInput input,
    .stNumberInput input {
        border-color: #e2e8f0 !important;
        color: #1e293b !important;
        background: #ffffff !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus {
        border-color: #1e40af !important;
        box-shadow: 0 0 0 2px rgba(30,64,175,0.1) !important;
    }

    /* DataFrames */
    div[data-testid="stDataFrame"],
    div[data-testid="stDataFrameContainer"] {
        background: #ffffff !important;
        border-color: #e2e8f0 !important;
    }

    /* Uploader */
    .stFileUploader > div > div {
        border-color: #cbd5e1 !important;
        background: #ffffff !important;
    }
    .stFileUploader > div > div:hover {
        border-color: #1e40af !important;
        background: #f8fafc !important;
    }

    /* Download button style (color only) */
    .stDownloadButton > button {
        background: #1e40af !important;
        color: white !important;
    }
    .stDownloadButton > button:hover {
        background: #3730a3 !important;
        color: white !important;
    }

    /* ============================================================
    MATCH DOWNLOAD BUTTON HEIGHT TO UPLOADER
    ============================================================ */

    .stDownloadButton > button {
        height: 110px !important;          /* Same visual height as uploader */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
    }
    .stDownloadButton > button * {
        margin: 0 auto !important;
    }

</style>
        """,
        unsafe_allow_html=True
    )


def render_header(title: str, subtitle: str = ""):
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
        if idx < current_stage:
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
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        f"""
        <div class="card">
            <div class="card-header">{icon_html}{title}</div>
        """,
        unsafe_allow_html=True,
    )


def close_card():
    st.markdown("</div>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, col):
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
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_download_template_button():
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


# ------------------------------------------------------------
# NEW: ALIGN UPLOADER + DOWNLOAD BUTTON IN A ROW
# ------------------------------------------------------------
def render_upload_and_template_row(upload_label="Upload File"):
    """Render uploader on the left and download-template button on the right."""

    col1, col2 = st.columns([1, 1])

    with col1:
        st.file_uploader(upload_label, type=["xlsx"])

    with col2:
        render_download_template_button()
