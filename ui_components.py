"""
UI Components with Material-3 inspired design + Clickable Animated Stepper
"""

import streamlit as st
import streamlit.components.v1 as components
from constants import THEME_COLORS, SS_THEME


# =====================================================================
# APPLY GLOBAL THEME + CSS
# =====================================================================
def apply_custom_css(is_dark_mode=False):

    radius = "14px"
    card_shadow = "0 3px 8px rgba(0, 0, 0, 0.07)"
    hover_shadow = "0 6px 20px rgba(0, 0, 0, 0.15)"

    if is_dark_mode:
        theme = {
            "--bg-main": "#0D1117",
            "--bg-surface": "#161B22",
            "--bg-card": "#1C2128",
            "--text-primary": "#F0F6FC",
            "--text-secondary": "#8B949E",
            "--border": "#2D333B",
            "--tab-bg": "#21262D",
            "--primary": "#58A6FF",
            "--primary-hover": "#1F6FEB",
            "--gradient": "linear-gradient(135deg, #58A6FF 0%, #1F6FEB 100%)",
        }
    else:
        theme = {
            "--bg-main": "#FFFFFF",
            "--bg-surface": "#F6F8FA",
            "--bg-card": "#FFFFFF",
            "--text-primary": "#1B1F24",
            "--text-secondary": "#57606A",
            "--border": "#D0D7DE",
            "--tab-bg": "#F6F8FA",
            "--primary": "#0969DA",
            "--primary-hover": "#033D8B",
            "--gradient": "linear-gradient(135deg, #0969DA 0%, #033D8B 100%)",
        }

    st.markdown(
        f"""
        <style>
        :root {{
            {"".join([f"{k}: {v};" for k, v in theme.items()])}
        }}

        body, .main, .stApp {{
            background: var(--bg-main) !important;
            color: var(--text-primary) !important;
        }}

        p, span, div {{
            color: var(--text-primary) !important;
        }}

        /* HEADER */
        .app-header {{
            background: var(--gradient);
            padding: 2rem;
            color: white;
            border-radius: {radius};
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: {card_shadow};
        }}

        /* CARDS */
        .card {{
            background: var(--bg-card);
            padding: 1.7rem;
            border-radius: {radius};
            border: 1px solid var(--border);
            box-shadow: {card_shadow};
            margin-bottom: 1.5rem;
        }}

        /* METRIC CARDS */
        .metric-card {{
            background: var(--gradient);
            color: white;
            padding: 1.4rem;
            border-radius: {radius};
            text-align: center;
            box-shadow: {card_shadow};
            transition: 0.25s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: {hover_shadow};
        }}

        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
        }}

        /* ALERTS */
        .alert {{
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            display: flex;
            gap: 0.8rem;
            align-items: flex-start;
            border-left-width: 5px;
            border-left-style: solid;
        }}

        .alert-success {{
            background: {THEME_COLORS['success_light']};
            border-left-color: #1A7F37;
        }}
        .alert-info {{
            background: {THEME_COLORS['primary_light']};
            border-left-color: var(--primary);
        }}

        /* STAGE PROGRESS BASE CSS (Connectors added in component) */
        </style>
        """,
        unsafe_allow_html=True,
    )


# =====================================================================
# THEME TOGGLE
# =====================================================================
def render_theme_toggle():
    if SS_THEME not in st.session_state:
        st.session_state[SS_THEME] = "light"

    current = st.session_state[SS_THEME]
    label = "🌙 Dark" if current == "light" else "☀️ Light"

    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button(label):
            st.session_state[SS_THEME] = "dark" if current == "light" else "light"
            st.rerun()


# =====================================================================
# HEADER
# =====================================================================
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


# =====================================================================
# *** CLICKABLE + ANIMATED STAGE PROGRESS ***
# =====================================================================
def render_stage_progress(current_stage: int):

    if "stage" not in st.session_state:
        st.session_state["stage"] = current_stage

    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"),
        ("3", "Results"),
    ]

    items = []
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

        items.append(
            f"""
            <div class="step-block" onclick="setStage({idx})">
                <div class="step-circle {status}">{icon}</div>
                <div class="step-label {'active' if idx == current_stage else ''}">
                    {label}
                </div>
            </div>
            """
        )

    html = f"""
    <html>
    <head>
    <style>

        .stepper-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            margin-top: 0.6rem;
            position: relative;
        }}

        /* CONNECTOR BAR (behind steps) */
        .stepper-line {{
            position: absolute;
            top: 22px;
            left: 0;
            width: 100%;
            height: 5px;
            background: var(--border);
            z-index: 1;
            border-radius: 5px;
        }}

        /* ANIMATED filled progress */
        .stepper-progress {{
            position: absolute;
            top: 22px;
            left: 0;
            height: 5px;
            background: var(--primary);
            border-radius: 5px;
            z-index: 2;
            width: calc({current_stage} / {len(stages)-1} * 100%);
            transition: width 0.35s ease-in-out;
        }}

        .step-block {{
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 3;
            cursor: pointer;
        }}

        .step-circle {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: 600;
            background: var(--border);
            color: var(--text-secondary);
            transition: transform 0.25s ease, background 0.25s ease;
        }}

        .step-circle.completed {{
            background: #1A7F37;
            color: white;
        }}

        .step-circle.active {{
            background: var(--primary);
            color: white;
            transform: scale(1.07);
        }}

        .step-label {{
            margin-top: 4px;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}

        .step-label.active {{
            color: var(--primary);
            font-weight: 600;
        }}

    </style>
    </head>

    <body>

        <div class="stepper-container">

            <div class="stepper-line"></div>
            <div class="stepper-progress"></div>

            {''.join(items)}

        </div>

        <script>
        function setStage(s) {{
            fetch("/_stcore/forward_msg", {{
                method: "POST",
                body: JSON.stringify({{ stage: s }})
            }}).then(() => window.parent.location.reload());
        }}
        </script>

    </body>
    </html>
    """

    components.html(html, height=150)


# =====================================================================
# CARDS
# =====================================================================
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


# =====================================================================
# METRICS
# =====================================================================
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


# =====================================================================
# ALERT BOXES
# =====================================================================
def render_alert(message: str, alert_type: str = "info"):
    icons = {"success": "✔", "info": "ℹ", "warning": "⚠", "error": "✕"}
    st.markdown(
        f"""
        <div class="alert alert-{alert_type}">
            <strong style="font-size:1.2rem">{icons.get(alert_type,"ℹ")}</strong>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =====================================================================
# DIVIDER
# =====================================================================
def render_section_divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
