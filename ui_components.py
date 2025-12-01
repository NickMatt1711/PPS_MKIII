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
CUSTOM_CSS = """/* =============================
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

/* Buttons */
.stButton>button, button[data-testid="stDownloadButton"] {
  background: var(--md-sys-color-primary) !important;
  color: var(--md-sys-color-on-primary) !important;
  border-radius: var(--md-shape-corner-large) !important;
  padding: 0.75rem 1.5rem !important;
  font-weight: 500 !important;
  font-size: 0.875rem !important;
  text-transform: none !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
  transition: all 0.2s ease !important;
}
.stButton>button:hover, button[data-testid="stDownloadButton"]:hover {
  background: #085BB5 !important;
}

/* Header */
.app-header {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary) !important;
  padding: 2rem 1.5rem;
  border-radius: var(--md-shape-corner-large);
  text-align: center;
}
.app-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 500;
}
.app-header p {
  opacity: 0.9;
  font-size: 1rem;
}

/* Cards */
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

/* Alerts */
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
FINAL POLISHED UI
============================= */

/* Header Resized */
.app-header {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary) !important;
  padding: 1rem 1.5rem; /* Reduced padding */
  border-radius: var(--md-shape-corner-large);
  text-align: center;
}
.app-header h1 {
  margin: 0;
  font-size: 1.75rem; /* Reduced size */
  font-weight: 500;
}
.app-header p {
  opacity: 0.9;
  font-size: 0.95rem;
}

/* Stage Container */
.stage-container {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}

/* Stage Row Alignment */
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
.stage-circle.completed::after {
  content: '';
  font-size: 1.4rem;
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


/* Tabs equally distributed */
.stTabs [role="tablist"] {
  display: flex;
  justify-content: space-between;
  width: 100%;
}
.stTabs [role="tab"] {
  flex: 1;
  text-align: center;
  font-weight: 600;
  padding: 0.75rem;
  transition: background-color 0.3s ease;
}

/* Different colors for up to 4 tabs when selected */
.stTabs [role="tab"]:nth-child(1)[aria-selected="true"] {
  background-color: #0A74DA; /* Blue */
  color: #FFFFFF;
}
.stTabs [role="tab"]:nth-child(2)[aria-selected="true"] {
  background-color: #28A745; /* Green */
  color: #FFFFFF;
}
.stTabs [role="tab"]:nth-child(3)[aria-selected="true"] {
  background-color: #FFC107; /* Amber */
  color: #212529;
}
.stTabs [role="tab"]:nth-child(4)[aria-selected="true"] {
  background-color: #DC3545; /* Red */
  color: #FFFFFF;
}

/* Metric cards with different background colors */
.metric-card:nth-child(1) {
  background-color: #E6F0FA; /* Light Blue */
}
.metric-card:nth-child(2) {
  background-color: #DFF6E3; /* Light Green */
}
.metric-card:nth-child(3) {
  background-color: #FFF3CD; /* Light Amber */
}
.metric-card:nth-child(4) {
  background-color: #F8D7DA; /* Light Red */
}
.metric-card {
  border-radius: var(--md-shape-corner-medium);
  padding: 1rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.metric-label {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}
.metric-value {
  font-size: 1.25rem;
  font-weight: 600;
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
