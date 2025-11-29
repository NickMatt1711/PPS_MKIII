import streamlit as st
import pandas as pd
import io

# --- CSS and Styling ---

def apply_custom_css():
    """Applies necessary custom CSS styles for the wizard UI and components."""
    
    css = """
    <style>
        /* General Streamlit Overrides for Light Theme */
        .main {
            background-color: #ffffff;
        }
        .stApp {
            background-color: #f8f9fa;
        }
        .stButton>button {
            border-radius: 8px;
            border: 1px solid #d0d0d0;
            background-color: #ffffff;
            color: #333333;
            transition: all 0.2s ease;
            font-weight: 500;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #f0f0f0;
            border-color: #a0a0a0;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #1a365d; /* Darker blue for better contrast in light theme */
            padding-top: 10px;
        }
        .stAlert {
            border-radius: 8px;
            border: 1px solid;
        }
        .stInfo {
            border-color: #2196F3;
        }
        .stSuccess {
            border-color: #4CAF50;
        }
        .stWarning {
            border-color: #FF9800;
        }
        .stError {
            border-color: #f44336;
        }

        /* 1. Progress Bar / Stage Indicator - Fixed for Light Theme */
        .stage-indicator {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e0e0e0;
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .stage-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            flex-grow: 1;
        }
        .stage-circle {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background-color: #e9ecef;
            color: #6c757d;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            z-index: 10;
            border: 3px solid #e9ecef;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }
        .stage-item.active .stage-circle {
            background-color: #1976d2;
            border-color: #1976d2;
            color: white;
            box-shadow: 0 0 0 4px rgba(25, 118, 210, 0.2);
        }
        .stage-item.complete .stage-circle {
            background-color: #28a745;
            border-color: #28a745;
            color: white;
        }
        .stage-label {
            margin-top: 0.75rem;
            font-size: 0.85rem;
            text-align: center;
            color: #6c757d;
            font-weight: 500;
            max-width: 100px;
        }
        .stage-item.active .stage-label {
            color: #1976d2;
            font-weight: 600;
        }
        .stage-item.complete .stage-label {
            color: #28a745;
        }
        .stage-connector {
            position: absolute;
            height: 2px;
            background-color: #e9ecef;
            top: 18px;
            left: -50%;
            right: 50%;
            z-index: 5;
        }
        .stage-item:first-child .stage-connector {
            display: none;
        }
        .stage-item.complete .stage-connector {
            background-color: #28a745;
        }

        /* 2. Optimization Spinner Stage - Improved for Light Theme */
        .optimization-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem 2rem;
            text-align: center;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin: 2rem 0;
        }
        .spinner {
            border: 4px solid #f8f9fa;
            border-top: 4px solid #1976d2;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1.5s linear infinite;
            margin-bottom: 1.5rem;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .optimization-text {
            font-size: 1.4rem;
            font-weight: 600;
            color: #1a365d;
            margin-bottom: 0.5rem;
        }
        .optimization-subtext {
            color: #6c757d;
            font-size: 1rem;
            line-height: 1.5;
        }

        /* 3. Metric Card Styling - Improved for Light Theme */
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.75rem 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            text-align: center;
            border: 1px solid #e9ecef;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        }
        .metric-title {
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 0.5rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 2.25rem;
            font-weight: 700;
            color: #1a365d;
            line-height: 1.2;
        }

        /* 4. Download Button Styling */
        .stDownloadButton>button {
            background-color: #28a745;
            color: white;
            border: none;
        }
        .stDownloadButton>button:hover {
            background-color: #218838;
            color: white;
        }

        /* 5. Section Styling */
        .section-container {
            background-color: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin: 1.5rem 0;
            border: 1px solid #e9ecef;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# --- UI Component Functions ---

def render_header(title: str, subtitle: str):
    """Renders the main header for the application."""
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f"#### {subtitle}")
    st.markdown('</div>', unsafe_allow_html=True)

def render_stage_progress(current_stage: float):
    """Renders the step-by-step progress indicator with fixed connector logic."""
    
    # Define stages and titles
    stages = [
        (0, "Upload Data"),
        (1, "Configure"),
        (2, "Results"),
    ]
    
    html = '<div class="stage-indicator">'
    
    for i, (stage_id, label) in enumerate(stages):
        is_complete = current_stage > stage_id
        is_active = stage_id == int(current_stage)
        
        # Handle the special 1.5 stage visually as part of stage 1
        if current_stage == 1.5 and stage_id == 1:
            is_active = True

        status_class = "complete" if is_complete else ("active" if is_active else "")
        
        # Use checkmark for complete stages
        circle_content = "✓" if is_complete else str(stage_id + 1)
        
        html += f"""
        <div class="stage-item {status_class}">
            <div class="stage-connector"></div>
            <div class="stage-circle">{circle_content}</div>
            <div class="stage-label">{label}</div>
        </div>
        """
    
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_alert(message: str, type: str = "info"):
    """Renders a Streamlit alert message (info, success, warning, error)."""
    if type == "info":
        st.info(message)
    elif type == "success":
        st.success(message)
    elif type == "warning":
        st.warning(message)
    elif type == "error":
        st.error(message)

def render_section_divider():
    """Renders a visual separator for sections."""
    st.markdown('<div style="margin: 2rem 0; height: 1px; background: linear-gradient(90deg, transparent 0%, #e0e0e0 50%, transparent 100%);"></div>', unsafe_allow_html=True)

def render_section_container():
    """Creates a container for section content with proper styling."""
    return st.container()

def render_metric_card(title: str, value: str, column: st.delta_generator.DeltaGenerator):
    """Renders a key performance metric card in the specified column."""
    with column:
        html = f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

def render_download_button(label: str, data, file_name: str, mime: str):
    """
    Renders a Streamlit download button with improved styling.
    Data can be bytes (e.g., for Excel) or a string (e.g., for CSV).
    """
    st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime=mime,
        use_container_width=True
    )

def render_optimization_spinner(message: str = "Optimizing your configuration...", submessage: str = "This may take a few moments."):
    """Renders the optimization spinner with custom messages."""
    html = f"""
    <div class="optimization-container">
        <div class="spinner"></div>
        <div class="optimization-text">{message}</div>
        <div class="optimization-subtext">{submessage}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.empty()  # Creates some space below
