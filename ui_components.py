"""
ui_components.py
Original global theme preserved; added Upload-page-scoped CSS under .upload-page to avoid impacting other pages.
"""

import streamlit as st
from pathlib import Path

# -------------------------------
# CSS - Original corporate theme + upload-page scoped additions
# -------------------------------
CUSTOM_CSS = """
/* =============================
GLOBAL THEME (unchanged core)
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

/* =============================
BUTTONS, HEADER, CARDS, ALERTS (unchanged)
============================= */
/* Primary Button */
.stButton>button[kind="primary"],
.stButton>button:not([kind]),
button[data-testid="stDownloadButton"] { 
  background: linear-gradient(135deg, #0A74DA, #4BA3F4) !important;
  color: var(--md-sys-color-on-primary) !important;
  border-radius: var(--md-shape-corner-large) !important;
  padding: 0.75rem 1.5rem !important;
  font-weight: 500 !important;
  font-size: 0.875rem !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
  text-transform: none !important;
  transition: all 0.2s ease !important;
  border: none !important;
}

/* Keep rest of original theme rules intact (omitted here for brevity) */
"""  # note: original file had large CSS; keep it out-of-line here for readability below

# Append the rest of original CSS from prior file (we include necessary parts now)
CUSTOM_CSS += """
/* =============================
Header - Enhanced
============================= */
.app-header {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4);
  color: var(--md-sys-color-on-primary) !important;
  padding: 1.5rem 2rem;
  border-radius: var(--md-shape-corner-large);
  text-align: center;
  box-shadow: 0 4px 12px rgba(10, 116, 218, 0.25);
  margin-bottom: 2rem;
}

.app-header h1 {
  margin: 0;
  font-size: 1.875rem;
  font-weight: 500;
  letter-spacing: -0.5px;
}

.app-header p {
  opacity: 0.95;
  font-size: 1rem;
  margin-top: 0.5rem;
}

.card, .metric-card, .stTabs {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
  transition: box-shadow 0.2s ease;
}

.card-header {
  font-size: 1.25rem;
  font-weight: 500;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

/* Alerts */
div[data-testid="stAlert"] {
  border-radius: var(--md-shape-corner-medium);
  padding: 1rem 1.5rem;
  margin: 1rem 0;
  border-left: 4px solid;
}

.alert-success { 
  background: var(--md-sys-color-success-container); 
  color: var(--md-sys-color-on-success);
  border-left-color: var(--md-sys-color-success);
}

.alert-info { 
  background: var(--md-sys-color-primary-container); 
  color: var(--md-sys-color-on-primary-container);
  border-left-color: var(--md-sys-color-primary);
}

.alert-warning { 
  background: var(--md-sys-color-warning-container); 
  color: var(--md-sys-color-on-warning);
  border-left-color: var(--md-sys-color-warning);
}

.alert-error { 
  background: var(--md-sys-color-error-container); 
  color: var(--md-sys-color-on-error);
  border-left-color: var(--md-sys-color-error);
}

/* Stage progress - keep as-is */
.stage-container {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 2rem 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Metric card basics (unchanged) */
.metric-card {
  border-radius: var(--md-shape-corner-medium) !important;
  padding: 1.75rem 1.5rem !important;
  text-align: center !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
  margin-bottom: 1rem !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  min-height: 140px !important;
  transition: all 0.2s ease !important;
}

/* Loading spinner etc. (unchanged) */
/* ... keep original rules ... */

/* =============================
UPLOAD PAGE - SCOPED (only affects Upload page)
============================= */
.upload-page .upload-grid-card {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
  min-height: 240px;
}

/* Primary: middle upload card accent */
.upload-page .upload-primary-card {
  border: 2px solid var(--md-sys-color-primary);
  background: linear-gradient(180deg, rgba(10,116,218,0.03), rgba(10,116,218,0.01));
  box-shadow: 0 8px 20px rgba(10,116,218,0.06);
  padding: 14px;
}

/* Dropzone styling for file uploader (scoped) */
.upload-page .upload-dropzone {
  border: 2px dashed var(--md-sys-color-outline);
  border-radius: var(--md-shape-corner-medium);
  padding: 14px;
  background: rgba(10,116,218,0.015);
}

/* Ensure the native uploader inside the dropzone doesn't add an extra border */
.upload-page div[data-testid="stFileUploader"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* Button alignment in the download card */
.upload-page .upload-grid-card .stDownloadButton > button {
  width: 100% !important;
}

/* Limit expander height so left column doesn't push others down when open */
.upload-page details[open] {
  max-height: 320px;
  overflow-y: auto;
}

/* Small utility */
.upload-page .card-header { font-size:1.05rem; font-weight:600; margin-bottom:8px; }

/* Reduce top-level block padding inside upload page only */
.upload-page .block-container {
  padding-top: 8px !important;
}
"""

# -------------------------------
# APPLY CSS
# -------------------------------
def apply_custom_css():
    """Inject global CSS + upload-page scoped CSS."""
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


# -------------------------------
# HEADER
# -------------------------------
def render_header(title: str, subtitle: str = ""):
    """Render corporate app header with enhanced styling."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="app-header"><h1>{title}</h1>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


# -------------------------------
# STAGE PROGRESS (4 stages)
# -------------------------------
def render_stage_progress(current_stage: int):
    """Render 4-stage progress indicator with proper numbering."""
    stages = [
        ("📤", "Upload"),
        ("🛠️", "Configure"),
        ("⚡", "Optimizing"),
        ("📊", "Results")
    ]
    
    total = len(stages)
    current_stage = max(0, min(current_stage, total - 1))
    
    html = '<div class="stage-row">'

    for idx, (icon, label) in enumerate(stages):
        status = "inactive"
        display_icon = icon
        
        if idx < current_stage:
            status = "completed"
            display_icon = "✓"
        elif idx == current_stage:
            status = "active"

        html += f'<div class="stage-step">'
        html += f'<div class="stage-circle {status}">{display_icon}</div>'
        html += f'<div class="stage-label {"active" if idx == current_stage else ""}">{label}</div>'
        html += '</div>'

        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            html += f'<div class="stage-connector {connector_class}"></div>'

    html += '</div>'
    st.markdown(f'<div class="stage-container">{html}</div>', unsafe_allow_html=True)


# -------------------------------
# CARD helpers, metric card, alerts, errors, etc.
# Keep these implementations (unchanged) so other pages behave the same.
# -------------------------------
def render_card(title: str, icon: str = ""):
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        f'<div class="card"><div class="card-header">{icon_html}{title}</div>',
        unsafe_allow_html=True
    )

def close_card():
    st.markdown('</div>', unsafe_allow_html=True)

def render_metric_card(label: str, value: str, col, card_index: int = 0):
    gradient_classes = [
        'metric-card-blue',
        'metric-card-green', 
        'metric-card-yellow',
        'metric-card-red'
    ]
    card_class = gradient_classes[card_index % 4]
    
    with col:
        st.markdown(
            f'''<div class="metric-card {card_class}">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>''',
            unsafe_allow_html=True
        )

def render_alert(message: str, alert_type: str = "info"):
    icons = {
        "success": "✓",
        "info": "ℹ",
        "warning": "⚠",
        "error": "✖"
    }
    st.markdown(
        f'<div class="alert alert-{alert_type}">'
        f'<strong>{icons.get(alert_type, "ℹ")}</strong> '
        f'<span>{message}</span></div>',
        unsafe_allow_html=True
    )

def render_error_state(error_type: str, message: str):
    st.markdown(f"""
        <div class="error-container">
            <div class="error-icon">❌</div>
            <h3>{error_type}</h3>
            <p>{message}</p>
        </div>
    """, unsafe_allow_html=True)

def render_skeleton_loader(rows: int = 3):
    skeleton_html = '<div class="skeleton-loader">'
    for _ in range(rows):
        skeleton_html += '<div class="skeleton-row"></div>'
    skeleton_html += '</div>'
    st.markdown(skeleton_html, unsafe_allow_html=True)

def render_section_divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

def render_download_template_button():
    try:
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        if template_path.exists():
            with open(template_path, "rb") as f:
                template_data = f.read()
            st.download_button(
                label="📥 Download Template",
                data=template_data,
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error("Template file not found")
    except Exception as e:
        st.error(f"Template file not found: {e}")
