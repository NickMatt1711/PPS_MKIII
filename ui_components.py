# ui_components.py
"""
Full Material 3 UI Component System
Completely rewritten to replace gradients, neon colors,
and outdated styling with a clean, accessible M3 visual language.
"""

import base64
import streamlit as st

# ============================================================
# MATERIAL 3 TOKEN SET
# ============================================================

M3 = dict(
    primary="#6750A4",
    on_primary="#FFFFFF",
    primary_container="#EADDFF",
    on_primary_container="#21005D",

    secondary="#625B71",
    on_secondary="#FFFFFF",
    secondary_container="#E8DEF8",
    on_secondary_container="#1D192B",

    surface="#FFFBFE",
    on_surface="#1C1B1F",
    surface_variant="#E7E0EC",
    on_surface_variant="#49454F",

    outline="#79747E",
)


# ============================================================
# GLOBAL CSS INJECTION
# Material 3 throughout the app
# ============================================================

def apply_custom_css():
    p = M3
    radius = "12px"
    radius_lg = "18px"

    st.markdown(
        f"""
        <style>

        /* Root surface */
        .stApp {{
            background: {p['surface']} !important;
            color: {p['on_surface']} !important;
            font-family: "Inter", sans-serif !important;
        }}

        /* Typography */
        h1, h2, h3 {{
            color: {p['on_surface']} !important;
            font-weight: 600 !important;
        }}

        /* ---------------------------------------------------- */
        /* HEADER                                               */
        /* ---------------------------------------------------- */

        .app-header {{
            background: {p['primary']};
            color: {p['on_primary']};
            padding: 2.5rem 2rem;
            border-radius: {radius_lg};
            margin-bottom: 1.5rem;
        }}

        /* ---------------------------------------------------- */
        /* PROGRESS BAR                                         */
        /* ---------------------------------------------------- */

        .stage-container {{
            background: {p['surface']};
            border: 1px solid {p['outline']};
            padding: 2rem;
            border-radius: {radius_lg};
            margin-bottom: 2rem;
        }}

        .stage-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2rem;
        }}

        .stage-step {{
            text-align: center;
        }}

        .stage-circle {{
            width: 58px;
            height: 58px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.25rem;
        }}

        .stage-circle.active {{
            background: {p['primary']};
            color: {p['on_primary']};
        }}

        .stage-circle.completed {{
            background: {p['primary_container']};
            color: {p['on_primary_container']};
            border: 1px solid {p['primary']};
        }}

        .stage-circle.inactive {{
            background: {p['surface_variant']};
            color: {p['on_surface_variant']};
            border: 1px solid {p['outline']};
        }}

        .stage-label {{
            margin-top: .35rem;
            font-size: .9rem;
            color: {p['on_surface']};
        }}

        .stage-label.active {{
            color: {p['primary']};
            font-weight: 600;
        }}

        .stage-connector {{
            width: 70px;
            height: 4px;
            border-radius: 2px;
            background: {p['surface_variant']};
        }}

        .stage-connector.completed {{
            background: {p['primary']};
        }}

        /* ---------------------------------------------------- */
        /* CARD                                                  */
        /* ---------------------------------------------------- */

        .card {{
            background: {p['surface']};
            border: 1px solid {p['outline']};
            border-radius: {radius_lg};
            padding: 1.5rem 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0px 1px 3px rgba(0,0,0,0.08);
        }}

        .card-title {{
            color: {p['on_surface_variant']};
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .card-value {{
            color: {p['on_surface']};
            font-size: 1.4rem;
            font-weight: 700;
        }}

        /* ---------------------------------------------------- */
        /* ALERTS                                               */
        /* ---------------------------------------------------- */

        .alert {{
            border-radius: {radius_lg};
            padding: 1rem 1rem;
            margin: 1rem 0;
            font-weight: 500;
            border: 1px solid transparent;
        }}

        .alert-success {{
            background: {p['primary_container']};
            color: {p['on_primary_container']};
            border-color: {p['primary']};
        }}

        .alert-warning {{
            background: {p['secondary_container']};
            color: {p['on_secondary_container']};
            border-color: {p['secondary']};
        }}

        .alert-error {{
            background: {p['surface_variant']};
            color: #B3261E;
            border-color: #B3261E;
        }}

        /* ---------------------------------------------------- */
        /* DIVIDER                                              */
        /* ---------------------------------------------------- */

        .divider {{
            height: 2px;
            background: {p['primary']};
            margin: 2rem 0 1rem 0;
            border-radius: 2px;
        }}

        /* ---------------------------------------------------- */
        /* DOWNLOAD BUTTON                                      */
        /* ---------------------------------------------------- */

        .download-btn {{
            display: inline-block;
            background: {p['primary']};
            color: {p['on_primary']} !important;
            padding: 0.75rem 1.25rem;
            border-radius: {radius};
            text-decoration: none;
            font-weight: 600;
            transition: 0.15s ease-in-out;
        }}

        .download-btn:hover {{
            background: {p['primary_container']};
            color: {p['on_primary_container']} !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HEADER
# ============================================================

def render_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{title}</h1>
            <p style="color: {M3['on_primary']}; margin-top: .5rem;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROGRESS BAR
# ============================================================

def render_stage_progress(current_stage: int) -> None:
    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"),
        ("3", "Results")
    ]
    last = len(stages) - 1

    current_stage = max(0, min(current_stage, last))

    blocks = []
    connectors = []

    for idx, (num, label) in enumerate(stages):

        if idx == last:
            status = "completed"
            icon = "✓"
        else:
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

        if idx < last:
            connector_class = "completed" if idx < current_stage else ""
            connectors.append(f'<div class="stage-connector {connector_class}"></div>')

    final_html = ""
    for i, b in enumerate(blocks):
        final_html += b
        if i < len(connectors):
            final_html += connectors[i]

    st.markdown(
        f"""
        <div class="stage-container">
            <div class="stage-row">{final_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# CARDS / METRICS
# ============================================================

def render_card(title: str, value: str):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ALERTS
# ============================================================

def render_alert(message: str, alert_type: str = "success"):
    mapping = {
        "success": "alert-success",
        "warning": "alert-warning",
        "error": "alert-error",
    }
    style_class = mapping.get(alert_type, "alert-success")

    st.markdown(
        f"""
        <div class="alert {style_class}">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DIVIDER
# ============================================================

def render_divider():
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ============================================================
# QUICK START SECTION
# ============================================================

def render_quickstart():
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Quick start</div>
            <div class="card-value" style="font-size: 1rem; font-weight: 500;">
                1. Upload your PPS export file<br>
                2. Preview and configure your output<br>
                3. Download clean results instantly
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DOWNLOAD BUTTON
# ============================================================

def render_download_button(label: str, file_bytes: bytes, file_name: str):
    b64 = base64.b64encode(file_bytes).decode()
    href = f'data:application/octet-stream;base64,{b64}'

    st.markdown(
        f"""
        <a download="{file_name}" href="{href}" class="download-btn">
            {label}
        </a>
        """,
        unsafe_allow_html=True
    )

