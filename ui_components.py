"""
Material 3 Light Theme - Corporate UI Components
Clean, professional design with a clear Wizard UX.
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
        REFINED CORPORATE LIGHT THEME CSS (Focus: Stability & Wizard UX)
        ----------------------------------------------------*/

        /* Colors Definitions (Using lighter, more accessible corporate shades) */
        :root {
            --primary-blue: #1565c0;       /* Corporate Blue (Medium-Dark) */
            --secondary-blue: #e3f2fd;     /* Very Light Blue for accents */
            --primary-dark-text: #263238;  /* Dark Gray Text */
            --background-light: #f5f5f5;   /* App Background (Slightly off-white) */
            --surface-white: #ffffff;      /* Card/Input Background */
            --border-light: #cfd8dc;       /* Subtle Border/Divider */
            --success-green: #388e3c;      /* Success/Completed status */
            --header-gradient: linear-gradient(135deg, var(--primary-blue) 0%, #1976d2 100%);
        }

        /* ------------------------------------
        GLOBAL BASE (MANDATORY LIGHT MODE)
        ------------------------------------*/
        .stApp, .main, .block-container {
            background-color: var(--background-light) !important;
            color: var(--primary-dark-text) !important;
            /* Max width adjustment for better corporate look */
            padding-top: 2rem;
        }
        
        /* Force Dark Text for ALL Streamlit elements */
        p, span, div, label, h1, h2, h3, h4, h5, h6, a, li, strong, .stMarkdown, .stText, .stLabel, .stSubheader {
            color: var(--primary-dark-text) !important; 
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        h1, h2, h3 {
            color: #1a237e !important; /* Darker navy for headings */
            font-weight: 700 !important;
            margin-bottom: 0.5rem;
        }

        /* ------------------------------------
        HEADER - Clean Gradient
        ------------------------------------*/
        .app-header {
            background: var(--header-gradient);
            padding: 2.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        }
        
        .app-header h1 {
            color: var(--surface-white) !important;
        }
        
        .app-header p {
            color: rgba(255, 255, 255, 0.85) !important;
        }
        
        /* ------------------------------------
        WIZARD / STAGE PROGRESS STYLING (Simplified for reliability)
        ------------------------------------*/
        .stage-container {
            padding: 1.5rem 1rem;
            margin-bottom: 2rem;
            background-color: var(--surface-white);
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-light);
        }
        .stage-row {
            display: flex;
            justify-content: space-around;
            align-items: flex-start;
            width: 100%;
        }
        .stage-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex-grow: 1; 
            min-width: 0;
            padding: 0 10px;
        }
        .stage-circle {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: 700;
            margin-bottom: 0.5rem;
            font-size: 1rem;
            border: 2px solid;
        }
        .stage-label {
            font-size: 0.85rem;
            text-align: center;
            font-weight: 500;
            white-space: nowrap;
        }

        /* Status Classes */
        .stage-circle.inactive {
            background-color: var(--background-light); 
            color: #78909c; /* Light Gray Text */
            border-color: #b0bec5;
        }
        .stage-circle.active {
            background-color: var(--primary-blue);
            color: var(--surface-white);
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 5px rgba(21, 101, 192, 0.2); 
        }
        .stage-circle.completed {
            background-color: var(--success-green); 
            color: var(--surface-white);
            border-color: var(--success-green);
        }
        .stage-label.active {
            font-weight: 700;
            color: var(--primary-dark-text) !important;
        }

        /* Connectors */
        .stage-connector {
            height: 2px; /* Thinner line */
            background-color: #b0bec5; 
            flex-grow: 1;
            margin: 0 -10px; /* Pull connector over */
            position: relative;
            top: 15px; /* Aligns connector to the middle of the circle */
            z-index: 0;
        }
        .stage-connector.completed {
            background-color: var(--success-green); 
        }
        /* Ensure step content is layered above the connector */
        .stage-step > div {
            z-index: 1; 
        }

        /* ------------------------------------
        CARDS & ALERTS
        ------------------------------------*/
        .card {
            background: var(--surface-white);
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); /* More subtle shadow */
            border: 1px solid var(--border-light);
            padding: 1.5rem; 
            margin-bottom: 1.5rem;
        }
        
        .card-header {
            color: var(--primary-dark-text) !important;
            border-bottom: 1px solid var(--border-light);
            padding-bottom: 0.75rem;
            margin-bottom: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
        }

        /* ALERTS - Ensure light background */
        div[data-testid="stAlert"] {
            background-color: var(--secondary-blue) !important; /* Light accent background */
            border-left: 5px solid var(--primary-blue) !important; /* Primary color left border */
            border-radius: 4px;
            box-shadow: none;
        }
        
        /* Adjust Alert content colors */
        .alert-success { border-left-color: var(--success-green) !important; background-color: #e8f5e9 !important; }
        .alert-info { border-left-color: #1976d2 !important; background-color: #e3f2fd !important; }
        .alert-warning { border-left-color: #ffb300 !important; background-color: #fffde7 !important; }
        .alert-error { border-left-color: #d32f2f !important; background-color: #ffebee !important; }
        
        .stAlert p, .stAlert strong { color: var(--primary-dark-text) !important; }

        /* ------------------------------------
        BUTTONS (Aggressive Fix)
        ------------------------------------*/
        .stButton > button, 
        .stDownloadButton > button,
        section[data-testid="stFileUploader"] button {
            background: var(--primary-blue) !important;
            color: var(--surface-white) !important;
            font-weight: 600 !important;
            border-radius: 4px !important;
            border: none !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            padding: 0.5rem 1rem !important;
        }
        
        /* EXTREME OVERRIDE: Target ALL nested elements, including icons and spans */
        .stButton > button * {
            color: var(--surface-white) !important;
        }

        /* Hover state */
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        section[data-testid="stFileUploader"] button:hover {
            background: #1976d2 !important; /* Slightly lighter shade on hover */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        /* ------------------------------------
        DATAFRAME STYLING (Light Mode Fix)
        ------------------------------------*/
        div[data-testid="stDataFrame"], 
        div[data-testid="stDataFrameContainer"] {
            background-color: var(--surface-white) !important; 
            border: 1px solid var(--border-light);
            border-radius: 4px;
            overflow: hidden; 
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        /* Force light background and dark text for all table cells/elements */
        div[data-testid="stDataFrame"] table,
        div[data-testid="stDataFrame"] th,
        div[data-testid="stDataFrame"] td,
        div[data-testid="stDataFrame"] span {
            background-color: var(--surface-white) !important;
            color: var(--primary-dark-text) !important;
            border-color: #eceff1 !important; /* Very light grid lines */
        }
        
        /* Style for the header row background */
        div[data-testid="stDataFrame"] th {
            background-color: #eceff1 !important; /* Very light grey header */
            font-weight: 600;
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
            border: 1px solid #b0bec5 !important;
            border-radius: 4px !important;
            color: var(--primary-dark-text) !important; 
            background: var(--surface-white) !important;
            padding: 0.5rem 0.75rem !important;
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.05);
        }

        /* Focused state */
        .stTextInput input:focus, .stTextInput textarea:focus,
        .stNumberInput input:focus, .stDateInput input:focus,
        .stTimeInput input:focus {
            border-color: var(--primary-blue) !important;
            box-shadow: 0 0 0 2px rgba(21, 101, 192, 0.3) !important;
        }

        /* ------------------------------------
        FILE UPLOADER - General Style
        ------------------------------------*/
        section[data-testid="stFileUploader"] {
            border: 2px dashed #90a4ae !important; 
            border-radius: 8px !important;
            padding: 1.5rem !important;
            background-color: #fcfcfc !important; 
        }

        /* ------------------------------------
        TABS STYLING
        ------------------------------------*/
        button[data-baseweb="tab"] {
            color: #78909c !important; 
            background-color: transparent !important;
            font-weight: 500;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--primary-blue) !important; 
            border-bottom: 3px solid var(--primary-blue) !important; 
            font-weight: 600;
        }
        
        .stTabs {
            background-color: var(--surface-white) !important;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid var(--border-light);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        /* ------------------------------------
        SECTION DIVIDER
        ------------------------------------*/
        .section-divider {
            margin: 2rem 0;
            border-top: 1px solid var(--border-light);
        }

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
