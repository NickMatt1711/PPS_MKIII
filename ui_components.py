"""
Material 3 Light Theme – Streamlit-Compatible (Refactored)
Includes:
- CSS transitions and hover effects for interactivity.
- Improved heading color and metric card customization.
- Stage progress bar responsiveness.
- Card rendering using a Python context manager.
"""

import streamlit as st
from pathlib import Path
from contextlib import contextmanager

def apply_custom_css():
    st.markdown(
        """
        <style>

        /* APP BACKGROUND */
        [data-testid="stAppViewContainer"] {
            background: #f8fafc !important;
        }

        [data-testid="stHeader"] {
            background: none;
        }

        /* GLOBAL TYPOGRAPHY */
        html, body, [data-testid="stMarkdownContainer"] * {
            color: #1e293b !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        /* STREAMLIT HEADING COLOR ALIGNMENT */
        /* Ensures Streamlit's built-in H1/H2/H3 elements use the brand color */
        [data-testid="stMarkdownContainer"] h1:not(.app-header h1), 
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 {
            color: #1e40af !important; /* Use primary brand color for headings */
            font-weight: 700;
        }


        /* HEADER */
        .app-header {
            background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
            padding: 2.5rem 2rem;
            color: white !important;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 6px 20px rgba(30, 64, 175, 0.25); /* Deeper shadow */
        }

        .app-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            color: white !important;
            letter-spacing: -0.025em;
        }

        .app-header p {
            margin-top: .75rem;
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500;
        }

        /* CARD */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); /* Add transition for hover */
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.12); /* Subtle lift effect */
            border-color: #93c5fd; /* Light blue border on hover */
        }
        
        /* Inner content area of the card for context manager */
        .card-content {
            margin-top: 1rem;
        }

        .card-header {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1e293b !important;
            padding-bottom: .5rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        /* METRIC CARD */
        .metric-card {
            padding: 1.2rem 1rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            background: white;
            border: 1px solid #e2e8f0;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); /* Add transition for hover */
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #93c5fd;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1e40af !important; /* Use primary blue by default */
            margin: .5rem 0;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        /* Ensures icon doesn't inherit value color if specific color is set */
        .metric-value span {
            color: inherit !important; 
        }

        .metric-label {
            font-size: .8rem;
            font-weight: 600;
            text-transform: uppercase;
            color: #64748b !important;
            letter-spacing: .05em;
        }

        /* ALERTS */
        .alert {
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            border-left: 4px solid;
            font-weight: 500;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .alert-success { border-left-color:#10b981; background:#f0fdf4; }
        .alert-info    { border-left-color:#3b82f6; background:#f0f9ff; }
        .alert-warning { border-left-color:#f59e0b; background:#fffbeb; }
        .alert-error   { border-left-color:#ef4444; background:#fef2f2; }

        /* DIVIDER */
        .section-divider {
            height: 1px;
            background: #e2e8f0;
            margin: 2rem 0;
        }

        /* STAGE PROGRESS */
        .stage-container {
            padding: 2rem 1.5rem;
            background: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 2rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        }

        .stage-row {
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap; /* Allows steps to wrap on small screens */
        }
        
        .stage-connector {
            flex-grow: 1;
            height: 2px;
            background: #e2e8f0;
            margin: 0.5rem 0.5rem 0 0.5rem; /* Better vertical alignment */
            align-self: center;
        }
        
        .stage-connector.completed {
            background: #1e40af; /* Connector uses primary color when completed */
        }


        .stage-step {
            text-align: center;
            min-width: 100px;
        }

        .stage-circle {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: 600;
            font-size: 1rem;
            margin: 0 auto .5rem auto;
            border: 2px solid;
            transition: all 0.3s ease;
        }

        .stage-circle.active {
            background:#1e40af; border-color:#1e40af; color:white !important;
            box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.2); /* Focus ring effect */
        }

        .stage-circle.completed {
            background:#10b981; border-color:#10b981; color:white !important;
        }

        .stage-circle.inactive {
            background:#f8fafc; border-color:#e2e8f0; color:#94a3b8 !important;
        }

        .stage-label { font-size:.85rem; color:#64748b !important; }
        .stage-label.active { color:#1e40af !important; font-weight:600; }

        /* DOWNLOAD BUTTON */
        [data-testid="stDownloadButton"] button {
            background:#1e40af !important;
            color:white !important;
            border:none !important;
            font-weight:600 !important;
            border-radius:8px !important;
            padding:.75rem 1.5rem !important;
            width:100% !important;
            transition: background-color 0.2s ease, transform 0.1s ease; /* Added transition */
        }
        
        [data-testid="stDownloadButton"] button:hover {
            background: #1e3a8a !important; /* Slightly darker blue on hover */
        }
        
        [data-testid="stDownloadButton"] button:active {
            transform: scale(0.98); /* Subtle press effect */
        }


        /* FILE UPLOADER */
        [data-testid="stFileUploader"] > div {
            background:white !important;
            border:2px dashed #cbd5e1 !important;
            border-radius:8px !important;
            padding:2rem !important;
            transition: border-color 0.3s ease;
        }
        
        [data-testid="stFileUploader"] > div:hover {
            border-color: #93c5fd !important; /* Border color change on hover */
        }

        [data-testid="stFileUploader"] label {
            color:#1e293b !important;
            font-weight:600 !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{title}</h1>
            {'<p>'+subtitle+'</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stage_progress(current_stage: float):
    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"),
        ("3", "Results"),
    ]

    total = len(stages)
    # Ensure valid current_stage index (0, 1, 1.5, or 2)
    current_stage = max(0, min(current_stage, total - 1))

    blocks = []
    connectors = []

    # Create each stage's block and connector
    for idx, (num, label) in enumerate(stages):
        if idx < current_stage or (idx == total - 1 and current_stage >= total - 1):
            status = "completed"
            icon = "✓"
        # Current active stage (if not the final one)
        elif idx == int(current_stage): 
            status = "active"
            icon = num
        # Future stages
        else:
            status = "inactive"
            icon = num

        # Determine if label should be bold/blue (Active)
        # It is active if it matches the current integer stage, OR if it is the final completed stage
        is_active_label = (idx == int(current_stage)) or (idx == total - 1 and current_stage >= total - 1)

        blocks.append(
            f"""
            <div class="stage-step">
                <div class="stage-circle {status}">{icon}</div>
                <div class="stage-label {'active' if is_active_label else ''}">
                    {label}
                </div>
            </div>
            """
        )

        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            connectors.append(f'<div class="stage-connector {connector_class}"></div>')

    # Combine blocks and connectors into HTML
    html = ""
    for i, block in enumerate(blocks):
        html += block
        if i < len(connectors):
            html += connectors[i]

    # Render the final stage progress bar
    st.markdown(
        f"""
        <div class="stage-container">
            <div class="stage-row">{html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def custom_card(title: str, icon: str = ""):
    """
    A context manager to wrap Streamlit content in a custom, styled card.
    
    Usage:
    with custom_card("Data Summary", icon="📊"):
        st.write("This content is inside the card.") 
    """
    # Start the card HTML structure and the header
    st.markdown(
        f"""
        <div class="card">
            <div class="card-header">{icon + ' ' if icon else ''}{title}</div>
            <div class="card-content">
        """,
        unsafe_allow_html=True,
    )
    
    # Yield control back to the 'with' block where Streamlit commands will be executed
    try:
        yield 
    finally:
        # Close the HTML structure after the content is rendered
        st.markdown(
            """
                </div> 
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metric_card(label: str, value: str, col, value_color: str = "#1e40af", icon: str = ""):
    """
    Renders a customizable metric card inside a Streamlit column.
    
    Args:
        label (str): The label/title of the metric.
        value (str): The main value of the metric.
        col: The Streamlit column object to render into.
        value_color (str): Optional. A hex or name CSS color for the value text (e.g., '#10b981' for success).
        icon (str): Optional. An emoji or simple text icon to display next to the value.
    """
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{value_color} !important;">
                    {'<span style="font-size:1.5rem; margin-right:8px;">' + icon + '</span>' if icon else ''}
                    {value}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_alert(message: str, alert_type: str = "info"):
    icons = {
        "success": "✓",
        "info": "ℹ",
        "warning": "⚠",
        "error": "✕",
    }
    st.markdown(
        f"""
        <div class="alert alert-{alert_type}">
            <strong>{icons.get(alert_type,"ℹ")}</strong>
            <span>{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_download_template_button():
    # Helper for rendering a download button for a specific file
    try:
        template_path = Path("polymer_production_template.xlsx")

        if template_path.exists():
            st.download_button(
                label="Download Template",
                data=template_path.read_bytes(),
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            # Fallback for if the file is not in the same directory
            st.error("Template file not found. Ensure 'polymer_production_template.xlsx' is in the application directory.")
    except Exception as e:
        st.error(f"Error loading template: {e}")
