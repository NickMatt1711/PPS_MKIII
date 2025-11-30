"""
Material 3 Light Theme - Corporate UI Components
Clean, professional design without sidebar
"""

import streamlit as st
from constants import THEME_COLORS

def apply_custom_css():
    """Apply Material 3 Light theme for corporate application."""
    
    # Extract colors from constants
    primary = THEME_COLORS['primary']
    primary_light = THEME_COLORS['primary_light']
    surface = THEME_COLORS['surface']
    on_primary = THEME_COLORS['on_primary']
    on_surface = THEME_COLORS['on_surface']
    border_light = THEME_COLORS['border_light']
    
    st.markdown(
        f"""
        <style>
        /* Fix download button to match other buttons */
        .stDownloadButton > button {{
            background: {primary} !important;
            color: {on_primary} !important;
        }}
        
        .stDownloadButton > button:hover {{
            background: {primary_light} !important;
        }}

        /* Fix file uploader text colors */
        section[data-testid="stFileUploader"] {{
            color: {on_surface} !important;
        }}

        section[data-testid="stFileUploader"] * {{
            color: {on_surface} !important;
        }}

        /* Fix dataframe text colors */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrameResizable"] {{
            color: {on_surface} !important;
        }}

        div[data-testid="stDataFrame"] *,
        div[data-testid="stDataFrameResizable"] * {{
            color: {on_surface} !important;
        }}
        </style>
        """, 
        unsafe_allow_html=True
    )

# ... rest of your existing functions remain exactly the same ...
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
    """Render horizontal full-width stage progress indicator."""
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
        if idx < current_stage:
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
                help="Download the Excel template file",
                use_container_width=True
            )
        else:
            st.error("Template file not found")
    except Exception as e:
        st.error(f"Error loading template: {e}")
