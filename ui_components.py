"""
ui_components.py
Material 3 Light Theme - Corporate UI Components
All UI elements and CSS are self-contained in this file.
"""

import streamlit as st
from pathlib import Path

# -------------------------------
# CSS - Material 3 Light Theme
# -------------------------------
CUSTOM_CSS = """
/* =============================
   COLOR TOKENS
   ============================= */
:root {
    --md-sys-color-primary: #6750A4;
    --md-sys-color-on-primary: #FFFFFF;
    --md-sys-color-primary-container: #EADDFF;
    --md-sys-color-on-primary-container: #21005D;
    --md-sys-color-secondary: #625B71;
    --md-sys-color-on-secondary: #FFFFFF;
    --md-sys-color-secondary-container: #E8DEF8;
    --md-sys-color-on-secondary-container: #1D192B;
    --md-sys-color-surface: #FFFBFE;
    --md-sys-color-on-surface: #1C1B1F;
    --md-sys-color-surface-variant: #E7E0EC;
    --md-sys-color-on-surface-variant: #49454F;
    --md-sys-color-background: #F8FAFC;
    --md-sys-color-on-background: #1C1B1F;
    --md-sys-color-outline: #79747E;
    --md-sys-color-outline-variant: #C4C7C5;
    --md-sys-color-error: #B3261E;
    --md-sys-color-on-error: #FFFFFF;
    --md-sys-color-error-container: #F9DEDC;
    --md-sys-color-success: #0D652D;
    --md-sys-color-on-success: #FFFFFF;
    --md-sys-color-success-container: #A7F0BA;
    --md-sys-color-warning: #7C5800;
    --md-sys-color-on-warning: #FFFFFF;
    --md-sys-color-warning-container: #FFDEA3;
    --md-shape-corner-small: 8px;
    --md-shape-corner-medium: 12px;
    --md-shape-corner-large: 16px;
}

/* =============================
   GLOBAL STYLES
   ============================= */
.stApp, html, body {
    background: var(--md-sys-color-background) !important;
    font-family: 'Roboto', 'Segoe UI', system-ui, sans-serif;
    color: var(--md-sys-color-on-background);
}

* {
    color: var(--md-sys-color-on-background);
}

/* =============================
   BUTTON FIXES
   ============================= */
.stButton>button, button[data-testid="stDownloadButton"] {
    background: var(--md-sys-color-primary) !important;
    color: var(--md-sys-color-on-primary) !important;
    border-radius: var(--md-shape-corner-large) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    text-transform: none !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
    min-height: 40px !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover, button[data-testid="stDownloadButton"]:hover {
    background: rgba(103,80,164,0.85) !important;
    transform: translateY(-1px) !important;
}

/* =============================
   TABLE / DATAFRAME LIGHT MODE
   ============================= */
.stDataFrame, .css-1d391kg, .stTable td, .stTable th {
    background-color: var(--md-sys-color-surface) !important;
    color: var(--md-sys-color-on-surface) !important;
    border-color: var(--md-sys-color-outline-variant) !important;
}
.stDataFrame th {
    font-weight: 600 !important;
}

/* =============================
   HEADER
   ============================= */
.app-header {
    background: var(--md-sys-color-primary);
    color: var(--md-sys-color-on-primary) !important;
    padding: 2rem 1.5rem;
    border-radius: var(--md-shape-corner-large);
    text-align: center;
}

.app-header h1 {
    margin: 0;
    font-size: 2.25rem;
    font-weight: 400;
    letter-spacing: 0.5px;
}

.app-header p {
    color: var(--md-sys-color-on-primary) !important;
    opacity: 0.9;
    margin-top: 0.5rem;
    font-size: 1.1rem;
}

/* =============================
   STAGE / PROGRESS INDICATOR
   ============================= */
.stage-container {
    background: var(--md-sys-color-surface);
    border-radius: var(--md-shape-corner-medium);
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}

.stage-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    position: relative;
}

.stage-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
    z-index: 2;
}

.stage-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    font-size: 0.875rem;
    border: 2px solid;
    background: var(--md-sys-color-surface);
    transition: all 0.2s ease;
}

.stage-label {
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.5rem;
    text-align: center;
    color: var(--md-sys-color-on-surface-variant);
}

.stage-circle.inactive {
    border-color: var(--md-sys-color-outline-variant);
    color: var(--md-sys-color-outline);
}

.stage-circle.active {
    background: var(--md-sys-color-primary);
    border-color: var(--md-sys-color-primary);
    color: var(--md-sys-color-on-primary);
}

.stage-circle.completed {
    background: var(--md-sys-color-success);
    border-color: var(--md-sys-color-success);
    color: var(--md-sys-color-on-success);
}

.stage-label.active {
    color: var(--md-sys-color-on-surface);
    font-weight: 600;
}

.stage-connector {
    position: absolute;
    top: 15px;
    left: 50%;
    right: 50%;
    height: 2px;
    background: var(--md-sys-color-outline-variant);
    z-index: 1;
}

.stage-connector.completed {
    background: var(--md-sys-color-success);
}

/* =============================
   CARDS / METRICS / BUTTONS
   ============================= */
.card, .metric-card, .stTabs {
    background: var(--md-sys-color-surface);
    border-radius: var(--md-shape-corner-medium);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}

.card-header {
    color: var(--md-sys-color-on-surface) !important;
    font-size: 1.25rem;
    font-weight: 500;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--md-sys-color-outline-variant);
}


/* =============================
   ALERTS
   ============================= */
div[data-testid="stAlert"] {
    border-radius: var(--md-shape-corner-medium);
    border: none;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
    padding: 1rem 1.5rem;
    margin: 1rem 0;
}

.alert-success {
    background: var(--md-sys-color-success-container);
    color: var(--md-sys-color-on-success-container);
}

.alert-info {
    background: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
}

.alert-warning {
    background: var(--md-sys-color-warning-container);
    color: var(--md-sys-color-on-warning-container);
}

.alert-error {
    background: var(--md-sys-color-error-container);
    color: var(--md-sys-color-on-error);
}

/* =============================
   DIVIDERS
   ============================= */
.section-divider {
    margin: 2rem 0;
    border: none;
    border-top: 1px solid var(--md-sys-color-outline-variant);
}
"""

# -------------------------------
# APPLY CSS
# -------------------------------
def apply_custom_css():
    """Inject Material 3 corporate theme."""
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


# -------------------------------
# HEADER
# -------------------------------
def render_header(title: str, subtitle: str = ""):
    """Render corporate app header."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="app-header"><h1>{title}</h1>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


# -------------------------------
# STAGE PROGRESS
# -------------------------------
def render_stage_progress(current_stage: int):
    stages = [("1","Upload"),("2","Preview & Configure"),("3","Results")]
    total = len(stages)
    current_stage = max(0, min(current_stage, total-1))
    html = '<div class="stage-row">'
    
    for idx,(num,label) in enumerate(stages):
        status = "inactive"
        icon = num
        if idx == current_stage:
            status = "active"
        elif idx < current_stage:
            status = "completed"
            icon = "✓"
        
        html += f'<div class="stage-step">'
        html += f'<div class="stage-circle {status}">{icon}</div>'
        html += f'<div class="stage-label {"active" if idx==current_stage else ""}">{label}</div>'
        html += '</div>'
        
        if idx < total-1:
            connector_class = "completed" if idx < current_stage else ""
            html += f'<div class="stage-connector {connector_class}"></div>'
    
    html += '</div>'
    st.markdown(f'<div class="stage-container">{html}</div>', unsafe_allow_html=True)


# -------------------------------
# CARD
# -------------------------------
def render_card(title: str, icon: str = ""):
    icon_html = f"{icon} " if icon else ""
    st.markdown(f'<div class="card"><div class="card-header">{icon_html}{title}</div>', unsafe_allow_html=True)

def close_card():
    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------
# METRIC CARD
# -------------------------------
def render_metric_card(label: str, value: str, col):
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',
            unsafe_allow_html=True
        )


# -------------------------------
# ALERT
# -------------------------------
def render_alert(message: str, alert_type: str = "info"):
    icons = {"success":"✓","info":"ℹ","warning":"⚠","error":"✖"}
    st.markdown(f'<div class="alert alert-{alert_type}"><strong>{icons.get(alert_type,"ℹ")}</strong> <span>{message}</span></div>', unsafe_allow_html=True)


# -------------------------------
# SECTION DIVIDER
# -------------------------------
def render_section_divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# -------------------------------
# DOWNLOAD TEMPLATE
# -------------------------------
def render_download_template_button():
    try:
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        if template_path.exists():
            with open(template_path, "rb") as f:
                template_data = f.read()
            st.download_button(
                label="🔥 Download Template",
                data=template_data,
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error("Template file not found")
    except Exception as e:
        st.error(f"Template file not found: {e}")
