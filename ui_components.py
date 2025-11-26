"""
Reusable UI components with Material Design 3 Light Blue theme
Clean, modern interface with blue primary colors
"""

import streamlit as st
from constants import THEME_COLORS


# ------------------------------------------------------------
# THEME + GLOBAL CSS
# ------------------------------------------------------------
def apply_custom_css():
    """Apply Material 3 Light theme with Blue primary colors."""

    radius = "12px"
    radius_lg = "16px"
    card_shadow = "0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)"
    hover_shadow = "0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23)"

    # Material 3 Light Blue Theme
    theme = {
        # Surface colors
        "--md-sys-color-background": "#FDFCFF",
        "--md-sys-color-surface": "#FDFCFF",
        "--md-sys-color-surface-variant": "#E1E2EC",
        "--md-sys-color-surface-container": "#F0F0F7",
        "--md-sys-color-surface-container-high": "#EAEAF1",
        "--md-sys-color-surface-container-highest": "#E5E5EB",
        
        # Text colors
        "--md-sys-color-on-surface": "#1A1C1E",
        "--md-sys-color-on-surface-variant": "#44474E",
        "--md-sys-color-outline": "#74777F",
        "--md-sys-color-outline-variant": "#C4C6D0",
        
        # Primary colors (Blue)
        "--md-sys-color-primary": "#0B57D0",
        "--md-sys-color-on-primary": "#FFFFFF",
        "--md-sys-color-primary-container": "#D3E3FD",
        "--md-sys-color-on-primary-container": "#001B3F",
        
        # Secondary colors (Blue-Gray)
        "--md-sys-color-secondary": "#5A6470",
        "--md-sys-color-secondary-container": "#DEE3EB",
        "--md-sys-color-on-secondary-container": "#171C22",
        
        # Tertiary colors (Teal)
        "--md-sys-color-tertiary": "#006A6A",
        "--md-sys-color-tertiary-container": "#9CF2F2",
        "--md-sys-color-on-tertiary-container": "#00201F",
        
        # Error colors
        "--md-sys-color-error": "#BA1A1A",
        "--md-sys-color-error-container": "#FFDAD6",
        "--md-sys-color-on-error-container": "#410002",
        
        # Success colors
        "--md-sys-color-success": "#146C2E",
        "--md-sys-color-success-container": "#B7F3C6",
        "--md-sys-color-on-success-container": "#002106",
        
        # Warning colors
        "--md-sys-color-warning": "#7D5700",
        "--md-sys-color-warning-container": "#FFE08B",
        "--md-sys-color-on-warning-container": "#271900",
    }

    # Inject CSS
    st.markdown(
        f"""
        <style>
        :root {{
            {"".join([f"{k}: {v};" for k, v in theme.items()])}
        }}

        /* ------------------------------------
        GLOBAL RESETS
        ------------------------------------*/
        .stApp {{
            background: var(--md-sys-color-background);
        }}
        
        .main {{
            background: var(--md-sys-color-background);
        }}

        /* Only target specific text elements, not all divs */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--md-sys-color-on-surface);
        }}

        /* ------------------------------------
        HEADER
        ------------------------------------*/
        .app-header {{
            background: linear-gradient(135deg, var(--md-sys-color-primary) 0%, var(--md-sys-color-primary-container) 100%);
            padding: 2rem;
            color: var(--md-sys-color-on-primary);
            border-radius: {radius_lg};
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: {card_shadow};
        }}
        .app-header h1 {{
            margin: 0;
            font-size: 2.4rem;
            font-weight: 600;
            color: var(--md-sys-color-on-primary);
        }}
        .app-header p {{
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            color: var(--md-sys-color-on-primary);
        }}

        /* ------------------------------------
        CARDS
        ------------------------------------*/
        .card {{
            background: var(--md-sys-color-surface-container-high);
            padding: 1.5rem;
            border-radius: {radius};
            border: 1px solid var(--md-sys-color-outline-variant);
            box-shadow: {card_shadow};
            margin-bottom: 1.5rem;
        }}
        .card-header {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--md-sys-color-on-surface);
        }}

        /* ------------------------------------
        METRIC CARDS
        ------------------------------------*/
        .metric-card {{
            background: linear-gradient(135deg, var(--md-sys-color-primary) 0%, var(--md-sys-color-primary-container) 100%);
            color: var(--md-sys-color-on-primary);
            padding: 1.5rem;
            border-radius: {radius};
            text-align: center;
            box-shadow: {card_shadow};
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: {hover_shadow};
        }}

        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--md-sys-color-on-primary);
        }}

        .metric-label {{
            font-size: 0.875rem;
            opacity: 0.9;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: var(--md-sys-color-on-primary);
        }}

        /* ------------------------------------
        ALERT BOXES
        ------------------------------------*/
        .alert {{
            padding: 1rem 1.25rem;
            border-radius: {radius};
            margin-bottom: 1rem;
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
            border-left-width: 4px;
            border-left-style: solid;
        }}

        .alert strong {{
            font-size: 1.2rem;
            line-height: 1;
        }}

        .alert span {{
            line-height: 1.5;
        }}

        .alert-success {{
            background: var(--md-sys-color-success-container);
            border-left-color: var(--md-sys-color-success);
            color: var(--md-sys-color-on-success-container);
        }}
        .alert-success strong,
        .alert-success span {{
            color: var(--md-sys-color-on-success-container);
        }}

        .alert-info {{
            background: var(--md-sys-color-primary-container);
            border-left-color: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary-container);
        }}
        .alert-info strong,
        .alert-info span {{
            color: var(--md-sys-color-on-primary-container);
        }}

        .alert-warning {{
            background: var(--md-sys-color-warning-container);
            border-left-color: var(--md-sys-color-warning);
            color: var(--md-sys-color-on-warning-container);
        }}
        .alert-warning strong,
        .alert-warning span {{
            color: var(--md-sys-color-on-warning-container);
        }}

        .alert-error {{
            background: var(--md-sys-color-error-container);
            border-left-color: var(--md-sys-color-error);
            color: var(--md-sys-color-on-error-container);
        }}
        .alert-error strong,
        .alert-error span {{
            color: var(--md-sys-color-on-error-container);
        }}

        /* ------------------------------------
        TABS
        ------------------------------------*/
        .stTabs [data-baseweb="tab-list"] {{
            background: var(--md-sys-color-surface-container);
            padding: 0.5rem;
            border-radius: {radius};
            gap: 0.5rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: {radius};
            background: transparent;
            border: 1px solid transparent;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            color: var(--md-sys-color-on-surface-variant);
            transition: all 0.2s ease;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background: var(--md-sys-color-surface-container-high);
            color: var(--md-sys-color-on-surface);
        }}

        .stTabs [aria-selected="true"] {{
            background: var(--md-sys-color-primary) !important;
            color: var(--md-sys-color-on-primary) !important;
            border-color: var(--md-sys-color-primary);
        }}

        /* ------------------------------------
        BUTTONS
        ------------------------------------*/
        .stButton > button {{
            background: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary);
            padding: 0.75rem 2rem;
            font-weight: 600;
            border-radius: {radius};
            border: none;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
        }}
        .stButton > button:hover {{
            background: var(--md-sys-color-primary-container);
            box-shadow: {hover_shadow};
            transform: translateY(-1px);
        }}
        .stButton > button:active {{
            transform: translateY(0);
        }}

        /* ------------------------------------
        STAGE PROGRESS
        ------------------------------------*/
        .stage-container {{
            padding: 1.5rem;
            background: var(--md-sys-color-surface-container-high);
            border-radius: {radius};
            border: 1px solid var(--md-sys-color-outline-variant);
            box-shadow: {card_shadow};
            margin-bottom: 2rem;
        }}

        .stage-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
        }}

        .stage-step {{
            flex: 1;
            text-align: center;
        }}

        .stage-connector {{
            flex: 0.5;
            height: 2px;
            background: var(--md-sys-color-outline-variant);
            margin: 0 0.5rem;
            border-radius: 1px;
        }}

        .stage-circle {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1rem;
            margin: 0 auto 0.5rem auto;
            transition: all 0.3s ease;
        }}

        .stage-circle.active {{
            background: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary);
            box-shadow: 0 2px 8px rgba(103, 80, 164, 0.4);
        }}

        .stage-circle.completed {{
            background: var(--md-sys-color-success);
            color: var(--md-sys-color-on-primary);
        }}

        .stage-circle.inactive {{
            background: var(--md-sys-color-surface-container-highest);
            color: var(--md-sys-color-on-surface-variant);
            border: 2px solid var(--md-sys-color-outline-variant);
        }}

        .stage-label {{
            font-size: 0.875rem;
            color: var(--md-sys-color-on-surface-variant);
            font-weight: 500;
        }}

        .stage-label.active {{
            color: var(--md-sys-color-primary);
            font-weight: 600;
        }}

        /* ------------------------------------
        SECTION DIVIDER
        ------------------------------------*/
        .section-divider {{
            height: 1px;
            background: var(--md-sys-color-outline-variant);
            margin: 2rem 0;
            border: none;
        }}

        /* ------------------------------------
        OPTIMIZATION SPINNER
        ------------------------------------*/
        .optimization-container {{
            text-align: center;
            padding: 3rem 1rem;
        }}

        .spinner {{
            width: 60px;
            height: 60px;
            margin: 0 auto 1.5rem;
            border: 4px solid var(--md-sys-color-outline-variant);
            border-top-color: var(--md-sys-color-primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        .optimization-text {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--md-sys-color-on-surface);
            margin-bottom: 0.5rem;
        }}

        .optimization-subtext {{
            font-size: 1rem;
            color: var(--md-sys-color-on-surface-variant);
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# THEME TOGGLE
# ------------------------------------------------------------
def render_theme_toggle():
    """Render theme toggle button in top-right corner."""
    if SS_THEME not in st.session_state:
        st.session_state[SS_THEME] = "light"

    current = st.session_state[SS_THEME]
    label = "🌙 Dark" if current == "light" else "☀️ Light"

    _, col = st.columns([8, 1])
    with col:
        if st.button(label, key="theme_toggle"):
            st.session_state[SS_THEME] = "dark" if current == "light" else "light"
            st.rerun()


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
def render_header(title: str, subtitle: str = ""):
    """Render app header with title and optional subtitle."""
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
# STAGE PROGRESS
# ------------------------------------------------------------
def render_stage_progress(current_stage: int) -> None:
    """Render wizard-style stage progress indicator."""
    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"),
        ("3", "Results")
    ]

    total = len(stages)
    current_stage = max(0, min(current_stage, total - 1))

    blocks = []
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

    # Insert connectors between stages
    html = ""
    for i, block in enumerate(blocks):
        html += block
        if i < total - 1:
            html += '<div class="stage-connector"></div>'

    st.markdown(
        f"""
        <div class="stage-container">
            <div class="stage-row">{html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# CARDS
# ------------------------------------------------------------
def render_card(title: str, icon: str = ""):
    """Open a card container with optional icon."""
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


# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------
def render_metric_card(label: str, value: str, col):
    """Render a metric card in the specified column."""
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


# ------------------------------------------------------------
# ALERTS
# ------------------------------------------------------------
def render_alert(message: str, alert_type: str = "info"):
    """Render an alert box with icon and message."""
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


# ------------------------------------------------------------
# DIVIDER
# ------------------------------------------------------------
def render_section_divider():
    """Render a horizontal divider line."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
