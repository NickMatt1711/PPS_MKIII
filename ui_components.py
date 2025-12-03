"""
ui_components.py
Material 3 Light Theme - Enhanced UX with improved responsiveness and accessibility
"""

import streamlit as st
from pathlib import Path

# -------------------------------
# CSS - Material 3 Light Theme (Enhanced)
# -------------------------------
CUSTOM_CSS = """
/* =============================
CORPORATE LIGHT THEME CSS - ENHANCED
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
BUTTONS - Enhanced Hierarchy
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

.stButton>button[kind="primary"]:hover,
.stButton>button:not([kind]):hover,
button[data-testid="stDownloadButton"]:hover {
  background: linear-gradient(135deg, #085BB5, #3D8CD9) !important;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
  transform: translateY(-1px);
}

/* Secondary Button */
.stButton>button[kind="secondary"] {
  background: var(--md-sys-color-surface) !important;
  color: var(--md-sys-color-primary) !important;
  border: 2px solid var(--md-sys-color-primary) !important;
  border-radius: var(--md-shape-corner-large) !important;
  padding: 0.75rem 1.5rem !important;
  font-weight: 500 !important;
  font-size: 0.875rem !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
  transition: all 0.2s ease !important;
}

.stButton>button[kind="secondary"]:hover {
  background: var(--md-sys-color-primary-container) !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
}

/* Template download button enhancement */
.template-download-btn {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4) !important;
  color: white !important;
  border-radius: var(--md-shape-corner-large) !important;
  padding: 1rem 2rem !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(10, 116, 218, 0.25) !important;
}

.template-download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(10, 116, 218, 0.35) !important;
}

/* Focus states for accessibility */
.stButton>button:focus-visible,
button[data-testid="stDownloadButton"]:focus-visible {
  outline: 3px solid #4BA3F4 !important;
  outline-offset: 2px !important;
}

/* Disabled state */
.stButton>button:disabled {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
}

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

/* =============================
Upload Page Enhancements
============================= */
.upload-section {
  padding: 1rem 0;
}

.upload-card {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-large);
  padding: 2.5rem;
  margin: 1.5rem 0;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border: 2px solid var(--md-sys-color-outline-variant);
}

.upload-card:hover {
  border-color: var(--md-sys-color-primary);
  transition: border-color 0.3s ease;
}

.file-info-card {
  background: linear-gradient(135deg, var(--md-sys-color-primary-container) 0%, #E6F0FA 100%);
  border-radius: var(--md-shape-corner-medium);
  padding: 1.5rem;
  margin: 1rem 0;
}

.file-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.file-info-row:last-child {
  border-bottom: none;
}

.file-info-label {
  color: var(--md-sys-color-on-surface-variant);
  font-weight: 500;
  font-size: 0.9rem;
}

.file-info-value {
  color: var(--md-sys-color-on-surface);
  font-weight: 600;
  font-size: 0.95rem;
}

.upload-zone {
  border: 3px dashed var(--md-sys-color-outline);
  border-radius: var(--md-shape-corner-large);
  padding: 3rem 2rem;
  text-align: center;
  margin: 20px 0;
  background: var(--md-sys-color-surface-variant);
  transition: all 0.3s ease;
}

.upload-zone:hover {
  border-color: var(--md-sys-color-primary);
  background: var(--md-sys-color-primary-container);
}

.upload-zone-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  color: var(--md-sys-color-primary);
}

.upload-zone-title {
  color: var(--md-sys-color-on-surface);
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.upload-zone-subtitle {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
}

.upload-zone-note {
  color: #aaa;
  font-size: 0.8rem;
  margin-top: 1rem;
}

/* =============================
Cards - Enhanced
============================= */
.card, .metric-card, .stTabs {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

.card-header {
  font-size: 1.25rem;
  font-weight: 500;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

/* =============================
Alerts - Enhanced with Actionable Steps
============================= */
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

.alert-fix-steps {
  background: var(--md-sys-color-surface-variant) !important;
  border-left-color: #6c757d !important;
  margin-top: 1rem;
  padding: 1rem !important;
}

.alert-fix-steps ul {
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
}

.alert-fix-steps li {
  margin-bottom: 0.25rem;
}

/* =============================
Stage Progress - Enhanced (4 stages)
============================= */
.stage-container {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 2rem 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
  min-width: 80px;
  position: relative;
  z-index: 2;
}

.stage-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  border: 3px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stage-circle.active {
  transform: scale(1.15);
  background: var(--md-sys-color-primary);
  border-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  box-shadow: 0 4px 12px rgba(10, 116, 218, 0.4);
}

.stage-circle.completed {
  background: var(--md-sys-color-success);
  border-color: var(--md-sys-color-success);
  color: var(--md-sys-color-on-success);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.stage-label {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  text-align: center;
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
  transition: background-color 0.3s ease;
  border-radius: 2px;
}

.stage-connector.completed {
  background: var(--md-sys-color-success);
}

/* =============================
Tabs - Enhanced with dynamic colors
============================= */
.stTabs {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium) !important;
  overflow: hidden;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--md-sys-color-surface-variant);
  border-radius: var(--md-shape-corner-medium) !important;
}

.stTabs [role="tab"] {
  flex: 1;
  text-align: center;
  font-weight: 600;
  padding: 0.875rem 1rem;
  border-radius: var(--md-shape-corner-small) !important;
  transition: all 0.2s ease;
  border: none !important;
}

.stTabs [role="tab"]:nth-child(1)[aria-selected="true"] {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4) !important;
  color: #FFFFFF !important;
  box-shadow: 0 2px 8px rgba(10, 116, 218, 0.3);
}

.stTabs [role="tab"]:nth-child(2)[aria-selected="true"] {
  background: linear-gradient(135deg, #28A745, #5DDC7A) !important;
  color: #FFFFFF !important;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.stTabs [role="tab"]:nth-child(3)[aria-selected="true"] {
  background: linear-gradient(135deg, #FFC107, #FFD76A) !important;
  color: #212529 !important;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
}

.stTabs [role="tab"]:nth-child(4)[aria-selected="true"] {
  background: linear-gradient(135deg, #DC3545, #F08080) !important;
  color: #FFFFFF !important;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.stTabs [role="tab"]:not([aria-selected="true"]) {
  background: var(--md-sys-color-surface) !important;
  color: var(--md-sys-color-on-surface-variant) !important;
}

.stTabs [role="tab"]:not([aria-selected="true"]):hover {
  background: var(--md-sys-color-surface-variant) !important;
}

/* =============================
Metric Cards - Enhanced with hover effects
============================= */
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

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15) !important;
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
  margin-bottom: 0.75rem !important;
  text-align: center !important;
  width: 100% !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 2.25rem !important;
  font-weight: 700 !important;
  color: #212529 !important;
  line-height: 1 !important;
  text-align: center !important;
  width: 100% !important;
}

/* =============================
Loading States - Enhanced
============================= */
.spinner {
  width: 48px;
  height: 48px;
  border: 5px solid #E0E0E0;
  border-top: 5px solid #0A74DA;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 1.5rem auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.optimization-container {
  text-align: center;
  margin: 2rem auto;
  padding: 2rem;
}

.optimization-text {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1rem;
  color: var(--md-sys-color-on-surface);
}

.optimization-subtext {
  font-size: 1rem;
  color: var(--md-sys-color-on-surface-variant);
  margin-top: 0.5rem;
}

/* Skeleton Loader */
.skeleton-loader {
  padding: 1rem;
}

.skeleton-row {
  height: 40px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  margin-bottom: 12px;
  border-radius: 8px;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* =============================
Error States - Enhanced
============================= */
.error-container {
  text-align: center;
  padding: 3rem 2rem;
  background: var(--md-sys-color-error-container);
  border-radius: var(--md-shape-corner-medium);
  margin: 2rem 0;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-container h3 {
  color: var(--md-sys-color-error);
  margin-bottom: 0.5rem;
}

.error-container p {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1rem;
}

.validation-issues-container {
  border: 2px solid var(--md-sys-color-error);
  border-radius: var(--md-shape-corner-medium);
  padding: 1.5rem;
  margin: 1rem 0;
  background: var(--md-sys-color-error-container);
}

/* =============================
Section Divider
============================= */
.section-divider {
  height: 1px;
  background: var(--md-sys-color-outline-variant);
  margin: 2rem 0;
}

/* =============================
Requirements Section
============================= */
.requirements-section {
  background: var(--md-sys-color-surface-variant);
  border-radius: var(--md-shape-corner-medium);
  padding: 1.5rem;
  margin: 1.5rem 0;
}

.requirements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.requirement-card {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-small);
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.requirement-card h4 {
  margin-top: 0;
  color: var(--md-sys-color-primary);
  font-size: 1rem;
  margin-bottom: 0.75rem;
}

.requirement-card ul {
  margin: 0;
  padding-left: 1.25rem;
}

.requirement-card li {
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
  color: var(--md-sys-color-on-surface-variant);
}

.format-requirements {
  background: var(--md-sys-color-surface);
  border-left: 4px solid var(--md-sys-color-primary);
  padding: 1rem 1.5rem;
  margin: 1rem 0;
  border-radius: 0 var(--md-shape-corner-small) var(--md-shape-corner-small) 0;
}

/* =============================
Responsive Design
============================= */
@media (max-width: 768px) {
  .stage-row {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .stage-connector {
    width: 4px;
    height: 40px;
    margin: 0.5rem 0;
  }
  
  .metric-card {
    margin-bottom: 1rem !important;
  }
  
  .app-header h1 {
    font-size: 1.5rem;
  }
  
  .app-header {
    padding: 1.25rem 1.5rem;
  }
  
  .upload-card {
    padding: 1.5rem;
  }
  
  .upload-zone {
    padding: 2rem 1rem;
  }
  
  .requirements-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .stage-circle {
    width: 44px;
    height: 44px;
    font-size: 1.1rem;
  }
  
  .stage-label {
    font-size: 0.75rem;
  }
  
  .metric-value {
    font-size: 1.75rem !important;
  }
  
  .upload-zone-icon {
    font-size: 2.5rem;
  }
  
  .upload-zone-title {
    font-size: 1.1rem;
  }
}

/* =============================
Data Tables Enhancement
============================= */
.dataframe-container {
  border-radius: var(--md-shape-corner-medium);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* =============================
Accessibility Enhancements
============================= */
.skip-to-content {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  padding: 8px 16px;
  text-decoration: none;
  border-radius: 0 0 4px 0;
  z-index: 100;
}

.skip-to-content:focus {
  top: 0;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .stage-circle {
    border-width: 4px;
  }
  
  .stButton>button {
    border: 2px solid currentColor !important;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
"""

# -------------------------------
# APPLY CSS
# -------------------------------
def apply_custom_css():
    """Inject Material 3 corporate theme with enhanced UX."""
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
def render_stage_progress(current_stage: int, status_message: str = ""):
    """Render 4-stage progress indicator with optional status message."""
    stages = [
        ("📤", "Upload", "Upload production data"),
        ("🛠️", "Configure", "Set optimization parameters"),
        ("⚡", "Optimizing", "Running production optimization"),
        ("📊", "Results", "View optimization results")
    ]
    
    total = len(stages)
    current_stage = max(0, min(current_stage, total - 1))
    
    html = '<div class="stage-row">'

    for idx, (icon, label, _) in enumerate(stages):
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
    
    # Add status message if provided
    if status_message:
        html += f"""
        <div style="text-align: center; margin-top: 1rem; padding: 1rem; 
                    background: var(--md-sys-color-surface-variant); 
                    border-radius: var(--md-shape-corner-small);">
            <strong>🔄 {status_message}</strong>
        </div>
        """
    
    st.markdown(f'<div class="stage-container">{html}</div>', unsafe_allow_html=True)


# -------------------------------
# CARD
# -------------------------------
def render_card(title: str, icon: str = ""):
    """Render card container with optional icon."""
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        f'<div class="card"><div class="card-header">{icon_html}{title}</div>',
        unsafe_allow_html=True
    )

def close_card():
    """Close card container."""
    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------
# METRIC CARD (Enhanced with hover)
# -------------------------------
def render_metric_card(label: str, value: str, col, card_index: int = 0):
    """Render a metric card with gradient background and hover effect."""
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


# -------------------------------
# ALERT with Fix Steps
# -------------------------------
def render_alert(message: str, alert_type: str = "info", fix_steps: list = None):
    """Render styled alert with optional fix steps."""
    icons = {
        "success": "✓",
        "info": "ℹ",
        "warning": "⚠",
        "error": "✖"
    }
    
    alert_html = f'''
    <div class="alert alert-{alert_type}">
        <strong>{icons.get(alert_type, "ℹ")}</strong> 
        <span>{message}</span>
    </div>
    '''
    
    if fix_steps:
        steps_html = "<ul>"
        for step in fix_steps:
            steps_html += f"<li>{step}</li>"
        steps_html += "</ul>"
        
        alert_html += f'''
        <div class="alert alert-fix-steps">
            <strong>🔧 How to fix:</strong>
            {steps_html}
        </div>
        '''
    
    st.markdown(alert_html, unsafe_allow_html=True)


# -------------------------------
# ERROR STATE
# -------------------------------
def render_error_state(error_type: str, message: str):
    """Render enhanced error state with icon."""
    st.markdown(f"""
        <div class="error-container">
            <div class="error-icon">❌</div>
            <h3>{error_type}</h3>
            <p>{message}</p>
        </div>
    """, unsafe_allow_html=True)


# -------------------------------
# VALIDATION ISSUES CONTAINER
# -------------------------------
def render_validation_issues(errors: list, warnings: list = None):
    """Render validation issues with actionable fix steps."""
    if errors:
        with st.expander("❌ Validation Issues Found", expanded=True):
            st.markdown('<div class="validation-issues-container">', unsafe_allow_html=True)
            
            for error in errors:
                st.error(f"**Error:** {error}")
            
            st.markdown("""
            **🔧 How to fix:**
            1. Download the template again for correct structure
            2. Check all required sheets are present (Plant, Inventory, Demand)
            3. Verify column names match exactly
            4. Ensure no missing values in required fields
            5. Check date formats are valid Excel dates
            6. Verify numeric values are valid numbers
            """)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    if warnings:
        for warning in warnings:
            st.warning(warning)


# -------------------------------
# SKELETON LOADER
# -------------------------------
def render_skeleton_loader(rows: int = 3):
    """Render skeleton loader for loading states."""
    skeleton_html = '<div class="skeleton-loader">'
    for _ in range(rows):
        skeleton_html += '<div class="skeleton-row"></div>'
    skeleton_html += '</div>'
    st.markdown(skeleton_html, unsafe_allow_html=True)


# -------------------------------
# SECTION DIVIDER
# -------------------------------
def render_section_divider():
    """Render section divider line."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# -------------------------------
# DOWNLOAD TEMPLATE BUTTON
# -------------------------------
def render_download_template_button():
    """Render download template button with enhanced styling."""
    try:
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        if template_path.exists():
            with open(template_path, "rb") as f:
                template_data = f.read()
            
            st.download_button(
                label="📥 Download Excel Template",
                data=template_data,
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="download_template"
            )
        else:
            st.error("⚠️ Template file not found")
    except Exception as e:
        st.error(f"⚠️ Template file not found: {e}")


# -------------------------------
# RENDER FILE SUMMARY
# -------------------------------
def render_file_summary(uploaded_file):
    """Render detailed file information after upload."""
    if uploaded_file:
        import os
        
        st.markdown("### 📄 File Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="file-info-card">
                <div class="file-info-row">
                    <span class="file-info-label">File Name</span>
                    <span class="file-info-value">{uploaded_file.name}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
            st.markdown(f"""
            <div class="file-info-card">
                <div class="file-info-row">
                    <span class="file-info-label">File Size</span>
                    <span class="file-info-value">{file_size:.2f} MB</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="file-info-card">
                <div class="file-info-row">
                    <span class="file-info-label">Type</span>
                    <span class="file-info-value">Excel (.xlsx)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add a preview button
        if st.button("🔍 Preview File Contents", type="secondary", use_container_width=True):
            st.session_state["wizard_stage"] = 1  # STAGE_PREVIEW
            st.rerun()


# -------------------------------
# RENDER REQUIREMENTS SECTION
# -------------------------------
def render_requirements_section():
    """Render file requirements section."""
    st.markdown("### 📋 File Requirements")
    
    st.markdown('<div class="requirements-section">', unsafe_allow_html=True)
    
    st.markdown('<div class="requirements-grid">', unsafe_allow_html=True)
    
    # Required Sheets
    st.markdown("""
    <div class="requirement-card">
        <h4>✅ Required Sheets</h4>
        <ul>
            <li><strong>Plant</strong>: Production lines & capacities</li>
            <li><strong>Inventory</strong>: Product grades & constraints</li>
            <li><strong>Demand</strong>: Daily demand per grade</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Optional Sheets
    st.markdown("""
    <div class="requirement-card">
        <h4>📊 Optional Sheets</h4>
        <ul>
            <li><strong>Transition_PlantName</strong>: Grade transition rules</li>
            <li>Multiple transition sheets supported</li>
            <li>One sheet per production line</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Format requirements
    st.markdown("""
    <div class="format-requirements">
        <strong>📝 Format Requirements:</strong><br>
        • Excel (.xlsx) format only<br>
        • Maximum file size: 200MB<br>
        • Dates must be in proper Excel date format<br>
        • All numeric values must be valid numbers<br>
        • Column names must match template exactly
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
