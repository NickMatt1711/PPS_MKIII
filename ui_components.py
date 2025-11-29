"""
Material 3 Light Theme - COMPLETELY REFACTORED UI Components
Fixing all color inconsistencies and Streamlit override issues
"""

import streamlit as st

def apply_custom_css():
    """Apply Material 3 Light theme with proper specificity and overrides."""
    
    st.markdown(
        """
        <style>
        /* =============================================
        MATERIAL 3 LIGHT THEME - HIGH SPECIFICITY FIX
        ============================================= */
        
        /* CSS Variables with !important to ensure they apply */
        :root {
            /* Primary Colors */
            --md-primary: #6750A4 !important;
            --md-on-primary: #FFFFFF !important;
            --md-primary-container: #EADDFF !important;
            --md-on-primary-container: #21005D !important;
            
            /* Surface Colors */
            --md-surface: #FFFBFE !important;
            --md-on-surface: #1C1B1F !important;
            --md-surface-variant: #E7E0EC !important;
            --md-on-surface-variant: #49454F !important;
            --md-background: #F8FAFC !important;
            --md-on-background: #1C1B1F !important;
            
            /* Semantic Colors */
            --md-error: #B3261E !important;
            --md-error-container: #F9DEDC !important;
            --md-success: #0D652D !important;
            --md-success-container: #A7F0BA !important;
            --md-warning: #7C5800 !important;
            --md-warning-container: #FFDEA3 !important;
            
            /* Border & Outline */
            --md-outline: #79747E !important;
            --md-outline-variant: #C4C7C5 !important;
        }

        /* =============================================
        GLOBAL OVERRIDES - HIGH SPECIFICITY
        ============================================= */
        
        /* Force background colors */
        .stApp, .main, [data-testid="stAppViewContainer"] {
            background-color: var(--md-background) !important;
            color: var(--md-on-background) !important;
        }

        /* Force text colors throughout the app */
        .stApp *:not(button):not(.stButton *):not(.stDownloadButton *):not(.app-header *) {
            color: var(--md-on-background) !important;
        }

        /* =============================================
        HEADER STYLES
        ============================================= */
        .app-header {
            background: var(--md-primary) !important;
            color: var(--md-on-primary) !important;
            padding: 2rem 1.5rem !important;
            border-radius: 16px !important;
            margin: 1rem 0 2rem 0 !important;
            box-shadow: 0 4px 12px rgba(103, 80, 164, 0.15) !important;
            text-align: center !important;
        }
        
        .app-header h1 {
            margin: 0 !important;
            font-size: 2.25rem !important;
            font-weight: 400 !important;
            color: var(--md-on-primary) !important;
            letter-spacing: 0.5px !important;
        }
        
        .app-header p {
            color: var(--md-on-primary) !important;
            opacity: 0.9 !important;
            margin-top: 0.5rem !important;
            font-size: 1.1rem !important;
        }

        /* =============================================
        WIZARD PROGRESS - FIXED COLORS
        ============================================= */
        .stage-container {
            background: var(--md-surface) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin-bottom: 2rem !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15) !important;
        }
        
        .stage-row {
            display: flex !important;
            justify-content: space-between !important;
            align-items: flex-start !important;
            position: relative !important;
        }
        
        .stage-step {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            flex: 1 !important;
            position: relative !important;
            z-index: 2 !important;
        }
        
        .stage-circle {
            width: 32px !important;
            height: 32px !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            border: 2px solid !important;
            background: var(--md-surface) !important;
            transition: all 0.2s ease !important;
        }
        
        .stage-label {
            font-size: 0.75rem !important;
            font-weight: 500 !important;
            margin-top: 0.5rem !important;
            text-align: center !important;
            color: var(--md-on-surface-variant) !important;
        }
        
        /* Stage States - FIXED */
        .stage-circle.inactive {
            border-color: var(--md-outline-variant) !important;
            color: var(--md-outline) !important;
            background: var(--md-surface) !important;
        }
        
        .stage-circle.active {
            background: var(--md-primary) !important;
            border-color: var(--md-primary) !important;
            color: var(--md-on-primary) !important;
            box-shadow: 0 0 0 4px rgba(103, 80, 164, 0.2) !important;
        }
        
        .stage-circle.completed {
            background: var(--md-success) !important;
            border-color: var(--md-success) !important;
            color: var(--md-on-primary) !important;
        }
        
        .stage-label.active {
            color: var(--md-on-surface) !important;
            font-weight: 600 !important;
        }
        
        .stage-connector {
            position: absolute !important;
            top: 15px !important;
            left: 50% !important;
            right: 50% !important;
            height: 2px !important;
            background: var(--md-outline-variant) !important;
            z-index: 1 !important;
        }
        
        .stage-connector.completed {
            background: var(--md-success) !important;
        }

        /* =============================================
        BUTTONS - COMPLETE OVERHAUL
        ============================================= */
        
        /* Primary buttons - ALL button types */
        .stButton > button,
        .stDownloadButton > button,
        .stDownloadButton > a,
        section[data-testid="stFileUploader"] button,
        div[data-testid="stBaseButton-secondary"] > button,
        button[data-testid="baseButton-secondary"],
        .stButton > button:focus,
        .stDownloadButton > button:focus,
        .stDownloadButton > a:focus {
            background: var(--md-primary) !important;
            color: var(--md-on-primary) !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            box-shadow: 0 1px 3px rgba(103, 80, 164, 0.3) !important;
            transition: all 0.2s ease !important;
            min-height: 40px !important;
        }

        /* Force white text in ALL button content */
        .stButton > button *,
        .stDownloadButton > button *,
        .stDownloadButton > a *,
        section[data-testid="stFileUploader"] button *,
        div[data-testid="stBaseButton-secondary"] > button * {
            color: var(--md-on-primary) !important;
        }

        /* Button hover states */
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stDownloadButton > a:hover,
        section[data-testid="stFileUploader"] button:hover,
        div[data-testid="stBaseButton-secondary"] > button:hover {
            background: #5A4791 !important; /* Darker shade of primary */
            box-shadow: 0 4px 12px rgba(103, 80, 164, 0.4) !important;
            transform: translateY(-1px) !important;
            color: var(--md-on-primary) !important;
        }

        /* Download button specific fixes */
        .stDownloadButton > a {
            text-decoration: none !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: var(--md-on-primary) !important;
        }

        /* =============================================
        FILE UPLOADER - LIGHT THEME FIXED
        ============================================= */
        section[data-testid="stFileUploader"] {
            background: var(--md-surface) !important;
            border: 2px dashed var(--md-outline) !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            margin: 1rem 0 !important;
            transition: all 0.2s ease !important;
        }
        
        section[data-testid="stFileUploader"]:hover {
            border-color: var(--md-primary) !important;
            background: rgba(103, 80, 164, 0.05) !important;
        }
        
        /* File uploader text - ensure light theme */
        section[data-testid="stFileUploader"] span,
        section[data-testid="stFileUploader"] div,
        section[data-testid="stFileUploader"] p {
            color: var(--md-on-surface-variant) !important;
        }

        /* =============================================
        DATAFRAMES - LIGHT THEME ENSURED
        ============================================= */
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrameContainer"],
        div[data-testid="stDataFrame"] table,
        div[data-testid="stDataFrame"] thead,
        div[data-testid="stDataFrame"] tbody {
            background: var(--md-surface) !important;
            color: var(--md-on-surface) !important;
            border: 1px solid var(--md-outline-variant) !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        }
        
        div[data-testid="stDataFrame"] th {
            background: var(--md-surface-variant) !important;
            color: var(--md-on-surface-variant) !important;
            font-weight: 500 !important;
            border-bottom: 1px solid var(--md-outline-variant) !important;
        }
        
        div[data-testid="stDataFrame"] td {
            background: var(--md-surface) !important;
            color: var(--md-on-surface) !important;
            border-bottom: 1px solid var(--md-outline-variant) !important;
        }

        /* =============================================
        INPUT FIELDS - LIGHT THEME
        ============================================= */
        .stTextInput input,
        .stTextInput textarea,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input,
        .stSelectbox select {
            background: var(--md-surface) !important;
            border: 1px solid var(--md-outline) !important;
            border-radius: 8px !important;
            color: var(--md-on-surface) !important;
            padding: 0.75rem 1rem !important;
            font-size: 1rem !important;
        }
        
        .stTextInput input:focus,
        .stTextInput textarea:focus,
        .stNumberInput input:focus,
        .stDateInput input:focus,
        .stTimeInput input:focus,
        .stSelectbox select:focus {
            border-color: var(--md-primary) !important;
            border-width: 2px !important;
            box-shadow: 0 0 0 1px var(--md-primary) !important;
            outline: none !important;
        }

        /* =============================================
        ALERTS - MATERIAL DESIGN
        ============================================= */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15) !important;
            padding: 1rem 1.5rem !important;
            margin: 1rem 0 !important;
        }
        
        /* Base alert */
        div[data-testid="stAlert"]:not([class*="alert-"]) {
            background: var(--md-primary-container) !important;
            color: var(--md-on-primary-container) !important;
        }
        
        /* Semantic alerts */
        .alert-success {
            background: var(--md-success-container) !important;
            color: #0D652D !important;
        }
        
        .alert-info {
            background: var(--md-primary-container) !important;
            color: var(--md-on-primary-container) !important;
        }
        
        .alert-warning {
            background: var(--md-warning-container) !important;
            color: var(--md-warning) !important;
        }
        
        .alert-error {
            background: var(--md-error-container) !important;
            color: var(--md-error) !important;
        }
        
        /* Alert text */
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] strong {
            color: inherit !important;
            margin: 0 !important;
        }

        /* =============================================
        TABS - MATERIAL DESIGN
        ============================================= */
        .stTabs {
            background: var(--md-surface) !important;
            padding: 0 !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
            border-radius: 12px !important;
        }
        
        button[data-baseweb="tab"] {
            background: transparent !important;
            color: var(--md-on-surface-variant) !important;
            font-weight: 500 !important;
            padding: 1rem 1.5rem !important;
            border-bottom: 2px solid transparent !important;
            transition: all 0.2s ease !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--md-primary) !important;
            border-bottom-color: var(--md-primary) !important;
            background: rgba(103, 80, 164, 0.05) !important;
        }

        /* =============================================
        METRIC CARDS & CONTAINERS
        ============================================= */
        .card, .metric-card {
            background: var(--md-surface) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
            border: none !important;
        }
        
        .card-header {
            color: var(--md-on-surface) !important;
            font-size: 1.25rem !important;
            font-weight: 500 !important;
            margin-bottom: 1rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 1px solid var(--md-outline-variant) !important;
        }
        
        .metric-label {
            font-size: 0.875rem !important;
            color: var(--md-on-surface-variant) !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }
        
        .metric-value {
            font-size: 2rem !important;
            font-weight: 600 !important;
            color: var(--md-primary) !important;
            line-height: 1 !important;
        }

        /* =============================================
        UTILITY CLASSES
        ============================================= */
        .section-divider {
            margin: 2rem 0 !important;
            border: none !important;
            border-top: 1px solid var(--md-outline-variant) !important;
        }

        /* =============================================
        STREAMLIT SPECIFIC OVERRIDES
        ============================================= */
        
        /* Ensure all Streamlit text elements use our theme */
        .stMarkdown, .stText, .stNumber, .stDate, .stTime {
            color: var(--md-on-surface) !important;
        }
        
        /* Fix any remaining dark text */
        .st-bb, .st-bc, .st-bd, .st-be, .st-bf, .st-bg, .st-bh, .st-bi, .st-bj, .st-bk {
            color: var(--md-on-surface) !important;
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

    html = '<div class="stage-row">'
    
    for idx, (num, label) in enumerate(stages):
        status = "inactive"
        icon = num
        
        if idx == current_stage:
            status = "active"
        elif idx < current_stage:
            status = "completed"
            icon = "✓"
        
        html += '<div class="stage-step">'
        html += f"""
            <div class="stage-circle {status}">{icon}</div>
            <div class="stage-label {'active' if idx == current_stage else ''}">
                {label}
            </div>
        """
        html += '</div>'
        
        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            html += f'<div class="stage-connector {connector_class}"></div>'

    html += '</div>'

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
    try:
        # Create a simple template download
        template_data = b"Template file content would be here"
        
        st.download_button(
            label="📥 Download Template",
            data=template_data,
            file_name="polymer_production_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the Excel template file",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Template download error: {e}")
