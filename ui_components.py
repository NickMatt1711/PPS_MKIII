"""
Reusable UI components with modern elevated material design (M3-Inspired)
Fully refactored for aesthetics, consistency & maintainability.
Now includes fully JS-clickable stage progress.
"""

import streamlit as st
from constants import THEME_COLORS, SS_THEME


# ------------------------------------------------------------
# THEME + GLOBAL CSS
# ------------------------------------------------------------
def apply_custom_css(is_dark_mode=False):
    """Apply Material-3 style UI theme with clean spacing & updated colors."""

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

    # Inject CSS
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
        .app-header h1 {{
            margin: 0;
            font-size: 2.4rem;
            font-weight: 600;
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
        .card-header {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}

        /* METRIC */
        .metric-card {{
            background: var(--gradient);
            color: white !important;
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

        /* ---------------------------------------
          JS-CLICKABLE STAGE PROGRESS BAR
        -----------------------------------------*/

        .stage-container {{
            padding: 1.2rem;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: {radius};
            box-shadow: {card_shadow};
        }}

        .stage-flex {{
            display: flex;
            justify-content: space-between;
            gap: 1rem;
        }}

        .stage-step {{
            text-align: center;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 10px;
            transition: 0.2s ease;
        }}

        .stage-step:hover .stage-label {{
            color: var(--primary);
        }}

        .stage-circle {{
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            font-weight: 600;
            margin: 0 auto 0.3rem auto;
            transition: 0.2s ease;
        }}

        .stage-circle.active {{
            background: var(--primary) !important;
            color: white !important;
        }}

        .stage-circle.completed {{
            background: #1A7F37 !important;
            color: white !important;
        }}

        .stage-circle.inactive {{
            background: var(--border);
            color: var(--text-secondary) !important;
        }}

        .stage-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}

        .stage-label.active {{
            color: var(--primary) !important;
        }}

        .stage-step:hover .stage-circle.inactive {{
            background: var(--primary);
            color: white !important;
        }}

        .section-divider {{
            height: 1px;
            background: var(--border);
            margin: 2rem 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# THEME TOGGLE
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# JS-CLICKABLE STAGE PROGRESS BAR
# ------------------------------------------------------------
def render_stage_progress(current_stage: int):
    if "stage" not in st.session_state:
        st.session_state["stage"] = current_stage

    if "finalized" not in st.session_state:
        st.session_state["finalized"] = False

    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"),
        ("3", "Results")
    ]

    stage_blocks = []

    for idx, (num, label) in enumerate(stages):

        # ---- CORRECTED LOGIC ----
        if idx < current_stage:
            status = "completed"
            icon = "✓"

        elif idx == current_stage:

            # Only completed if this is final step *and* finished
            if idx == len(stages) - 1 and st.session_state["finalized"]:
                status = "completed"
                icon = "✓"
            else:
                status = "active"
                icon = num

        else:
            status = "inactive"
            icon = num
        # --------------------------

        stage_blocks.append(
            f"""
            <div class="stage-step" onclick="window.setStage({idx})">
                <div class="stage-circle {status}">{icon}</div>
                <div class="stage-label {'active' if idx == current_stage else ''}">
                    {label}
                </div>
            </div>
            """
        )

    html = f"""
    <div class="stage-container">
        <div class="stage-flex">
            {''.join(stage_blocks)}
        </div>
    </div>

    <script>
        window.setStage = function(stageIndex) {{
            const payload = {{ "stage": stageIndex }};
            fetch("/_stcore/update", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify(payload)
            }}).then(() => window.location.reload());
        }}
    </script>
    """

    st.markdown(html, unsafe_allow_html=True)

# ------------------------------------------------------------
# CARDS
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# METRICS, ALERTS, DIVIDER
# ------------------------------------------------------------
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


def render_section_divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
