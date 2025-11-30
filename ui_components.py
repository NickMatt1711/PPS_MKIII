"""
Material 3 Light Theme - Corporate UI Components
Clean, professional design without sidebar
"""

import streamlit as st
from constants import THEME_COLORS

def apply_custom_css():
    """Apply Material 3 Light theme for corporate application."""
    
    st.markdown(
        """
        <style>
        /* GLOBAL */
        .stApp, .main { background: #f8fafc !important; }
        *, p, span, div, label { color: #1e293b !important; }

        /* HEADER */
        .app-header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            padding: 2.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .app-header h1, .app-header p { color: white !important; }

        /* BUTTONS - ALL UNIFIED */
        .stButton > button,
        .stDownloadButton > button,
        section[data-testid="stFileUploader"] button {
            background: #1e40af !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 2rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        
        .stButton > button *,
        .stDownloadButton > button *,
        section[data-testid="stFileUploader"] button * {
            color: white !important;
        }

        /* FILE UPLOADER */
        section[data-testid="stFileUploader"] {
            background: white !important;
            border: 2px dashed #cbd5e1 !important;
            border-radius: 12px !important;
            padding: 2rem !important;
        }
        
        section[data-testid="stFileUploader"] label,
        section[data-testid="stFileUploader"] span,
        section[data-testid="stFileUploader"] div:not(button) {
            color: #1e293b !important;
        }

        /* DATAFRAMES - FIX TEXT */
        [data-testid="stDataFrame"] table,
        [data-testid="stDataFrame"] thead,
        [data-testid="stDataFrame"] tbody,
        [data-testid="stDataFrame"] th,
        [data-testid="stDataFrame"] td {
            color: #1e293b !important;
            background: white !important;
        }
        
        [data-testid="stDataFrame"] thead th {
            background: #f1f5f9 !important;
            font-weight: 600 !important;
        }

        /* INPUTS */
        .stNumberInput input,
        .stTextInput input {
            border: 1px solid #cbd5e1 !important;
            background: white !important;
            color: #1e293b !important;
        }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] {
            display: flex !important;
            width: 100% !important;
            background: white !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            flex: 1 !important;
            color: #64748b !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #1e40af !important;
            color: white !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] * {
            color: white !important;
        }

        /* STAGE PROGRESS */
        .stage-container {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        
        .stage-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
        }
        
        .stage-step { text-align: center; min-width: 120px; }
        
        .stage-connector {
            flex: 1;
            height: 2px;
            background: #e2e8f0;
            max-width: 120px;
        }
        
        .stage-connector.completed { background: #1e40af; }
        
        .stage-circle {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem;
            font-weight: 600;
            border: 2px solid;
        }
        
        .stage-circle.active {
            background: #1e40af;
            color: white !important;
            border-color: #1e40af;
        }
        
        .stage-circle.completed {
            background: #10b981;
            color: white !important;
            border-color: #10b981;
        }
        
        .stage-circle.inactive {
            background: #f8fafc;
            color: #94a3b8 !important;
            border-color: #e2e8f0;
        }
        
        .stage-label { font-size: 0.875rem; color: #64748b !important; }
        .stage-label.active { color: #1e40af !important; font-weight: 600; }

        /* CARDS */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }

        /* METRICS */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
        }
        .metric-value { font-size: 2rem; font-weight: 700; color: #1e293b !important; }
        .metric-label { font-size: 0.875rem; color: #64748b !important; }

        /* ALERTS */
        .alert { padding: 1rem; border-radius: 8px; margin: 1rem 0; }
        .alert-success { background: #f0fdf4; border-left: 4px solid #10b981; }
        .alert-error { background: #fef2f2; border-left: 4px solid #ef4444; }
        .alert-warning { background: #fffbeb; border-left: 4px solid #f59e0b; }
        .alert-info { background: #f0f9ff; border-left: 4px solid #3b82f6; }

        .section-divider { height: 1px; background: #e2e8f0; margin: 2rem 0; }
        </style>
        """, 
        unsafe_allow_html=True
    )


def render_header(title: str, subtitle: str = ""):
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div class="app-header"><h1>{title}</h1>{subtitle_html}</div>', unsafe_allow_html=True)


def render_stage_progress(current_stage: int) -> None:
    stages = [("1", "Upload"), ("2", "Preview & Configure"), ("3", "Results")]
    current_stage = max(0, min(current_stage, 2))
    
    html = '<div class="stage-row">'
    for idx, (num, label) in enumerate(stages):
        status = "completed" if idx < current_stage else ("active" if idx == current_stage else "inactive")
        icon = "✓" if idx < current_stage else num
        
        html += f'<div class="stage-step"><div class="stage-circle {status}">{icon}</div>'
        html += f'<div class="stage-label {"active" if idx == current_stage else ""}">{label}</div></div>'
        
        if idx < 2:
            conn_class = "completed" if idx < current_stage else ""
            html += f'<div class="stage-connector {conn_class}"></div>'
    
    html += '</div>'
    st.markdown(f'<div class="stage-container">{html}</div>', unsafe_allow_html=True)


def render_card(title: str, icon: str = ""):
    st.markdown(f'<div class="card"><div class="card-header">{icon} {title}</div>', unsafe_allow_html=True)


def close_card():
    st.markdown("</div>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, col):
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)


def render_alert(message: str, alert_type: str = "info"):
    icons = {"success": "✓", "info": "ℹ", "warning": "⚠", "error": "✕"}
    st.markdown(f'<div class="alert alert-{alert_type}"><strong>{icons.get(alert_type, "ℹ")}</strong><span>{message}</span></div>', unsafe_allow_html=True)


def render_section_divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_download_template_button():
    from pathlib import Path
    try:
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        if template_path.exists():
            with open(template_path, "rb") as f:
                st.download_button("📥 Download Template", f.read(), "polymer_production_template.xlsx", 
                                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.error("Template file not found")
    except Exception as e:
        st.error(f"Error: {e}")
