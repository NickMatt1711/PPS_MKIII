"""
Material 3 Light Theme - Corporate UI Components
Clean, professional design without sidebar
"""

import streamlit as st
from constants import THEME_COLORS # Re-introducing the original import

def apply_custom_css():
    """Apply Material 3 Light theme for corporate application."""
    
    st.markdown(
        """
        <style>
        /* ------------------------------------
        GLOBAL BASE - Material 3 Light
        ------------------------------------*/
        .stApp {
            background: #f8fafc !important;
        }
        
        .main {
            background: #f8fafc !important;
        }

        /* Material 3 Typography - Force light text */
        p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: #1e293b !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        /* ------------------------------------
        HEADER - Corporate Gradient
        ------------------------------------*/
        .app-header {
            background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
            padding: 2.5rem 2rem;
            color: white !important;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
        }
        
        .app-header h1 {
            margin: 0;
            font-size: 2.5rem;
            color: white !important;
        }
        
        .app-header p {
            color: rgba(255, 255, 255, 0.9) !important;
            margin-top: 0.5rem;
        }

        /* ------------------------------------
        WIZARD / STAGE PROGRESS STYLING
        ------------------------------------*/
        .stage-container {
            padding: 1rem 0;
            margin-bottom: 2rem;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
        }
        .stage-circle {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: 700;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
            border: 3px solid;
            z-index: 10; /* Ensure it overlaps connector */
        }
        .stage-label {
            font-size: 0.9rem;
            text-align: center;
            font-weight: 500;
            color: #4b5563 !important;
        }

        /* Status Classes */
        .stage-circle.inactive {
            background-color: #f3f4f6;
            color: #9ca3af;
            border-color: #d1d5db;
        }
        .stage-circle.active {
            background-color: #1e40af;
            color: white;
            border-color: #1e40af;
            box-shadow: 0 0 0 5px rgba(30, 64, 175, 0.2);
        }
        .stage-circle.completed {
            background-color: #10b981;
            color: white;
            border-color: #10b981;
        }
        .stage-label.active {
            font-weight: 700;
            color: #1e293b !important;
        }

        /* Connectors */
        .stage-connector {
            height: 4px; 
            background-color: #d1d5db; 
            flex-grow: 1;
            margin: 0 -20px; 
            position: relative;
            top: 21.5px; /* (40/2 + 3/2) - (4/2) = 21.5 */
            z-index: 0;
        }
        .stage-connector.completed {
            background-color: #10b981; 
        }
        .stage-step > div { /* Re-layered z-index */
            position: relative;
            z-index: 1; 
        }

        /* ------------------------------------
        CARDS & ALERTS
        ------------------------------------*/
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            padding: 1.5rem; 
            margin-bottom: 1.5rem;
        }
        
        .card-header {
            color: #1e293b !important;
            border-bottom: 1px solid #e5e7eb;
            padding-bottom: 0.75rem;
            margin-bottom: 1rem;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        div[data-testid="stAlert"] {
            background-color: #eff6ff !important;
            border-left: 5px solid #1e40af !important;
            border-radius: 4px;
            box-shadow: none;
        }
        .stAlert p, .stAlert strong { color: #1e40af !important; }
        
        /* Specific Alert styles */
        .alert-success { background-color: #d1fae5 !important; border-left-color: #059669 !important; }
        .alert-info { background-color: #eff6ff !important; border-left-color: #3b82f6 !important; }
        .alert-warning { background-color: #fffde7 !important; border-left-color: #f59e0b !important; }
        .alert-error { background-color: #fee2e2 !important; border-left-color: #ef4444 !important; }
        .alert-success p, .alert-success strong { color: #059669 !important; }
        .alert-info p, .alert-info strong { color: #3b82f6 !important; }
        .alert-warning p, .alert-warning strong { color: #f59e0b !important; }
        .alert-error p, .alert-error strong { color: #ef4444 !important; }

        /* ------------------------------------
        BUTTONS - Primary Look
        ------------------------------------*/
        .stButton > button, 
        .stDownloadButton > button,
        section[data-testid="stFileUploader"] button {
            background: #1e40af !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: none !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 3px rgba(30, 64, 175, 0.3) !important;
            padding: 0.5rem 1rem !important;
        }
        
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        section[data-testid="stFileUploader"] button:hover {
            background: #3730a3 !important;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4) !important;
            transform: translateY(-1px) !important;
        }

        /* ------------------------------------
        DATAFRAME STYLING (Light Mode)
        ------------------------------------*/
        div[data-testid="stDataFrame"], 
        div[data-testid="stDataFrameContainer"] {
            background-color: white !important; 
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            overflow: hidden; 
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        div[data-testid="stDataFrame"] th {
            background-color: #f9fafb !important; 
            color: #1e293b !important;
            font-weight: 600;
            border-color: #e5e7eb !important;
        }
        
        div[data-testid="stDataFrame"] td {
            color: #1e293b !important;
            background-color: white !important;
            border-color: #f3f4f6 !important;
        }

        /* ------------------------------------
        INPUT FIELDS (Light Mode)
        ------------------------------------*/
        .stTextInput input,
        .stTextInput textarea,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input {
            border: 1px solid #d1d5db !important;
            border-radius: 4px !important;
            color: #1e293b !important; 
            background: white !important;
            padding: 0.5rem 0.75rem !important;
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.05);
        }

        .stTextInput input:focus, .stTextInput textarea:focus,
        .stNumberInput input:focus, .stDateInput input:focus,
        .stTimeInput input:focus {
            border-color: #1e40af !important;
            box-shadow: 0 0 0 2px rgba(30, 64, 175, 0.3) !important;
        }

        /* ------------------------------------
        FILE UPLOADER
        ------------------------------------*/
        section[data-testid="stFileUploader"] {
            border: 2px dashed #9ca3af !important; 
            border-radius: 8px !important;
            padding: 1.5rem !important;
            background-color: #fcfcfc !important; 
        }
        
        /* ------------------------------------
        TABS STYLING
        ------------------------------------*/
        button[data-baseweb="tab"] {
            color: #64748b !important; 
            background-color: transparent !important;
            font-weight: 500;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #1e40af !important; 
            border-bottom: 3px solid #1e40af !important; 
            font-weight: 600;
        }
        
        .stTabs {
            background-color: white !important;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        /* ------------------------------------
        SECTION DIVIDER
        ------------------------------------*/
        .section-divider {
            margin: 2rem 0;
            border-top: 1px solid #e5e7eb;
        }
        
        /* ------------------------------------
        METRIC CARDS (Placeholder style)
        ------------------------------------*/
        .metric-card {
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            text-align: center;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #64748b !important;
            font-weight: 500;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1e40af !important;
            margin-top: 0.25rem;
        }
        
        /* Ensure all nested text uses dark color */
        .stButton > button * {
            color: white !important;
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
    # The current stage should be 0, 1, or 2 for the three stages
    current_stage = max(0, min(current_stage, total - 1))

    html = '<div class="stage-row">'
    
    for idx, (num, label) in enumerate(stages):
        status = "inactive"
        icon = num
        
        if idx == current_stage:
            status = "active"
        elif idx < current_stage:
            status = "completed"
            icon = "✓"
        
        # Start Step Block
        html += '<div class="stage-step">'
        
        # Circle
        html += f"""
            <div class="stage-circle {status}">{icon}</div>
            <div class="stage-label {'active' if idx == current_stage else ''}">
                {label}
            </div>
        """
        html += '</div>' # End stage-step
        
        # Connector (Don't add after the last step)
        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            html += f'<div class="stage-connector {connector_class}"></div>'

    html += '</div>' # End stage-row

    st.markdown(
        f"""
        <div class="stage-container">
            {html}
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
            st.error("Template file not found")
    except Exception as e:
        st.error(f"Template file not found: {e}")
