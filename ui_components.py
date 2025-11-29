import streamlit as st
from pathlib import Path
from contextlib import contextmanager
import io

def apply_custom_css():
    """
    Applies the custom Material 3 Light theme CSS.
    Note: Still relies heavily on data-testid selectors, which are Streamlit's internal
    CSS hooks. This remains a high-risk factor for future Streamlit version changes.
    """
    st.markdown(
        """
        <style>

        /* APP BACKGROUND - Using standard Streamlit background overrides */
        [data-testid="stAppViewContainer"] {
            background: #f8fafc !important; /* Lighter background than default white */
        }

        [data-testid="stHeader"] {
            background: none;
        }

        /* GLOBAL TYPOGRAPHY */
        html, body {
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        /* Set default text color for most elements */
        [data-testid="stMarkdownContainer"] * {
            color: #1e293b; /* Slate-900 for dark text */
        }

        /* STREAMLIT HEADING COLOR ALIGNMENT */
        /* Ensures Streamlit's built-in H1/H2/H3 elements use the primary brand color */
        [data-testid="stMarkdownContainer"] h1:not(.app-header h1), 
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 {
            color: #1e40af; /* Primary brand color (Indigo-700) for headings */
            font-weight: 700;
        }


        /* HEADER */
        .app-header {
            background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
            padding: 2.5rem 2rem;
            color: white; /* Default text color in header */
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 6px 20px rgba(30, 64, 175, 0.25);
        }

        .app-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            color: white !important; /* MUST be !important to override global rule */
            letter-spacing: -0.025em;
        }

        .app-header p {
            margin-top: .75rem;
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.9);
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
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.12);
            border-color: #93c5fd;
        }
        
        /* Inner content area of the card for context manager */
        .card-content {
            margin-top: 1rem;
        }

        .card-header {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1e293b;
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
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #93c5fd;
        }

        /* FIX: Use primary blue for metric values */
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1e40af; 
            margin: .5rem 0;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .metric-label {
            font-size: .8rem;
            font-weight: 600;
            text-transform: uppercase;
            color: #64748b;
            letter-spacing: .05em;
        }

        /* --- BUTTON STYLING --- */
        
        /* REGULAR BUTTON STYLING (Applies to st.button) */
        [data-testid="stButton"] > button {
            background: #1e40af; /* Primary blue */
            color: white;
            border: 1px solid #1e40af;
            font-weight: 600;
            border-radius: 8px;
            padding: .6rem 1.2rem;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        [data-testid="stButton"] > button:hover {
            background: #3730a3; /* Darker blue on hover */
            border-color: #3730a3;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            transform: translateY(-1px);
        }
        
        [data-testid="stButton"] > button:active {
            transform: scale(0.98);
        }

        /* DOWNLOAD BUTTON STYLING */
        /* Note: Kept !important here as download buttons often use a high-specificity base style */
        [data-testid="stDownloadButton"] button {
            background:#1e40af !important;
            color:white !important;
            border:none !important;
            font-weight:600 !important;
            border-radius:8px !important;
            padding:.75rem 1.5rem !important;
            width:100% !important;
            transition: background-color 0.2s ease, transform 0.1s ease;
        }
        
        [data-testid="stDownloadButton"] button:hover {
            background: #1e3a8a !important;
        }
        
        [data-testid="stDownloadButton"] button:active {
            transform: scale(0.98);
        }


        /* --- TABLE & DATAFRAME STYLING --- */
        
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            margin-bottom: 1.5rem;
        }
        
        /* Table Headers */
        .dataframe thead th, 
        .stTable > div > div:first-child {
            background-color: #f1f5f9; /* Light gray for headers */
            color: #1e293b;
            font-weight: 700;
            border-bottom: 2px solid #e2e8f0;
        }

        /* Table Cells */
        .dataframe tbody tr td,
        .stTable > div > div:not(:first-child) {
            background-color: white;
            color: #1e293b;
            border-bottom: 1px solid #f1f5f9;
        }
        
        /* Striping for better readability */
        .dataframe tbody tr:nth-child(even) td {
             background-color: #f8fafc; /* Very light subtle stripe */
        }
        
        /* --- TAB STYLING --- */
        
        [data-testid="stTabs"] {
            width: 100%; 
        }

        [data-testid="stTabs"] > div:first-child {
            display: flex;
            width: 100%;
            border-bottom: 2px solid #e2e8f0 !important;
        }
        
        /* Style individual tabs, allowing flexible width based on content */
        [data-testid="stTabs"] button {
            /* Removed flex: 1 1 25%; for better responsiveness with many tabs */
            flex-grow: 1;
            flex-shrink: 1;
            flex-basis: auto; 
            border-radius: 8px 8px 0 0;
            padding: 1rem 0;
            text-align: center;
            font-weight: 600;
            color: #64748b;
            border-bottom: 4px solid transparent !important;
            transition: all 0.3s ease;
        }
        
        /* Hover effect on inactive tabs */
        [data-testid="stTabs"] button:hover {
            color: #1e40af;
            border-bottom-color: #dbeafe !important;
        }

        /* ACTIVE TAB INDICATORS (Different colors for up to 4 tabs) */
        
        /* 1st Tab: Primary Blue */
        [data-testid="stTabs"] button[aria-selected="true"]:nth-child(1) {
            color: #1e40af !important;
            border-bottom-color: #1e40af !important;
        }

        /* 2nd Tab: Success Green */
        [data-testid="stTabs"] button[aria-selected="true"]:nth-child(2) {
            color: #10b981 !important;
            border-bottom-color: #10b981 !important;
        }

        /* 3rd Tab: Warning Orange */
        [data-testid="stTabs"] button[aria-selected="true"]:nth-child(3) {
            color: #f59e0b !important;
            border-bottom-color: #f59e0b !important;
        }

        /* 4th Tab: Secondary Purple */
        [data-testid="stTabs"] button[aria-selected="true"]:nth-child(4) {
            color: #6366f1 !important;
            border-bottom-color: #6366f1 !important;
        }
        
        /* --- Existing Styles --- */

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
        .alert-info    { border-left-color:#3b82f6; background:#f0f9ff; }
        .alert-warning { border-left-color:#f59e0b; background:#fffbeb; }
        .alert-error    { border-left-color:#ef4444; background:#fef2f2; }

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
            flex-wrap: wrap;
        }
        
        .stage-connector {
            flex-grow: 1;
            height: 2px;
            background: #e2e8f0;
            margin: 0.5rem 0.5rem 0 0.5rem; 
            align-self: center;
        }
        
        .stage-connector.completed {
            background: #1e40af; 
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
            box-shadow: 0 0 0 4px rgba(30, 64, 175, 0.2);
        }

        .stage-circle.completed {
            background:#10b981; border-color:#10b981; color:white !important;
        }

        .stage-circle.inactive {
            background:#f8fafc; border-color:#e2e8f0; color:#94a3b8;
        }

        .stage-label { font-size:.85rem; color:#64748b; }
        .stage-label.active { color:#1e40af; font-weight:600; }

        /* FILE UPLOADER */
        [data-testid="stFileUploader"] > div {
            background:white !important;
            border:2px dashed #cbd5e1 !important;
            border-radius:8px !important;
            padding:2rem !important;
            transition: border-color 0.3s ease;
        }
        
        [data-testid="stFileUploader"] > div:hover {
            border-color: #93c5fd !important;
        }

        [data-testid="stFileUploader"] label {
            color:#1e293b;
            font-weight:600;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

def render_header(title: str, subtitle: str = ""):
    """Renders the stylized application header."""
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{title}</h1>
            {'<p>'+subtitle+'</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

@contextmanager
def card(title: str, icon: str = ""):
    """
    Renders a stylized card container using a Python context manager.
    
    Usage:
    with card("My Card Title"):
        st.write("Content goes here...")
    """
    # Start the card HTML container
    st.markdown(
        f"""
        <div class="card">
            <div class="card-header">{icon if icon else ''} {title}</div>
            <div class="card-content">
        """,
        unsafe_allow_html=True,
    )
    
    # Yield control to the 'with' block
    try:
        yield
    finally:
        # Close the inner and outer card divs
        st.markdown("</div></div>", unsafe_allow_html=True)


def render_stage_progress(current_stage: float):
    """Renders the responsive stage progress bar."""
    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"),
        ("3", "Results"),
    ]

    total = len(stages)
    current_stage = max(0, min(current_stage, total - 1))

    blocks = []
    connectors = []

    # Create each stage's block and connector
    for idx, (num, label) in enumerate(stages):
        is_completed = (idx < current_stage)
        is_active = (idx == int(current_stage))

        if is_completed:
            status = "completed"
            icon = "✓"
        elif is_active:
            status = "active"
            icon = num
        else:
            status = "inactive"
            icon = num

        # Final stage special case: if fractional stage is passed (e.g., 2.5), it is complete
        if idx == total - 1 and current_stage >= total - 1:
            status = "completed"
            icon = "✓"

        is_active_label = is_active or (idx == total - 1 and current_stage >= total - 1)

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


def render_metric_card(label: str, value: str, col: st.delta_generator.DeltaGenerator):
    """Renders a stylized metric card within a specified Streamlit column."""
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
    """Renders a stylized alert box (success, info, warning, error)."""
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
    """Renders a visual separator line."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_download_button(label: str, data: bytes | io.BytesIO, file_name: str, mime: str):
    """
    Renders a stylized download button for arbitrary file data.

    Args:
        label (str): Text displayed on the button.
        data (bytes | io.BytesIO): The file content to download.
        file_name (str): The default file name for the downloaded file.
        mime (str): The MIME type of the file (e.g., "application/pdf").
    """
    st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime=mime,
        use_container_width=True,
    )

# --- Example of Usage ---

def main():
    """Demonstrates the usage of the themed components."""
    
    # 1. Apply Theme
    apply_custom_css()
    
    # 2. Render Header
    render_header(
        title="Material 3 Dashboard",
        subtitle="Refactored Streamlit components with robust styling and interaction."
    )
    
    # 3. Render Stage Progress (e.g., Step 2 in progress)
    st.markdown("## Progress Tracker")
    render_stage_progress(current_stage=1.2)
    render_section_divider()
    
    st.markdown("## Metrics & Cards")
    
    # 4. Render Metrics
    col1, col2, col3 = st.columns(3)
    render_metric_card("Total Revenue", "💰 $1.2M", col1)
    render_metric_card("Conversion Rate", "📈 4.8%", col2)
    render_metric_card("New Users", "👤 8,450", col3)

    # 5. Render Card using the new context manager
    with card("Data Upload & Preview", icon="⬇️"):
        st.write(
            "Upload your dataset below. Only CSV and Excel files are supported for processing."
        )
        st.file_uploader("Select File", type=["csv", "xlsx"])
        
        # Demonstrating the reusable download button (mocking file data)
        mock_excel_data = b"Mock Excel Content"
        render_download_button(
            label="Download Blank Template",
            data=mock_excel_data,
            file_name="blank_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    render_section_divider()

    st.markdown("## Tabs & Alerts")
    
    # 6. Render Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Configuration", "History", "Settings"])
    
    with tab1:
        render_alert("This is a success message!", "success")
        st.write("This is the main dashboard content.")
    
    with tab2:
        render_alert("Warning: Settings must be saved.", "warning")
        st.write("Configuration details here.")

    with tab3:
        # 7. Render Buttons and Table
        st.button("Run Simulation", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.table({
            'ID': [1, 2, 3],
            'Status': ['Completed', 'Failed', 'Running'],
            'Runtime': ['15s', '30s', '5s']
        })

    with tab4:
        render_alert("Info: New features are available in beta.", "info")
        st.write("Application settings.")

if __name__ == "__main__":
    main()
