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
    primary_container = THEME_COLORS['primary_container']
    on_primary = THEME_COLORS['on_primary']
    
    secondary = THEME_COLORS['secondary']
    secondary_container = THEME_COLORS['secondary_container']
    
    surface = THEME_COLORS['surface']
    surface_variant = THEME_COLORS['surface_variant']
    on_surface = THEME_COLORS['on_surface']
    on_surface_variant = THEME_COLORS['on_surface_variant']
    
    background = THEME_COLORS['background']
    on_background = THEME_COLORS['on_background']
    
    border = THEME_COLORS['border']
    border_light = THEME_COLORS['border_light']
    outline = THEME_COLORS['outline']
    
    error = THEME_COLORS['error']
    error_light = THEME_COLORS['error_light']
    success = THEME_COLORS['success']
    success_light = THEME_COLORS['success_light']
    warning = THEME_COLORS['warning']
    warning_light = THEME_COLORS['warning_light']
    info = THEME_COLORS['info']
    info_light = THEME_COLORS['info_light']
    
    st.markdown(
        f"""
        <style>
        /* DISABLE STREAMLIT'S DEFAULT THEME */
        .stApp {{
            background-color: {background} !important;
            color: {on_surface} !important;
        }}
        
        /* Force light theme on all elements */
        * {{
            color: {on_surface} !important;
        }}
        
        /* Specifically target problematic elements with more aggressive selectors */
        
        /* DOWNLOAD BUTTON - Force light theme */
        div.stDownloadButton > button {{
            background-color: {primary} !important;
            color: {on_primary} !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
        }}
        
        div.stDownloadButton > button:hover {{
            background-color: {primary_light} !important;
            color: {on_primary} !important;
        }}
        
        div.stDownloadButton > button p,
        div.stDownloadButton > button span,
        div.stDownloadButton > button div {{
            color: {on_primary} !important !important;
        }}

        /* FILE UPLOADER - Force light theme */
        section[data-testid="stFileUploader"] {{
            background-color: {surface} !important;
            border: 2px dashed {border} !important;
            border-radius: 12px !important;
        }}
        
        section[data-testid="stFileUploader"] * {{
            color: {on_surface} !important;
            background-color: transparent !important;
        }}
        
        section[data-testid="stFileUploader"] label {{
            color: {on_surface} !important;
        }}
        
        section[data-testid="stFileUploader"] small {{
            color: {on_surface_variant} !important;
        }}
        
        /* Uploaded file items */
        section[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
        section[data-testid="stFileUploader"] [data-testid="stFileUploaderFileSize"] {{
            color: {on_surface} !important;
            background-color: {surface_variant} !important;
        }}

        /* DATAFRAMES - Force light theme */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrameResizable"],
        .stDataFrame {{
            background-color: {surface} !important;
            color: {on_surface} !important;
        }}
        
        div[data-testid="stDataFrame"] table,
        div[data-testid="stDataFrameResizable"] table {{
            background-color: {surface} !important;
            color: {on_surface} !important;
        }}
        
        div[data-testid="stDataFrame"] th,
        div[data-testid="stDataFrameResizable"] th {{
            background-color: {surface_variant} !important;
            color: {on_surface} !important;
            border-color: {border} !important;
        }}
        
        div[data-testid="stDataFrame"] td,
        div[data-testid="stDataFrameResizable"] td {{
            background-color: {surface} !important;
            color: {on_surface} !important;
            border-color: {border_light} !important;
        }}
        
        div[data-testid="stDataFrame"] tr:hover td,
        div[data-testid="stDataFrameResizable"] tr:hover td {{
            background-color: {surface_variant} !important;
            color: {on_surface} !important;
        }}

        /* HEADER - Corporate Gradient */
        .app-header {{
            background: linear-gradient(135deg, {primary} 0%, {primary_light} 100%);
            padding: 2.5rem 2rem;
            color: {on_primary} !important;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
        }}
        
        .app-header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            color: {on_primary} !important;
            letter-spacing: -0.025em;
        }}
        
        .app-header p {{
            margin: 0.75rem 0 0 0;
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500;
        }}

        /* CARDS - Material 3 Elevation */
        .card {{
            background: {surface};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            border: 1px solid {border_light};
        }}
        
        .card-header {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: {on_surface} !important;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid {border_light};
        }}

        /* METRIC CARDS - Subtle Colors */
        .metric-card {{
            padding: 1.5rem 1rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
            background: {surface};
            border: 1px solid {border_light};
        }}
        
        .metric-card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }}

        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: {on_surface} !important;
            margin: 0.5rem 0;
        }}

        .metric-label {{
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            color: {on_surface_variant} !important;
            letter-spacing: 0.05em;
        }}

        /* ALERT BOXES - Material 3 */
        .alert {{
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            border-left: 4px solid;
            font-weight: 500;
            background: {surface};
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}

        .alert-success {{
            border-left-color: {success};
            background: {success_light};
            color: {on_surface} !important;
        }}

        .alert-info {{
            border-left-color: {info};
            background: {info_light};
            color: {on_surface} !important;
        }}

        .alert-warning {{
            border-left-color: {warning};
            background: {warning_light};
            color: {on_surface} !important;
        }}

        .alert-error {{
            border-left-color: {error};
            background: {error_light};
            color: {on_surface} !important;
        }}

        /* STAGE PROGRESS - Full Width Horizontal */
        .stage-container {{
            padding: 2rem 1.5rem;
            background: {surface};
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            border: 1px solid {border_light};
        }}

        .stage-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            max-width: 100%;
            margin: 0 auto;
        }}

        .stage-step {{
            flex: 0 0 auto;
            text-align: center;
            min-width: 120px;
        }}

        .stage-connector {{
            flex: 1 1 80px;
            height: 2px;
            background: {border_light};
            border-radius: 1px;
            max-width: 120px;
        }}

        .stage-connector.completed {{
            background: {primary};
        }}

        .stage-circle {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 1rem;
            margin: 0 auto 0.5rem auto;
            transition: all 0.2s ease;
            border: 2px solid;
        }}

        .stage-circle.active {{
            background: {primary};
            color: {on_primary} !important;
            border-color: {primary};
        }}

        .stage-circle.completed {{
            background: {success};
            color: {on_primary} !important;
            border-color: {success};
        }}

        .stage-circle.inactive {{
            background: {surface_variant};
            color: {on_surface_variant} !important;
            border-color: {border_light};
        }}

        .stage-label {{
            font-size: 0.875rem;
            color: {on_surface_variant} !important;
            font-weight: 500;
        }}

        .stage-label.active {{
            color: {primary} !important;
            font-weight: 600;
        }}

        /* SECTION DIVIDER */
        .section-divider {{
            height: 1px;
            background: {border_light};
            margin: 2rem 0;
            border: none;
        }}

        /* OPTIMIZATION LOADING - Center Aligned */
        .optimization-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem 2rem;
            background: {surface};
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
            min-height: 300px;
        }}

        .spinner {{
            width: 64px;
            height: 64px;
            border: 4px solid {border_light};
            border-top-color: {primary};
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        .optimization-text {{
            font-size: 1.5rem;
            font-weight: 600;
            color: {on_surface} !important;
            margin-top: 1.5rem;
        }}

        .optimization-subtext {{
            font-size: 1rem;
            color: {on_surface_variant} !important;
            margin-top: 0.5rem;
        }}
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
