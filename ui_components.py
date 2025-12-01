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
CORPORATE LIGHT THEME CSS
============================= */
:root {
  --md-sys-color-primary: #0A74DA;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #E6F0FA;
  --md-sys-color-on-primary-container: #0A2E5C;

  --md-sys-color-secondary: #5A6F8E;
  --md-sys-color-on-secondary: #FFFFFF;
  --md-sys-color-secondary-container: #F0F4F8;
  --md-sys-color-on-secondary-container: #1D2939;

  --md-sys-color-surface: #FFFFFF;
  --md-sys-color-on-surface: #212529;
  --md-sys-color-surface-variant: #F1F3F5;
  --md-sys-color-on-surface-variant: #495057;

  --md-sys-color-background: #F9FAFB;
  --md-sys-color-on-background: #212529;

  --md-sys-color-outline: #CED4DA;
  --md-sys-color-outline-variant: #DEE2E6;

  --md-sys-color-success: #28A745;
  --md-sys-color-on-success: #FFFFFF;
  --md-sys-color-success-container: #DFF6E3;

  --md-sys-color-warning: #FFC107;
  --md-sys-color-on-warning: #212529;
  --md-sys-color-warning-container: #FFF3CD;

  --md-sys-color-error: #DC3545;
  --md-sys-color-on-error: #FFFFFF;
  --md-sys-color-error-container: #F8D7DA;

  /* Correct shape variables */
  --md-shape-corner-small: 8px;
  --md-shape-corner-medium: 12px;
  --md-shape-corner-large: 16px;
}

/* Global Styles */
.stApp, html, body {
  background: var(--md-sys-color-background) !important;
  font-family: 'Roboto', 'Segoe UI', system-ui, sans-serif;
  color: var(--md-sys-color-on-background);
}

/* =============================
BUTTONS — Gradient
============================= */
.stButton>button,
button[data-testid="stDownloadButton"] {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4) !important;
  color: var(--md-sys-color-on-primary) !important;
  border-radius: var(--md-shape-corner-large) !important;
  padding: 0.75rem 1.5rem !important;
  font-weight: 500 !important;
  font-size: 0.875rem !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
  text-transform: none !important;
  transition: all 0.2s ease !important;
}
.stButton>button:hover,
button[data-testid="stDownloadButton"]:hover {
  background: linear-gradient(135deg, #085BB5, #3D8CD9) !important;
}

/* =============================
Header — Gradient
============================= */
.app-header {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4);
  color: var(--md-sys-color-on-primary) !important;
  padding: 1rem 1.5rem;
  border-radius: var(--md-shape-corner-large);
  text-align: center;
}
.app-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 500;
}
.app-header p {
  opacity: 0.9;
  font-size: 0.95rem;
}

/* =============================
Cards
============================= */
.card, .metric-card, .stTabs {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.card-header {
  font-size: 1.25rem;
  font-weight: 500;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  margin-bottom: 1rem;
}

/* =============================
Alerts
============================= */
div[data-testid="stAlert"] {
  border-radius: var(--md-shape-corner-medium);
  padding: 1rem 1.5rem;
  margin: 1rem 0;
}
.alert-success { background: var(--md-sys-color-success-container); color: var(--md-sys-color-on-success); }
.alert-info { background: var(--md-sys-color-primary-container); color: var(--md-sys-color-on-primary-container); }
.alert-warning { background: var(--md-sys-color-warning-container); color: var(--md-sys-color-on-warning); }
.alert-error { background: var(--md-sys-color-error-container); color: var(--md-sys-color-on-error); }

/* =============================
Stage Progress
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
  align-items: center;
  width: 100%;
  gap: 1rem;
}

.stage-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  min-width: 100px;
  position: relative;
  z-index: 2;
}

.stage-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  border: 3px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface);
  transition: transform 0.4s ease, background-color 0.4s ease, border-color 0.4s ease;
}
.stage-circle.active {
  transform: scale(1.15);
  background: var(--md-sys-color-primary);
  border-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}
.stage-circle.completed {
  background: var(--md-sys-color-success);
  border-color: var(--md-sys-color-success);
  color: var(--md-sys-color-on-success);
}

.stage-label {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
}
.stage-label.active {
  color: var(--md-sys-color-on-surface);
  font-weight: 600;
}

.stage-connector {
  flex: 1;
  height: 4px;
  background: var(--md-sys-color-outline-variant);
  margin: 0 0.5rem;
  transition: background-color 0.4s ease;
}
.stage-connector.completed {
  background: var(--md-sys-color-success);
}

/* =============================
Tabs
============================= */
.stTabs {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium) !important;
  overflow: hidden;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--md-sys-color-surface-variant);
  border-radius: var(--md-shape-corner-medium) !important;
}

.stTabs [role="tab"] {
  flex: 1;
  text-align: center;
  font-weight: 600;
  padding: 0.75rem;
  border-radius: var(--md-shape-corner-small) !important;
  transition: background 0.3s ease, box-shadow 0.3s ease;
  border: none !important;
}

.stTabs [role="tab"]:nth-child(1)[aria-selected="true"] {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4) !important;
  color: #FFFFFF !important;
}

.stTabs [role="tab"]:nth-child(2)[aria-selected="true"] {
  background: linear-gradient(135deg, #28A745, #5DDC7A) !important;
  color: #FFFFFF !important;
}

.stTabs [role="tab"]:nth-child(3)[aria-selected="true"] {
  background: linear-gradient(135deg, #FFC107, #FFD76A) !important;
  color: #212529 !important;
}

.stTabs [role="tab"]:nth-child(4)[aria-selected="true"] {
  background: linear-gradient(135deg, #DC3545, #F08080) !important;
  color: #FFFFFF !important;
}

.stTabs [role="tab"]:not([aria-selected="true"]) {
  background: var(--md-sys-color-surface) !important;
  color: var(--md-sys-color-on-surface-variant) !important;
}

/* =============================
Metric Cards — Gradient Variants
============================= */

/* Base metric card styling */
.metric-card {
  border-radius: var(--md-shape-corner-medium) !important;
  padding: 1.5rem !important;
  text-align: center !important;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
  margin-bottom: 1rem !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  min-height: 120px !important;
}

.metric-card-blue {
  background: linear-gradient(135deg, #E6F0FA, #BBD7F5) !important;
}

.metric-card-green {
  background: linear-gradient(135deg, #DFF6E3, #AEE8C1) !important;
}

.metric-card-yellow {
  background: linear-gradient(135deg, #FFF3CD, #FFE29A) !important;
}

.metric-card-red {
  background: linear-gradient(135deg, #F8D7DA, #F1A2A9) !important;
}

.metric-label {
  font-size: 0.875rem !important;
  color: #495057 !important;
  font-weight: 600 !important;
  margin-bottom: 0.5rem !important;
  text-align: center !important;
  width: 100% !important;
}

.metric-value {
  font-size: 2rem !important;
  font-weight: 700 !important;
  color: #212529 !important;
  line-height: 1 !important;
  text-align: center !important;
  width: 100% !important;
}

/* =============================
Loading Spinner
============================= */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #E0E0E0;
  border-top: 4px solid #0A74DA;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 1rem auto;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.optimization-container {
  text-align: center;
  margin-bottom: 1rem;
}
.optimization-text {
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 0.5rem;
}
.optimization-subtext {
  font-size: 0.9rem;
  color: var(--md-sys-color-on-surface-variant);
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
    stages = [("📤","Upload"),("📄","Preview & Configure"),("📊","Results")]
    total = len(stages)
    current_stage = max(0, min(current_stage, total-1))
    html = '<div class="stage-row">'

    for idx,(icon,label) in enumerate(stages):
        status = "inactive"
        display_icon = icon
        if idx == current_stage:
            status = "active"
        elif idx < current_stage:
            status = "completed"
            display_icon = "✓"

        if idx == total-1 and current_stage == total-1:
            status = "completed"
            display_icon = "✓"

        html += f'<div class="stage-step">'
        html += f'<div class="stage-circle {status}">{display_icon}</div>'
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
def render_metric_card(label: str, value: str, col, card_index: int = 0):
    """Render a metric card with gradient background."""
    gradient_classes = [
        'metric-card-blue',
        'metric-card-green', 
        'metric-card-yellow',
        'metric-card-red'
    ]
    card_class = gradient_classes[card_index % 4] if card_index < 4 else 'metric-card'
    
    with col:
        st.markdown(
            f'''<div class="metric-card {card_class}">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>''',
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
