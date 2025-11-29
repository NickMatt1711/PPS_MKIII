"""
Material 3 Light Theme - Corporate UI Components
Clean, professional design without sidebar
"""

import streamlit as st


def apply_custom_css():
    """Apply Material 3 Light theme for corporate application."""
    
    st.markdown(
        """
        <style>
        /* Global background */
        .stApp {
            background: #f8fafc;
        }

        /* File Uploader - Fixed Colors */
        section[data-testid="stFileUploader"] {
            border: 2px dashed #1e40af !important;
            background-color: #f8fafc !important;
        }

        section[data-testid="stFileUploader"] * {
            color: #1e293b !important;
        }

        section[data-testid="stFileUploader"] button {
            background: #1e40af !important;
            color: white !important;
        }

        /* Download Button - Fixed Colors */
        .stDownloadButton > button {
            background: #1e40af !important;
            color: white !important;
        }

        /* DataFrames & Tables */
        .stDataFrame, 
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrameContainer"] {
            background: white !important;
            color: #1e293b !important;
        }

        .stDataFrame *,
        div[data-testid="stDataFrame"] * {
            color: #1e293b !important;
            background: white !important;
        }

        /* Input Fields */
        .stNumberInput > div > div > input,
        .stTextInput > div > div > input,
        .stSelectbox > div > div {
            background: white !important;
            color: #1e293b !important;
            border: 1px solid #e2e8f0 !important;
        }

        .stNumberInput label,
        .stTextInput label,
        .stSelectbox label {
            color: #1e293b !important;
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
        <div style="
            background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
            padding: 2.5rem 2rem;
            color: white;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.15);
        ">
            <h1 style="margin: 0; font-size: 2.5rem; color: white;">{title}</h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stage_progress(current_stage: int) -> None:
    """Render clean stage progress indicator."""
    stages = ["Upload", "Preview & Configure", "Results"]
    
    st.markdown(
        f"""
        <div style="
            padding: 2rem 1.5rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            border: 1px solid #e2e8f0;
        ">
            <div style="display: flex; align-items: center; justify-content: center; gap: 1rem;">
        """,
        unsafe_allow_html=True,
    )
    
    for idx, stage in enumerate(stages):
        if idx < current_stage:
            status = "completed"
            icon = "✓"
            color = "#10b981"
        elif idx == current_stage:
            status = "active"
            icon = str(idx + 1)
            color = "#1e40af"
        else:
            status = "inactive"
            icon = str(idx + 1)
            color = "#94a3b8"
        
        st.markdown(
            f"""
            <div style="text-align: center; min-width: 100px;">
                <div style="
                    width: 48px; height: 48px; border-radius: 50%; 
                    display: flex; align-items: center; justify-content: center;
                    font-weight: 600; margin: 0 auto 0.5rem auto;
                    background: {color}; color: white; border: 2px solid {color};
                ">{icon}</div>
                <div style="font-size: 0.875rem; color: {color if idx == current_stage else '#64748b'}; 
                          font-weight: {600 if idx == current_stage else 500};">{stage}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        if idx < len(stages) - 1:
            connector_color = "#1e40af" if idx < current_stage else "#e2e8f0"
            st.markdown(
                f'<div style="width: 60px; height: 2px; background: {connector_color};"></div>',
                unsafe_allow_html=True,
            )
    
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_card(title: str):
    """Open a card container."""
    st.markdown(
        f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
        ">
            <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; color: #1e293b;">
                {title}
            </div>
        """,
        unsafe_allow_html=True,
    )


def close_card():
    """Close the card container."""
    st.markdown("</div>", unsafe_allow_html=True)


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
    
