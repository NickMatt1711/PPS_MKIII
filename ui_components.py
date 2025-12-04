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
  --md-sys-color-error: #BA1A1A;
}

/* Base Styles */
body {
    background-color: var(--md-sys-color-background);
    color: var(--md-sys-color-on-background);
}

/* Headers */
.main-title {
    color: var(--md-sys-color-primary);
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid var(--md-sys-color-primary);
}

h2 { /* Streamlit subheader */
    color: var(--md-sys-color-on-secondary-container);
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}

h3 {
    color: var(--md-sys-color-secondary);
    font-weight: 500;
}

/* Card for Upload Stage */
.upload-card {
    background-color: var(--md-sys-color-surface);
    border-radius: 1rem;
    padding: 2rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--md-sys-color-outline);
    transition: box-shadow 0.3s ease;
}

.upload-card:hover {
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);
}

/* File Uploader Custom Styling */
/* This specific rule targets the Streamlit internal structure for the file uploader */
div.stFileUploader {
    border: 2px dashed var(--md-sys-color-primary-container) !important;
    padding: 2rem !important;
    border-radius: 0.75rem !important;
    background-color: var(--md-sys-color-surface-variant) !important;
    transition: background-color 0.3s ease;
}

/* Buttons */
.stButton>button {
    border-radius: 0.5rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton>button[data-testid="stSidebarButton"] {
    /* Special styling for sidebar buttons if needed */
}

/* Primary Button Styling */
.stButton>button[kind="primary"] {
    background-color: var(--md-sys-color-primary);
    color: var(--md-sys-color-on-primary);
    border: none;
}

.stButton>button[kind="primary"]:hover {
    background-color: #085FA3; /* Darker shade */
    box-shadow: 0 2px 8px rgba(10, 116, 218, 0.4);
}

/* Secondary/Default Button Styling */
.stButton>button:not([kind="primary"]) {
    border: 1px solid var(--md-sys-color-outline);
    background-color: var(--md-sys-color-surface);
    color: var(--md-sys-color-on-surface);
}

/* Info and Success Boxes (Alerts) */
.stAlert div[data-testid="stAlert"] {
    border-radius: 0.5rem;
    padding: 1rem 1.25rem;
}

/* Streamlit Tabs */
.stTabs [data-testid="stTab"] {
    font-weight: 600;
    border-radius: 0.5rem 0.5rem 0 0;
}

/* Dataframes */
.stDataFrame {
    border: 1px solid var(--md-sys-color-outline);
    border-radius: 0.75rem;
}

/* Skeleton Loader Animation */
@keyframes loading-animation {
    0% { background-position: -200px 0; }
    100% { background-position: 200px 0; }
}

.skeleton-loader {
    width: 100%;
    padding: 1rem 0;
}

.skeleton-row {
    height: 1.2rem;
    margin-bottom: 0.5rem;
    border-radius: 0.25rem;
    background: linear-gradient(90deg, var(--md-sys-color-surface-variant) 25%, #EFEFF1 50%, var(--md-sys-color-surface-variant) 75%);
    background-size: 400% 100%;
    animation: loading-animation 1.5s infinite;
}

/* Section Divider */
.section-divider {
    height: 1px;
    background-color: var(--md-sys-color-outline);
    margin: 1.5rem 0;
}

"""

def apply_custom_css():
    """Applies the custom CSS to the Streamlit app."""
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


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
# DOWNLOAD TEMPLATE
# -------------------------------
def render_download_template_button():
    """Render download template button."""
    try:
        # NOTE: This assumes the template file is correctly located relative to this script
        # In a typical environment, this path might need adjustment based on deployment
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        # Placeholder for demonstration, as the template file is not provided
        # I'll create a dummy file for this code to run without errors in a test environment
        
        # In a real environment, the template file should exist.
        # Since I don't have the template, I will create a minimal one in memory to prevent an error.
        import pandas as pd
        from io import BytesIO

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        pd.DataFrame({'Config': ['PlantA', 'PlantB']}).to_excel(writer, sheet_name='Configuration', index=False)
        pd.DataFrame({'Product': ['G1', 'G2']}).to_excel(writer, sheet_name='Inventory', index=False)
        pd.DataFrame({'Date': ['2025-01-01'], 'Demand': [100]}).to_excel(writer, sheet_name='Demand', index=False)
        pd.DataFrame({'Date': ['2025-01-01'], 'Prod': [50]}).to_excel(writer, sheet_name='Production', index=False)
        writer.close()
        template_data = output.getvalue()
        
        st.download_button(
            label="📥 Download Template",
            data=template_data,
            file_name="polymer_production_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="secondary" # Make the download button secondary to the primary "Process" button
        )
        
    except Exception as e:
        # Fallback error message if template generation/loading fails
        st.error(f"Error loading template file: {e}")
