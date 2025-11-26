"""
M3-inspired Streamlit theme + modern CSS targeting current Streamlit DOM.

Usage:
    from ui.theme_m3_streamlit import apply_custom_css, render_theme_toggle, render_header, ...
    apply_custom_css(is_dark_mode=(st.session_state.get('ss_theme','light')=='dark'))
"""

from typing import Any, Dict, Tuple
import streamlit as st

# ---------------------------
# THEME COLORS (guaranteed CSS strings)
# ---------------------------
# Material-3-inspired tokens (examples). Adjust to taste.
THEME_COLORS: Dict[str, Any] = {
    # Primaries
    "primary_light": "#0B63D6",  # primary on light
    "primary_light_container": "#DDEEFF",
    "primary_dark": "#58A6FF",
    "primary_dark_container": "#0B3B66",

    # Success / warning / error
    "success": "#0F9D58",
    "success_light": "#E8F6EA",
    "warning": "#F59E0B",
    "warning_light": "#FFF4E5",
    "error": "#D64545",
    "error_light": "#FBEAEA",

    # Surfaces / backgrounds
    "background_light": "#FFFFFF",
    "surface_light": "#F5F7FA",
    "card_light": "#FFFFFF",
    "on_surface_light": "#111827",
    "outline_light": "#D1D5DB",

    "background_dark": "#0B1220",
    "surface_dark": "#10151E",
    "card_dark": "#0F1724",
    "on_surface_dark": "#E6EEF6",
    "outline_dark": "#273042",
}

# ---------------------------
# Helpers
# ---------------------------
def _to_css_color(val: Any) -> str:
    """
    Convert common Python representations to CSS color strings.
    - '#rrggbb' or 'rgb(...)' strings pass through.
    - 3-tuple ints -> hex.
    - otherwise: str(val)
    """
    if isinstance(val, tuple) and len(val) == 3 and all(isinstance(c, int) for c in val):
        return "#{:02x}{:02x}{:02x}".format(*val)
    s = str(val).strip()
    # quick sanity: if it's like "0x..." or dict repr, fallback to transparent to avoid CSS injection errors
    if s.startswith("{") or s.startswith("(") and not s.startswith("rgb"):
        return "transparent"
    return s

def _palette(is_dark_mode: bool) -> Dict[str, str]:
    """Return sanitized palette tokens for light or dark theme."""
    if is_dark_mode:
        return {
            "--m3-bg": _to_css_color(THEME_COLORS["background_dark"]),
            "--m3-surface": _to_css_color(THEME_COLORS["surface_dark"]),
            "--m3-card": _to_css_color(THEME_COLORS["card_dark"]),
            "--m3-on-surface": _to_css_color(THEME_COLORS["on_surface_dark"]),
            "--m3-outline": _to_css_color(THEME_COLORS["outline_dark"]),
            "--m3-primary": _to_css_color(THEME_COLORS["primary_dark"]),
            "--m3-primary-container": _to_css_color(THEME_COLORS["primary_dark_container"]) if "primary_dark_container" in THEME_COLORS else _to_css_color(THEME_COLORS["primary_dark"]),
            "--m3-success": _to_css_color(THEME_COLORS["success"]),
            "--m3-success-light": _to_css_color(THEME_COLORS["success_light"]),
            "--m3-warning": _to_css_color(THEME_COLORS["warning"]),
            "--m3-warning-light": _to_css_color(THEME_COLORS["warning_light"]),
            "--m3-error": _to_css_color(THEME_COLORS["error"]),
            "--m3-error-light": _to_css_color(THEME_COLORS["error_light"]),
        }
    else:
        return {
            "--m3-bg": _to_css_color(THEME_COLORS["background_light"]),
            "--m3-surface": _to_css_color(THEME_COLORS["surface_light"]),
            "--m3-card": _to_css_color(THEME_COLORS["card_light"]),
            "--m3-on-surface": _to_css_color(THEME_COLORS["on_surface_light"]),
            "--m3-outline": _to_css_color(THEME_COLORS["outline_light"]),
            "--m3-primary": _to_css_color(THEME_COLORS["primary_light"]),
            "--m3-primary-container": _to_css_color(THEME_COLORS["primary_light_container"]) if "primary_light_container" in THEME_COLORS else _to_css_color(THEME_COLORS["primary_light"]),
            "--m3-success": _to_css_color(THEME_COLORS["success"]),
            "--m3-success-light": _to_css_color(THEME_COLORS["success_light"]),
            "--m3-warning": _to_css_color(THEME_COLORS["warning"]),
            "--m3-warning-light": _to_css_color(THEME_COLORS["warning_light"]),
            "--m3-error": _to_css_color(THEME_COLORS["error"]),
            "--m3-error-light": _to_css_color(THEME_COLORS["error_light"]),
        }

# ---------------------------
# Apply Custom CSS (updated selectors)
# ---------------------------
def apply_custom_css(is_dark_mode: bool = False) -> None:
    """
    Inject namespaced M3-inspired CSS using current Streamlit DOM selectors.
    Call early in your app (before complex layout) so styles apply to child elements.
    """
    tokens = _palette(is_dark_mode)
    # static layout tokens
    radius = "12px"
    card_shadow = "0 6px 18px rgba(2,6,23,0.25)"
    hover_shadow = "0 10px 30px rgba(2,6,23,0.32)"

    # Build CSS variables string
    vars_css = "\n".join(f"    {k}: {v};" for k, v in tokens.items())

    css = f"""
    <style>
    /* Define theme variables scoped to the app container to avoid clobbering Streamlit internals */
    [data-testid="stAppViewContainer"] {{
        /* attach variables to the app container */
    }}
    [data-testid="stAppViewContainer"] :root, 
    [data-testid="stAppViewContainer"] {{
{vars_css}
        --m3-radius: {radius};
        --m3-card-shadow: {card_shadow};
        --m3-hover-shadow: {hover_shadow};
    }}

    /* Ensure background / text colors apply to Streamlit primary containers */
    [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] .css-1outpf7, [data-testid="stAppViewContainer"] .css-1e5imcs {{
        background: var(--m3-bg) !important;
        color: var(--m3-on-surface) !important;
    }}

    /* Make markdown/card blocks pick up our card variables even when Streamlit wraps them */
    [data-testid="stMarkdown"] .card,
    [data-testid="stMarkdown"] .app-header,
    [data-testid="stMarkdown"] .metric-card,
    [data-testid="stMarkdown"] .stage-container {{
        box-sizing: border-box;
    }}

    /* App header */
    .app-header {{
        background: linear-gradient(135deg, var(--m3-primary), var(--m3-primary-container));
        color: white;
        padding: 1.6rem;
        border-radius: var(--m3-radius);
        margin-bottom: 1.6rem;
        text-align: center;
        box-shadow: var(--m3-card-shadow);
    }}
    .app-header h1{{ margin:0; font-size:1.9rem; font-weight:600; }}

    /* Card */
    [data-testid="stMarkdown"] .card {{
        background: var(--m3-card);
        color: var(--m3-on-surface);
        padding: 1.25rem;
        border-radius: var(--m3-radius);
        border: 1px solid var(--m3-outline);
        box-shadow: var(--m3-card-shadow);
        margin-bottom: 1rem;
    }}
    [data-testid="stMarkdown"] .card-header {{ font-size:1.05rem; font-weight:600; margin-bottom:0.75rem; }}

    /* Metric card */
    [data-testid="stMarkdown"] .metric-card {{
        background: linear-gradient(135deg, var(--m3-primary), var(--m3-primary-container));
        color: white;
        padding: 1rem;
        border-radius: calc(var(--m3-radius) - 2px);
        text-align: center;
        box-shadow: var(--m3-card-shadow);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    [data-testid="stMarkdown"] .metric-card:hover {{ transform: translateY(-4px); box-shadow: var(--m3-hover-shadow); }}

    .metric-value{{ font-size:1.6rem; font-weight:700; }}
    .metric-label{{ font-size:0.85rem; opacity:0.95; }}

    /* Alerts (use safe tokens) */
    [data-testid="stMarkdown"] .alert {{
        padding: 0.9rem;
        border-radius: 10px;
        margin-bottom: 0.85rem;
        display:flex;
        gap:0.6rem;
        align-items:flex-start;
        border-left-width:5px;
        border-left-style:solid;
    }}
    .alert-success{{ background: var(--m3-success-light); border-left-color: var(--m3-success); color: var(--m3-on-surface); }}
    .alert-info{{ background: var(--m3-primary-container); border-left-color: var(--m3-primary); color: var(--m3-on-surface); }}
    .alert-warning{{ background: var(--m3-warning-light); border-left-color: var(--m3-warning); color: var(--m3-on-surface); }}
    .alert-error{{ background: var(--m3-error-light); border-left-color: var(--m3-error); color: var(--m3-on-surface); }}

    /* Tabs: robust selection using data-testid and aria */
    [data-testid="stTabs"] {{ background: var(--m3-surface); padding: 0.4rem; border-radius: var(--m3-radius); display:flex; gap:8px; }}
    [data-testid="stTabs"] button {{
        background: var(--m3-card);
        border: 1px solid var(--m3-outline);
        padding: 0.55rem 1rem;
        border-radius: 10px;
        font-weight:600;
        flex: none;
    }}
    [data-testid="stTabs"] button[aria-selected="true"] {{
        background: var(--m3-primary) !important;
        color: white !important;
        border-color: var(--m3-primary);
    }}

    /* Buttons: target by test id then nested button */
    [data-testid="stButton"] button {{
        background: var(--m3-primary);
        color: white;
        padding: 0.55rem 1.1rem;
        font-weight:600;
        border-radius: 10px;
        border: none;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }}
    [data-testid="stButton"] button:hover {{
        background: var(--m3-primary-container);
        box-shadow: var(--m3-hover-shadow);
        transform: translateY(-2px);
    }}

    /* Stage progress: responsive, robust */
    [data-testid="stMarkdown"] .stage-container {{
        padding: 0.9rem;
        background: var(--m3-card);
        border-radius: var(--m3-radius);
        border:1px solid var(--m3-outline);
        box-shadow: var(--m3-card-shadow);
        margin-bottom: 1rem;
    }}
    [data-testid="stMarkdown"] .stage-row {{
        display:flex; align-items:center; gap:10px; flex-wrap:nowrap;
    }}
    [data-testid="stMarkdown"] .stage-step {{ flex:1; text-align:center; position:relative; min-width:64px; }}
    [data-testid="stMarkdown"] .stage-connector {{ height:2px; background:var(--m3-outline); flex:1; margin:0 6px; border-radius:2px; }}
    [data-testid="stMarkdown"] .stage-circle {{
        width:44px; height:44px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 0.25rem auto; font-weight:600;
        background: var(--m3-outline); color: var(--m3-on-surface);
    }}
    [data-testid="stMarkdown"] .stage-circle.active {{ background: var(--m3-primary); color: white; }}
    [data-testid="stMarkdown"] .stage-circle.completed {{ background: var(--m3-success); color: white; }}
    [data-testid="stMarkdown"] .stage-label {{ font-size:0.85rem; color: var(--m3-on-surface); }}
    [data-testid="stMarkdown"] .stage-label.active {{ color: var(--m3-primary); font-weight:600; }}

    /* Section divider */
    [data-testid="stMarkdown"] .section-divider {{ height:1px; background:var(--m3-outline); margin:1.5rem 0; }}

    /* Small adjustments to avoid Streamlit default focus outlines for our custom buttons */
    [data-testid="stButton"] button:focus {{ outline: 2px solid rgba(0,0,0,0.08); outline-offset: 2px; }}

    /* Ensure images inside our markdown cards scale properly */
    [data-testid="stMarkdown"] .card img {{ max-width:100%; height:auto; border-radius:8px; }}

    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

# ---------------------------
# Small component helpers (use the new token names)
# ---------------------------
SS_THEME = "ss_theme"  # session state key for theme

def render_theme_toggle():
    """Simple toggle button that flips theme state in session."""
    if SS_THEME not in st.session_state:
        st.session_state[SS_THEME] = "light"
    current = st.session_state[SS_THEME]
    label = "🌙 Dark" if current == "light" else "☀️ Light"
    _, col = st.columns([8, 1])
    with col:
        if st.button(label):
            st.session_state[SS_THEME] = "dark" if current == "light" else "light"
            st.experimental_rerun()

def render_header(title: str, subtitle: str = ""):
    subtitle_html = f"<p style='margin:0.25rem 0 0 0; opacity:0.92'>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
        <div class="app-header">
            <h1>{title}</h1>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)

def render_card(title: str, icon: str = ""):
    icon_html = f"{icon} " if icon else ""
    st.markdown(f"""
        <div class="card">
            <div class="card-header">{icon_html}{title}</div>
    """, unsafe_allow_html=True)

def close_card():
    st.markdown("</div>", unsafe_allow_html=True)

def render_metric_card(label: str, value: str, col):
    with col:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)

def render_alert(message: str, alert_type: str = "info"):
    icons = {"success": "✔", "info": "ℹ", "warning": "⚠", "error": "✕"}
    alert_class = {
        "success": "alert-success",
        "info": "alert-info",
        "warning": "alert-warning",
        "error": "alert-error"
    }.get(alert_type, "alert-info")
    st.markdown(f"""
        <div class="alert {alert_class}">
            <strong style="font-size:1.1rem">{icons.get(alert_type,"ℹ")}</strong>
            <div style="line-height:1.1">{message}</div>
        </div>
    """, unsafe_allow_html=True)

def render_section_divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

def render_stage_progress(current_stage: int):
    stages = [("1", "Upload"), ("2", "Preview & Configure"), ("3", "Results")]
    total = len(stages)
    # clamp to valid stage index range [0, total-1]
    current_stage = max(0, min(int(current_stage), total - 1))
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
        active_label_class = "active" if idx == current_stage else ""
        blocks.append(f'''
            <div class="stage-step">
                <div class="stage-circle {status}">{icon}</div>
                <div class="stage-label {active_label_class}">{label}</div>
            </div>
        ''')
    html = ""
    for i, block in enumerate(blocks):
        html += block
        if i < len(blocks) - 1:
            html += '<div class="stage-connector"></div>'
    st.markdown(f'<div class="stage-container"><div class="stage-row">{html}</div></div>', unsafe_allow_html=True)

# ---------------------------
# Auto-apply convenience (call at top of app)
# ---------------------------
def apply_theme_from_session():
    """Convenience: set up theme based on session state key SS_THEME."""
    mode = st.session_state.get(SS_THEME, "light")
    apply_custom_css(is_dark_mode=(mode == "dark"))
