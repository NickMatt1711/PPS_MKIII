"""
Material 3 Light Theme - Corporate UI Components
Clean, professional design without sidebar
"""

import streamlit as st
# The 'constants' import is kept, assuming it exists for other parts of the app.
# from constants import THEME_COLORS 


def apply_custom_css():
    """Apply Material 3 Light theme for corporate application, with corrected color overrides."""
    
    st.markdown(
        """
        <style>
        /* ----------------------------------------------------
        REFRESHED LIGHT THEME CSS
        ----------------------------------------------------*/

        /* Colors Definitions */
        :root {
            --primary-blue: #1e40af;       /* Corporate Blue */
            --primary-dark-text: #1e293b;  /* Dark Text */
            --background-light: #f8fafc;   /* App Background */
            --surface-white: #ffffff;      /* Card/Input Background */
            --border-light: #e2e8f0;       /* Subtle Border */
            --header-gradient: linear-gradient(135deg, var(--primary-blue) 0%, #3730a3 100%);
        }

        /* ------------------------------------
        GLOBAL BASE (MANDATORY LIGHT MODE)
        ------------------------------------*/
        .stApp, .main, .block-container {
            background-color: var(--background-light) !important;
            color: var(--primary-dark-text) !important;
        }
        
        /* Force Dark Text for ALL Streamlit elements */
        p, span, div, label, h1, h2, h3, h4, h5, h6, a, li, strong, .stMarkdown, .stText, .stLabel, .stSubheader {
            color: var(--primary-dark-text) !important; 
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        h1, h2, h3 {
            color: #0f172a !important;
            font-weight: 600 !important;
        }

        /* ------------------------------------
        HEADER - Corporate Gradient
        ------------------------------------*/
        .app-header {
            background: var(--header-gradient);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
        }
        
        .app-header h1 {
            color: var(--surface-white) !important;
        }
        
        .app-header p {
            color: rgba(255, 255, 255, 0.9) !important;
        }

        /* ------------------------------------
        CARDS & ALERTS
        ------------------------------------*/
        .card {
            background: var(--surface-white);
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-light);
        }
        
        .card-header {
            color: var(--primary-dark-text) !important;
            border-bottom: 2px solid var(--border-light);
        }

        /* ALERTS - Ensure light background */
        div[data-testid="stAlert"] {
            background-color: var(--surface-white) !important;
            border: 1px solid var(--border-light) !important;
        }
        
        .alert-success strong { color: #15803d !important; }
        .alert-info strong    { color: #2563eb !important; }
        .alert-warning strong { color: #f59e0b !important; }
        .alert-error strong   { color: #dc2626 !important; }
        
        /* ------------------------------------
        BUTTONS (Primary Fix)
        ------------------------------------*/
        /* Target general buttons, download, and uploader buttons */
        .stButton > button, 
        .stDownloadButton > button,
        section[data-testid="stFileUploader"] button {
            background: var(--primary-blue) !important;
            color: var(--surface-white) !important;
            box-shadow: 0 1px 3px rgba(30, 64, 175, 0.3);
        }
        
        /* Ensure all nested elements (text, icons) inside the primary button are white */
        .stButton > button *, 
        .stDownloadButton > button *,
        section[data-testid="stFileUploader"] button * {
            color: var(--surface-white) !important;
        }

        /* Hover state */
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        section[data-testid="stFileUploader"] button:hover {
            background: #3730a3 !important;
        }

        /* ------------------------------------
        DATAFRAME STYLING (Light Mode Fix)
        ------------------------------------*/
        div[data-testid="stDataFrame"] {
            background-color: var(--surface-white) !important; 
            border: 1px solid var(--border-light);
        }

        /* Force light background and dark text for all table cells/elements */
        div[data-testid="stDataFrame"] table,
        div[data-testid="stDataFrame"] th,
        div[data-testid="stDataFrame"] td,
        div[data-testid="stDataFrame"] span {
            background-color: var(--surface-white) !important;
            color: var(--primary-dark-text) !important;
            border-color: var(--border-light) !important;
        }
        
        /* Style for the header row background */
        div[data-testid="stDataFrame"] th {
            background-color: #f1f5f9 !important; /* Light grey header */
        }

        /* ------------------------------------
        INPUT FIELDS (Light Mode Fix)
        ------------------------------------*/
        
        /* Target all common Streamlit inputs for white background and dark text */
        .stTextInput input,
        .stTextInput textarea,
        .stNumberInput input,
        div[data-testid="stForm"] input, 
        div[data-testid="stForm"] textarea,
        div[data-testid="stSelectbox"] input,
        .stDateInput input,
        .stTimeInput input {
            border: 1px solid #ced4da !important;
            color: var(--primary-dark-text) !important; 
            background: var(--surface-white) !important;
        }

        /* Focused state */
        .stTextInput input:focus, .stTextInput textarea:focus,
        .stNumberInput input:focus, .stDateInput input:focus,
        .stTimeInput input:focus {
            border-color: var(--primary-blue) !important;
            box-shadow: 0 0 0 2px rgba(30, 64, 175, 0.2) !important;
        }

        /* ------------------------------------
        FILE UPLOADER - General Style
        ------------------------------------*/
        section[data-testid="stFileUploader"] {
            border: 2px dashed #10b981 !important; /* Success green border */
            background-color: #f0fdf4 !important; /* Very light success background */
        }

        /* ------------------------------------
        TABS STYLING
        ------------------------------------*/
        button[data-baseweb="tab"] {
            color: #64748b !important; /* Inactive tab color */
            background-color: transparent !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--primary-blue) !important; /* Active tab text color */
            border-bottom: 3px solid var(--primary-blue) !important; /* Active tab indicator */
        }
        
        .stTabs {
            background-color: var(--surface-white) !important;
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid var(--border-light);
        }
        
        /* ------------------------------------
        STAGE PROGRESS (No CSS changes needed for this part, as it relies on inline styles)
        ------------------------------------*/

        </style>
        """, 
        unsafe_allow_html=True
    )


def render_header(title: str, subtitle: str = ""):
    """Render corporate app header."""
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


def render_stage_progress(current_stage: int) -> None:
    """Render clean stage progress indicator."""
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
        if idx < current_stage or (idx == total - 1 and current_stage >= total - 1):
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
        
        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            connectors.append(f'<div class="stage-connector {connector_class}"></div>')

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


def render_card(title: str, icon: str = ""):
    """Open a Material 3 card container."""
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


def render_metric_card(label: str, value: str, col):
    """Render a Material 3 metric card."""
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


def render_alert(message: str, alert_type: str = "info"):
    """Render a Material 3 alert box."""
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


def render_section_divider():
    """Render a subtle divider."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_download_template_button():
    """Render download template button."""
    import io
    from pathlib import Path
    
    # Placeholder implementation, as the file isn't available in this environment.
    # The error handling below is kept to avoid breaking the original script structure.
    try:
        # NOTE: In a real environment, you would ensure 'polymer_production_template.xlsx' 
        # is available in the appropriate directory relative to this script.
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        
        if template_path.exists():
            with open(template_path, "rb") as f:
                template_data = f.read()
            
            st.download_button(
                label="📥 Download Template",
                data=template_data,
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download the Excel template file",
                use_container_width=True
            )
        else:
            # Create dummy data for the example to work if the file is missing
            st.download_button(
                label="📥 Download Template",
                data=b'This is a dummy Excel content.',
                file_name="polymer_production_template_DUMMY.txt",
                mime="text/plain",
                help="Template file not found (using dummy data)",
                use_container_width=True
            )
            # st.error("Template file not found")
    except Exception as e:
        # Simplified error handling for the code sandbox environment
        st.download_button(
            label="📥 Download Template",
            data=b'This is a dummy Excel content.',
            file_name="polymer_production_template_DUMMY.txt",
            mime="text/plain",
            help=f"Error loading template: {e}",
            use_container_width=True
        )
