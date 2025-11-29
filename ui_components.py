import streamlit as st
import pandas as pd
import io

# --- Constants (assuming these are defined in your constants.py) ---
# SS_THEME, SS_STAGE, APP_ICON, etc. are assumed to be imported by app.py

# --- CSS and Styling ---

def apply_custom_css():
    """Applies necessary custom CSS styles for the wizard UI and components."""
    # Note: Use f-strings for theme-dependent colors if SS_THEME were accessible, 
    # but for simplicity, we use universal colors here.
    
    css = """
    <style>
        /* General Streamlit Overrides */
        section.main {
            padding-top: 2rem; /* Reduce top padding for cleaner look */
        }
        .stButton>button {
            border-radius: 0.5rem;
            transition: all 0.2s;
            font-weight: 600;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #1f77b4; /* Deep Blue for Headers */
            padding-top: 10px;
        }
        .stAlert {
            border-radius: 0.75rem;
        }

        /* 1. Progress Bar / Stage Indicator */
        .stage-indicator {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #ccc;
        }
        .stage-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            flex-grow: 1;
        }
        .stage-circle {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: #ddd;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            z-index: 10;
            border: 2px solid #ddd;
        }
        .stage-item.active .stage-circle {
            background-color: #1f77b4;
            border-color: #1f77b4;
            box-shadow: 0 0 10px rgba(31, 119, 180, 0.5);
        }
        .stage-item.complete .stage-circle {
            background-color: #2ca02c; /* Green for complete */
            border-color: #2ca02c;
        }
        .stage-label {
            margin-top: 0.5rem;
            font-size: 0.85rem;
            text-align: center;
            color: #666;
            font-weight: 500;
        }
        .stage-item.active .stage-label {
            color: #1f77b4;
            font-weight: bold;
        }
        .stage-line {
            position: absolute;
            height: 2px;
            background-color: #ddd;
            width: 100%;
            top: 15px; /* Half height of circle */
            z-index: 5;
            transform: translateX(-50%); /* Start at the center of the previous circle */
        }
        .stage-item:not(:first-child) .stage-line {
            width: calc(100% + 15px); /* Extend line to touch previous circle */
            left: 0;
            transform: translateX(-50%);
        }
        .stage-item:first-child .stage-line {
            display: none;
        }
        .stage-item.complete:not(:first-child) .stage-line {
            background-color: #2ca02c; /* Green line for completed stages */
        }

        /* 2. Optimization Spinner Stage (Crucial Fix) */
        .optimization-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem 0;
            text-align: center;
        }
        .spinner {
            border: 8px solid #f3f3f3; /* Light grey */
            border-top: 8px solid #1f77b4; /* Blue */
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 2s linear infinite;
            margin-bottom: 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .optimization-text {
            font-size: 1.5rem;
            font-weight: bold;
            color: #1f77b4;
        }
        .optimization-subtext {
            color: #666;
            font-size: 1rem;
        }

        /* 3. Metric Card Styling */
        .metric-card {
            background-color: #f0f2f6; /* Light background for card */
            border-radius: 1rem;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .metric-title {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.25rem;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #1f77b4;
        }
        
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# --- UI Component Functions ---

def render_header(title: str, subtitle: str):
    """Renders the main header for the application."""
    st.title(title)
    st.markdown(f"#### {subtitle}")
    st.write("---")

def render_stage_progress(current_stage: float):
    """Renders the step-by-step progress indicator."""
    
    # Define stages and titles
    stages = [
        (0, "Upload Data"),
        (1, "Configure"),
        (2, "Results"),
    ]
    
    html = '<div class="stage-indicator">'
    
    for stage_id, label in stages:
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
            <div class="stage-line"></div>
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
    st.markdown('<div style="margin-top: 1.5rem; margin-bottom: 1.5rem; border-bottom: 1px solid #eee;"></div>', unsafe_allow_html=True)

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
    Renders a Streamlit download button.
    Data can be bytes (e.g., for Excel) or a string (e.g., for CSV).
    """
    st.download_button(
        label=label,
        data=data,
        file_name=file_name,
        mime=mime,
        use_container_width=True
    )
    
# NOTE: The file app.py imports the following, but they are not used/defined here. 
# They must be present in the final environment:
# - from data_loader import *
# - from preview_tables import *
# - from solver_cp_sat import build_and_solve_model
# - from postprocessing import * (including get_or_create_grade_colors, create_gantt_chart, etc.)
