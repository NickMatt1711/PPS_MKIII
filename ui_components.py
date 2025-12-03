"""
ui_components.py (updated)
- Desktop-first theme
- Emphasize upload card
- Consistent icons
- Cleaner stage progress
- Uploader styling & spacing improvements
"""

import streamlit as st
from pathlib import Path

# -------------------------------
# CSS - Desktop-first Corporate Theme
# -------------------------------
CUSTOM_CSS = """
:root {
  --md-sys-color-primary: #0A74DA;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #E6F0FA;
  --md-sys-color-on-primary-container: #0A2E5C;
  --md-sys-color-surface: #FFFFFF;
  --md-sys-color-on-surface: #212529;
  --md-sys-color-surface-variant: #F1F3F5;
  --md-sys-color-outline: #CED4DA;
  --md-shape-corner-small: 8px;
  --md-shape-corner-medium: 12px;
  --md-shape-corner-large: 16px;
}

/* App background & font */
.stApp, html, body {
  background: #F9FAFB !important;
  font-family: 'Inter', 'Roboto', system-ui, sans-serif;
  color: var(--md-sys-color-on-surface);
}

/* Header */
.app-header {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4);
  color: var(--md-sys-color-on-primary) !important;
  padding: 1.5rem 2rem;
  border-radius: var(--md-shape-corner-large);
  text-align: center;
  box-shadow: 0 4px 12px rgba(10,116,218,0.18);
  margin-bottom: 1.5rem;
}
.app-header h1 { margin: 0; font-size: 1.75rem; font-weight: 600; }
.app-header p { margin-top: .35rem; opacity: 0.94; }

/* Generic card */
.card {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
.card-header { font-size: 1.05rem; font-weight: 600; margin-bottom: .5rem; }

/* Upload card specifics */
.upload-card { padding: 1rem; min-height: 280px; }
.upload-card-primary {
  border: 2px solid var(--md-sys-color-primary);
  background: linear-gradient(180deg, rgba(10,116,218,0.04), rgba(10,116,218,0.02));
  box-shadow: 0 6px 18px rgba(10,116,218,0.06);
}

/* File uploader - desktop-focused */
div[data-testid="stFileUploader"], .stFileUploader {
  border: 2px dashed var(--md-sys-color-outline);
  padding: 1rem;
  border-radius: var(--md-shape-corner-medium);
  background: rgba(10,116,218,0.02);
}
div[data-testid="stFileUploader"] > label { font-weight: 600; }

/* Stage progress (4 stages) */
.stage-container {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stage-row { display:flex; align-items:center; gap:1rem; width:100%; }
.stage-step { display:flex; flex-direction:column; align-items:center; flex:1; min-width:90px; position:relative; z-index:2; }
.stage-circle { width:48px; height:48px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.1rem; border:3px solid var(--md-sys-color-outline); background:var(--md-sys-color-surface); color:var(--md-sys-color-on-surface); }
.stage-circle.active { background:var(--md-sys-color-primary); color:var(--md-sys-color-on-primary); transform:scale(1.06); box-shadow:0 6px 16px rgba(10,116,218,0.12); border-color:var(--md-sys-color-primary); }
.stage-circle.completed { background:#28A745; color:#fff; border-color:#28A745; }
.stage-label { margin-top:.6rem; font-size:0.85rem; font-weight:600; color:#495057; text-align:center; }
.stage-label.active { color:var(--md-sys-color-on-surface); }

/* Connector */
.stage-connector { flex:1; height:4px; background:var(--md-sys-color-outline); border-radius:2px; }
.stage-connector.completed { background: #28A745; }

/* Metric cards */
.metric-card { border-radius:var(--md-shape-corner-medium); padding:1.2rem; text-align:center; min-height:120px; display:flex; flex-direction:column; justify-content:center; }
.metric-label { font-size:0.8rem; font-weight:700; color:#495057; text-transform:uppercase; margin-bottom:0.5rem; }
.metric-value { font-size:1.9rem; font-weight:800; color:#212529; }

/* Alerts */
div[data-testid="stAlert"] { border-radius:8px; padding:0.85rem 1rem; margin:0.75rem 0; border-left:4px solid; }
.alert-success { background: #DFF6E3; color:#0E5B2D; border-left-color:#28A745; }
.alert-info { background:#E6F0FA; color:#074A8A; border-left-color:var(--md-sys-color-primary); }
.alert-warning { background:#FFF3CD; color:#7A5A00; border-left-color:#FFC107; }
.alert-error { background:#F8D7DA; color:#7A0E10; border-left-color:#DC3545; }

/* Optimization container */
.optimization-container { text-align:center; padding:1.5rem; }

/* Small utility */
.section-divider { height:1px; background:var(--md-sys-color-outline); margin:1.25rem 0; }

/* Desktop-only spacing for better alignment */
body { -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; }
"""

# -------------------------------
# APPLY CSS
# -------------------------------
def apply_custom_css():
    """Inject corporate desktop-first theme."""
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


# -------------------------------
# HEADER
# -------------------------------
def render_header(title: str, subtitle: str = ""):
    """Render app header."""
    subtitle_html = f"<p style='margin-top:6px; opacity:.95'>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div class="app-header"><h1>{title}</h1>{subtitle_html}</div>', unsafe_allow_html=True)


# -------------------------------
# STAGE PROGRESS (4 stages)
# -------------------------------
def render_stage_progress(current_stage: int):
    """Render 4-stage progress indicator (Upload, Preview, Optimizing, Results)."""
    stages = [
        ("📤", "Upload"),
        ("🔎", "Preview"),
        ("⚡", "Optimizing"),
        ("📊", "Results")
    ]
    total = len(stages)
    current_stage = max(0, min(current_stage, total - 1))
    html = '<div class="stage-row">'
    for idx, (icon, label) in enumerate(stages):
        status = ""
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
# METRIC CARD
# -------------------------------
def render_metric_card(label: str, value: str, col, card_index: int = 0):
    """Render a compact metric card."""
    with col:
        st.markdown(
            f'''<div class="card metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>''',
            unsafe_allow_html=True
        )


# -------------------------------
# ALERT
# -------------------------------
def render_alert(message: str, alert_type: str = "info"):
    """Render styled alert."""
    icons = {
        "success": "✓",
        "info": "ℹ",
        "warning": "⚠",
        "error": "✖"
    }
    st.markdown(
        f'<div class="alert alert-{alert_type}"><strong>{icons.get(alert_type, "ℹ")}</strong> <span style="margin-left:8px">{message}</span></div>',
        unsafe_allow_html=True
    )


# -------------------------------
# ERROR STATE
# -------------------------------
def render_error_state(error_type: str, message: str):
    """Render error block."""
    st.markdown(f"""
        <div class="card" style="background:#F8D7DA;">
            <div style="font-size:1.4rem; font-weight:700;">❌ {error_type}</div>
            <div style="margin-top:6px; color:#7A0E10;">{message}</div>
        </div>
    """, unsafe_allow_html=True)


# -------------------------------
# SECTION DIVIDER
# -------------------------------
def render_section_divider():
    """Render section divider line."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# -------------------------------
# DOWNLOAD TEMPLATE
# -------------------------------
def render_download_template_button():
    """Render download template button."""
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
