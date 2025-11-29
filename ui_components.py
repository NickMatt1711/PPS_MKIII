"""
Material 3 Corporate Theme - PROPERLY INTEGRATED UI Components
"""

import streamlit as st
from constants import THEME_COLORS  # Import the theme colors

def apply_custom_css():
    """Apply Material 3 Light theme styling."""
    st.markdown(
        """
        <style>

        /*********************************************************
         MATERIAL 3 TOKENS (Generated from THEME_COLORS)
        **********************************************************/
        :root {
            /* PRIMARY */
            --md-sys-color-primary: #5E7CE2;
            --md-sys-color-on-primary: #FFFFFF;
            --md-sys-color-primary-container: #E8EEFF;
            --md-sys-color-on-primary-container: #1C1B1F;

            /* SECONDARY */
            --md-sys-color-secondary: #4BAF39;
            --md-sys-color-on-secondary: #FFFFFF;
            --md-sys-color-secondary-container: #E8F5E9;
            --md-sys-color-on-secondary-container: #1C1B1F;

            /* TERTIARY (Accent warm tones) */
            --md-sys-color-tertiary: #C9852F;
            --md-sys-color-on-tertiary: #FFFFFF;
            --md-sys-color-tertiary-container: #FCEFD9;
            --md-sys-color-on-tertiary-container: #1C1B1F;

            /* ERROR */
            --md-sys-color-error: #B3261E;
            --md-sys-color-on-error: #FFFFFF;
            --md-sys-color-error-container: #F9DEDC;
            --md-sys-color-on-error-container: #410E0B;

            /* SUCCESS */
            --md-sys-color-success: #4BAF39;
            --md-sys-color-on-success: #FFFFFF;
            --md-sys-color-success-container: #E8F5E9;
            --md-sys-color-on-success-container: #1C1B1F;

            /* INFO */
            --md-sys-color-info: #75777F;
            --md-sys-color-on-info: #FFFFFF;
            --md-sys-color-info-container: #F4F4F5;
            --md-sys-color-on-info-container: #1C1B1F;

            /* SURFACE & BACKGROUND */
            --md-sys-color-background: #F7F8FA;
            --md-sys-color-surface: #FFFFFF;
            --md-sys-color-surface-variant: #E7E0EC;
            --md-sys-color-on-surface: #1C1B1F;
            --md-sys-color-on-surface-variant: #49454F;

            /* OUTLINE */
            --md-sys-color-outline: #79747E;
            --md-sys-color-outline-variant: #CAC5D0;

            /* ELEVATION */
            --md-elevation-1: 0px 1px 3px rgba(0,0,0,0.12);
            --md-elevation-2: 0px 2px 6px rgba(0,0,0,0.12);

            /* SHAPE */
            --md-shape-corner-small: 8px;
            --md-shape-corner-medium: 12px;
            --md-shape-corner-large: 16px;
        }


        /*********************************************************
         STREAMLIT — FORCE LIGHT THEME (REAL DOM SELECTORS)
        **********************************************************/
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background-color: var(--md-sys-color-background) !important;
            color: var(--md-sys-color-on-surface) !important;
        }

        /* Main container background */
        [data-testid="stAppViewContainer"] > .main {
            background-color: var(--md-sys-color-background) !important;
        }

        /* Markdown text, labels, headers */
        h1, h2, h3, h4, h5, p, label, span, div {
            color: var(--md-sys-color-on-surface) !important;
        }

        /*********************************************************
         FIXED: UPLOADER + BUTTONS (LIGHT THEME)
        **********************************************************/
        [data-testid="stFileUploader"] {
            background-color: var(--md-sys-color-surface) !important;
            border: 2px dashed var(--md-sys-color-outline) !important;
            border-radius: var(--md-shape-corner-medium) !important;
            padding: 1rem !important;
        }
        [data-testid="stFileUploader"] * {
            color: var(--md-sys-color-on-surface) !important;
        }

        .stButton button, .stDownloadButton button {
            background-color: var(--md-sys-color-primary) !important;
            color: var(--md-sys-color-on-primary) !important;
            border-radius: var(--md-shape-corner-small) !important;
            padding: 0.6rem 1.4rem !important;
            font-weight: 500 !important;
            border: none !important;
            box-shadow: var(--md-elevation-1) !important;
        }


        /*********************************************************
         FIXED: DATAFRAMES — FORCE LIGHT MODE
        **********************************************************/
        [data-testid="stDataFrame"] table {
            background-color: var(--md-sys-color-surface) !important;
        }
        [data-testid="stDataFrame"] th {
            background-color: var(--md-sys-color-surface-variant) !important;
            color: var(--md-sys-color-on-surface-variant) !important;
        }
        [data-testid="stDataFrame"] td {
            background-color: var(--md-sys-color-surface) !important;
            color: var(--md-sys-color-on-surface) !important;
        }
        [data-testid="stDataFrame"] tbody tr:hover td {
            background: color-mix(in srgb, var(--md-sys-color-primary-container) 15%, transparent) !important;
        }


        /*********************************************************
         FIXED: TABS — FULL WIDTH DISTRIBUTION
        **********************************************************/
        .stTabs [data-baseweb="tab-list"] {
            display: flex !important;
            width: 100% !important;
        }
        button[data-baseweb="tab"] {
            flex: 1 !important;
            margin: 0 !important;
            text-align: center !important;
            border-radius: 0 !important;
            border-bottom: 2px solid transparent !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            border-bottom: 2px solid var(--md-sys-color-primary) !important;
            color: var(--md-sys-color-primary) !important;
        }


        /*********************************************************
         FIXED: STAGE PROGRESS — TRUE HORIZONTAL
        **********************************************************/
        .stage-row {
            display: flex;
            width: 100%;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .stage-step {
            flex: 1;
            text-align: center;
        }
        .stage-connector {
            flex: 1;
            height: 2px;
            background: var(--md-sys-color-outline-variant);
        }
        .stage-connector.completed {
            background: var(--md-sys-color-success);
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
    st.markdown('<div style="margin: 2rem 0; border-top: 1px solid var(--md-outline-variant);"></div>', unsafe_allow_html=True)


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
