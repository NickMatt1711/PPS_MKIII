"""
Reusable UI components with vibrant multi-color theme
Maximum contrast, colorful sections, no sidebar
"""

import streamlit as st
from constants import THEME_COLORS


# ------------------------------------------------------------
# THEME + GLOBAL CSS
# ------------------------------------------------------------
def apply_custom_css():
    """Apply vibrant multi-color theme with maximum contrast."""

    radius = "12px"
    radius_lg = "16px"
    card_shadow = "0 4px 12px rgba(0, 0, 0, 0.15)"
    hover_shadow = "0 6px 20px rgba(0, 0, 0, 0.25)"

    st.markdown(
        f"""
        <style>
        /* ------------------------------------
        GLOBAL BASE - Light clean background
        ------------------------------------*/
        .stApp {{
            background: #f0f2f6 !important;
        }}
        
        .main {{
            background: #f0f2f6 !important;
        }}

        /* Force readable text */
        p, span, div, label {{
            color: #2d3748 !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: #1a202c !important;
            font-weight: 700 !important;
        }}

        /* ------------------------------------
        HEADER - Bold Purple Gradient
        ------------------------------------*/
        .app-header {{
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            padding: 3rem 2rem;
            color: white !important;
            border-radius: {radius_lg};
            margin-bottom: 2.5rem;
            text-align: center;
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
            border: 4px solid white;
        }}
        .app-header h1 {{
            margin: 0;
            font-size: 2.8rem;
            font-weight: 900;
            color: white !important;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
            letter-spacing: -0.5px;
        }}
        .app-header p {{
            margin: 1rem 0 0 0;
            font-size: 1.2rem;
            color: rgba(255, 255, 255, 0.95) !important;
            font-weight: 600;
        }}

        /* ------------------------------------
        CARDS - White with colored borders
        ------------------------------------*/
        .card {{
            background: white;
            padding: 2rem;
            border-radius: {radius};
            border: 3px solid #e2e8f0;
            box-shadow: {card_shadow};
            margin-bottom: 2rem;
        }}
        .card-header {{
            font-size: 1.5rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            color: #1a202c !important;
            border-bottom: 3px solid #6366f1;
            padding-bottom: 0.75rem;
        }}

        /* ------------------------------------
        METRIC CARDS - Different vibrant colors
        ------------------------------------*/
        .metric-card {{
            padding: 2rem 1.5rem;
            border-radius: {radius};
            text-align: center;
            box-shadow: {card_shadow};
            transition: all 0.3s ease;
            border: 4px solid white;
            position: relative;
            overflow: hidden;
        }}
        .metric-card:hover {{
            transform: translateY(-6px) scale(1.02);
            box-shadow: {hover_shadow};
        }}

        /* Purple */
        .metric-card:nth-child(1) {{
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        }}
        /* Pink */
        .metric-card:nth-child(2) {{
            background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
        }}
        /* Cyan */
        .metric-card:nth-child(3) {{
            background: linear-gradient(135deg, #06b6d4 0%, #14b8a6 100%);
        }}
        /* Green */
        .metric-card:nth-child(4) {{
            background: linear-gradient(135deg, #10b981 0%, #22c55e 100%);
        }}
        /* Orange */
        .metric-card:nth-child(5) {{
            background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
        }}

        .metric-value {{
            font-size: 2.5rem;
            font-weight: 900;
            color: white !important;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
            margin: 0.5rem 0;
        }}

        .metric-label {{
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            color: white !important;
            opacity: 0.95;
        }}

        /* ------------------------------------
        ALERT BOXES - High contrast
        ------------------------------------*/
        .alert {{
            padding: 1.5rem 2rem;
            border-radius: {radius};
            margin-bottom: 1.5rem;
            display: flex;
            gap: 1.25rem;
            align-items: center;
            border: 3px solid;
            font-weight: 600;
            box-shadow: {card_shadow};
        }}

        .alert strong {{
            font-size: 1.6rem;
            line-height: 1;
        }}

        .alert span {{
            line-height: 1.6;
            font-size: 1.05rem;
        }}

        .alert-success {{
            background: #d1fae5;
            border-color: #10b981;
            color: #065f46 !important;
        }}
        .alert-success strong,
        .alert-success span {{
            color: #065f46 !important;
        }}

        .alert-info {{
            background: #dbeafe;
            border-color: #3b82f6;
            color: #1e3a8a !important;
        }}
        .alert-info strong,
        .alert-info span {{
            color: #1e3a8a !important;
        }}

        .alert-warning {{
            background: #fef3c7;
            border-color: #f59e0b;
            color: #78350f !important;
        }}
        .alert-warning strong,
        .alert-warning span {{
            color: #78350f !important;
        }}

        .alert-error {{
            background: #fee2e2;
            border-color: #ef4444;
            color: #7f1d1d !important;
        }}
        .alert-error strong,
        .alert-error span {{
            color: #7f1d1d !important;
        }}

        /* ------------------------------------
        TABS - Colorful with high contrast
        ------------------------------------*/
        .stTabs [data-baseweb="tab-list"] {{
            background: white;
            padding: 1rem;
            border-radius: {radius};
            gap: 1rem;
            box-shadow: {card_shadow};
            border: 3px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: {radius};
            background: #f8fafc;
            border: 3px solid #e2e8f0;
            padding: 1rem 2rem;
            font-weight: 800;
            color: #1a202c !important;
            transition: all 0.3s ease;
            font-size: 1.05rem;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            white-space: nowrap;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background: #e2e8f0;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}

        /* Different color for each tab when active */
        .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {{
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
            color: white !important;
            border-color: #6366f1;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
        }}
        .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {{
            background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%) !important;
            color: white !important;
            border-color: #ec4899;
            box-shadow: 0 6px 20px rgba(236, 72, 153, 0.5) !important;
        }}
        .stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] {{
            background: linear-gradient(135deg, #06b6d4 0%, #14b8a6 100%) !important;
            color: white !important;
            border-color: #06b6d4;
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5) !important;
        }}

        /* ------------------------------------
        BUTTONS - Bold gradient
        ------------------------------------*/
        .stButton > button {{
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white !important;
            padding: 1rem 3rem;
            font-weight: 800;
            font-size: 1.1rem;
            border-radius: {radius};
            border: 4px solid white;
            transition: all 0.3s ease;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stButton > button:hover {{
            background: linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%);
            box-shadow: 0 8px 28px rgba(99, 102, 241, 0.6);
            transform: translateY(-3px) scale(1.02);
        }}
        .stButton > button:active {{
            transform: translateY(-1px) scale(1);
        }}

        /* ------------------------------------
        STAGE PROGRESS - Colorful steps
        ------------------------------------*/
        .stage-container {{
            padding: 2.5rem 2rem;
            background: white;
            border-radius: {radius_lg};
            border: 4px solid #e2e8f0;
            box-shadow: {card_shadow};
            margin-bottom: 2.5rem;
        }}

        .stage-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2rem;
        }}

        .stage-step {{
            flex: 0 0 auto;
            text-align: center;
            min-width: 120px;
        }}

        .stage-connector {{
            flex: 0 0 80px;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            position: relative;
        }}

        .stage-connector.completed {{
            background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        }}

        .stage-circle {{
            width: 70px;
            height: 70px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 1.6rem;
            margin: 0 auto 1rem auto;
            transition: all 0.3s ease;
            border: 5px solid;
        }}

        .stage-circle.active {{
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white !important;
            border-color: white;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}

        .stage-circle.completed {{
            background: linear-gradient(135deg, #10b981 0%, #22c55e 100%);
            color: white !important;
            border-color: white;
            box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
        }}

        .stage-circle.inactive {{
            background: #f8fafc;
            color: #94a3b8 !important;
            border-color: #e2e8f0;
        }}

        .stage-label {{
            font-size: 1rem;
            color: #1a202c !important;
            font-weight: 700;
        }}

        .stage-label.active {{
            color: #6366f1 !important;
            font-weight: 900;
            font-size: 1.1rem;
        }}

        /* ------------------------------------
        SECTION DIVIDER
        ------------------------------------*/
        .section-divider {{
            height: 4px;
            background: linear-gradient(90deg, transparent 0%, #6366f1 20%, #8b5cf6 50%, #d946ef 80%, transparent 100%);
            margin: 3rem 0;
            border: none;
            border-radius: 2px;
        }}

        /* ------------------------------------
        OPTIMIZATION SPINNER
        ------------------------------------*/
        .optimization-container {{
            text-align: center;
            padding: 5rem 2rem;
            background: white;
            border-radius: {radius_lg};
            box-shadow: {card_shadow};
            border: 4px solid #e2e8f0;
        }}

        .spinner {{
            width: 100px;
            height: 100px;
            margin: 0 auto 2.5rem;
            border: 8px solid #e2e8f0;
            border-top-color: #6366f1;
            border-right-color: #8b5cf6;
            border-bottom-color: #d946ef;
            border-radius: 50%;
            animation: spin 1.2s linear infinite;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        .optimization-text {{
            font-size: 2.2rem;
            font-weight: 900;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
        }}

        .optimization-subtext {{
            font-size: 1.2rem;
            color: #64748b !important;
            font-weight: 600;
        }}

        /* ------------------------------------
        DATAFRAME STYLING
        ------------------------------------*/
        .stDataFrame {{
            border: 3px solid #e2e8f0;
            border-radius: {radius};
            overflow: hidden;
            background: white;
        }}

        .stDataFrame thead tr th {{
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            border: none !important;
        }}

        /* ------------------------------------
        FILE UPLOADER
        ------------------------------------*/
        .uploadedFile {{
            border: 4px dashed #6366f1 !important;
            border-radius: {radius} !important;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%) !important;
        }}

        /* ------------------------------------
        INPUT FIELDS
        ------------------------------------*/
        .stNumberInput > div > div > input {{
            border: 2px solid #e2e8f0 !important;
            border-radius: {radius} !important;
            font-weight: 600 !important;
            color: #1a202c !important;
        }}

        .stNumberInput > div > div > input:focus {{
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        }}

        /* ------------------------------------
        EXPANDER
        ------------------------------------*/
        .streamlit-expanderHeader {{
            background: white !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: {radius} !important;
            font-weight: 700 !important;
            color: #1a202c !important;
        }}

        .streamlit-expanderHeader:hover {{
            background: #f8fafc !important;
            border-color: #6366f1 !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


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
    """Render wizard-style stage progress indicator with colors."""
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
        
        # Add connector with completion state
        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            connectors.append(f'<div class="stage-connector {connector_class}"></div>')

    # Interleave blocks and connectors
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
    """Render a colorful metric card in the specified column."""
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
    """Render a bold alert box with icon and message."""
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
    """Render a gradient divider line."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
