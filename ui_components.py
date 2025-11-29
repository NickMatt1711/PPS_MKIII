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
        /* File Uploader - Blue Theme */
        section[data-testid="stFileUploader"] {
            border: 2px dashed #1e40af !important;
            background-color: white !important;
        }

        section[data-testid="stFileUploader"] * {
            color: #1e293b !important;
        }

        section[data-testid="stFileUploader"] button {
            background: #1e40af !important;
            color: white !important;
        }

        /* Download Button - Blue Theme */
        .stDownloadButton > button {
            background: #1e40af !important;
            color: white !important;
        }

        /* DataFrames - White Background */
        .stDataFrame {
            background-color: white !important;
        }

        /* Input Fields - White Background */
        .stNumberInput input, .stTextInput input, .stSelectbox div {
            background-color: white !important;
            color: #1e293b !important;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )


def render_header(title: str, subtitle: str = ""):
    """Render corporate app header."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
            padding: 2.5rem 2rem;
            color: white;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
        ">
            <h1 style="margin: 0; color: white;">{title}</h1>
            <p style="margin: 0.75rem 0 0 0; color: rgba(255,255,255,0.9);">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
