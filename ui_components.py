"""
Material 3 Light Theme – Streamlit-Compatible (Refactored)
DOM selectors updated to current data-testid schema
Invalid / deprecated selectors removed
No deep-nesting CSS
No HTML invalid nesting
"""

import streamlit as st
from pathlib import Path


def apply_custom_css():
    st.markdown(
        """
        <style>

        /* APP BACKGROUND */
        [data-testid="stAppViewContainer"] {
            background: #f8fafc !important;
        }

        [data-testid="stHeader"] {
            background: none;
        }

        /* GLOBAL TYPOGRAPHY */
        html, body, [data-testid="stMarkdownContainer"] * {
            color: #1e293b !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        /* HEADER */
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
            margin-top: .75rem;
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500;
        }

        /* CARD */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
        }

        .card-header {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1e293b !important;
            padding-bottom: .5rem;
            border-bottom: 2px solid #e2e8f0;
        }

        /* METRIC CARD */
        .metric-card {
            padding: 1.2rem 1rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            background: white;
            border: 1px solid #e2e8f0;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1e293b !important;
            margin: .5rem 0;
        }

        .metric-label {
            font-size: .8rem;
            font-weight: 600;
            text-transform: uppercase;
            color: #64748b !important;
            letter-spacing: .05em;
        }

        /* ALERTS */
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
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .alert-success { border-left-color:#10b981; background:#f0fdf4; }
        .alert-info    { border-left-color:#3b82f6; background:#f0f9ff; }
        .alert-warning { border-left-color:#f59e0b; background:#fffbeb; }
        .alert-error   { border-left-color:#ef4444; background:#fef2f2; }

        /* DIVIDER */
        .section-divider {
            height: 1px;
            background: #e2e8f0;
            margin: 2rem 0;
        }

        /* STAGE PROGRESS */
        .stage-container {
            padding: 2rem 1.5rem;
            background: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 2rem;
        }

        .stage-row {
            display: flex;
            justify-content: center;
            gap: 1rem;
        }

        .stage-step {
            text-align: center;
            min-width: 100px;
        }

        .stage-circle {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: 600;
            font-size: 1rem;
            margin: 0 auto .5rem auto;
            border: 2px solid;
        }

        .stage-circle.active {
            background:#1e40af; border-color:#1e40af; color:white !important;
        }

        .stage-circle.completed {
            background:#10b981; border-color:#10b981; color:white !important;
        }

        .stage-circle.inactive {
            background:#f8fafc; border-color:#e2e8f0; color:#94a3b8 !important;
        }

        .stage-label { font-size:.85rem; color:#64748b !important; }
        .stage-label.active { color:#1e40af !important; font-weight:600; }

        /* DOWNLOAD BUTTON */
        [data-testid="stDownloadButton"] button {
            background:#1e40af !important;
            color:white !important;
            border:none !important;
            font-weight:600 !important;
            border-radius:8px !important;
            padding:.75rem 1.5rem !important;
            width:100% !important;
        }

        /* FILE UPLOADER */
        [data-testid="stFileUploader"] > div {
            background:white !important;
            border:2px dashed #cbd5e1 !important;
            border-radius:8px !important;
            padding:2rem !important;
        }

        [data-testid="stFileUploader"] label {
            color:#1e293b !important;
            font-weight:600 !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{title}</h1>
            {'<p>'+subtitle+'</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stage_progress(current_stage: int):
    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"),
        ("3", "Results"),
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

    html = "".join(blocks)

    st.markdown(
        f"""
        <div class="stage-container">
            <div class="stage-row">{html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card(title: str, icon: str = ""):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-header">{icon if icon else ''} {title}</div>
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
        "error": "✕",
    }
    st.markdown(
        f"""
        <div class="alert alert-{alert_type}">
            <strong>{icons.get(alert_type,"ℹ")}</strong>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_download_template_button():
    try:
        template_path = Path("polymer_production_template.xlsx")

        if template_path.exists():
            st.download_button(
                label="Download Template",
                data=template_path.read_bytes(),
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.error("Template file not found")
    except Exception as e:
        st.error(f"Error loading template: {e}")
