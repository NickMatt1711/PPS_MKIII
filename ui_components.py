"""
ui_components.py
Global theme preserved. Added Upload-page-scoped CSS and small UI helpers (pills) for the Upload page.
"""

import streamlit as st
from pathlib import Path

# -------------------------------
# CSS - Material 3 Light Theme (original) + upload-page scoped additions
# -------------------------------
CUSTOM_CSS = """
/* =============================
CORPORATE LIGHT THEME CSS - ENHANCED (original preserved)
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

/* ... (original global CSS from your file is preserved — omitted here for brevity) ... */

/* =============================
UPLOAD PAGE - SCOPED STYLES (only affects the Upload page)
============================= */
.upload-page {
  /* small top spacing for the block */
  padding-bottom: 8px;
}

/* Unified small card used only in upload page */
.upload-page .upload-grid-card {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 14px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  min-height: 220px;
  display:flex;
  flex-direction:column;
  justify-content:flex-start;
}

/* Primary (middle) card accent */
.upload-page .upload-primary-card {
  border: 2px solid var(--md-sys-color-primary);
  background: linear-gradient(180deg, rgba(10,116,218,0.03), rgba(10,116,218,0.01));
  box-shadow: 0 10px 30px rgba(10,116,218,0.05);
}

/* Dropzone area */
.upload-page .upload-dropzone {
  border: 2px dashed var(--md-sys-color-outline);
  border-radius: var(--md-shape-corner-medium);
  padding: 12px;
  background: rgba(10,116,218,0.01);
  margin-top: 8px;
}

/* Pills used in template card */
.upload-page .pill {
  display:inline-block;
  padding:6px 10px;
  background:#f1f5f9;
  border-radius:999px;
  font-size:13px;
  color:#213547;
  border:1px solid #eef2f7;
}

/* Align card headers across columns */
.upload-page .card-header {
  font-size:1.05rem;
  font-weight:600;
  margin-bottom:10px;
}

/* Slight visual separator between the three cards (subtle) */
.upload-page .upload-grid-card:not(.upload-primary-card) {
  /* keep supporting cards slightly lighter */
  background: #fff;
}

/* Smaller helper text styling */
.upload-page .small-muted {
  color:#6c757d;
  font-size:13px;
}

/* Reduce top padding for block container scoped to upload page */
.upload-page .block-container {
  padding-top: 6px !important;
}

/* Ensure the expander content looks like a reference drawer */
.upload-page details[open] > div {
  background: #fbfdfe;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #f0f2f5;
}

/* small horizontal rule styling inside upload page */
.upload-page hr { border: none; border-top: 1px solid #eee; margin:10px 0; }

/* make sure native uploader doesn't add big borders inside dropzone */
.upload-page div[data-testid="stFileUploader"] {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  margin: 0 !important;
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
# STAGE PROGRESS (unchanged)
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
# Re-use existing component helpers (unchanged)
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
