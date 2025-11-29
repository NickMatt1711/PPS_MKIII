# FILE: ui_components.py
"""
Material 3 Light Theme – UI helpers
"""

import streamlit as st


def apply_custom_css():
    st.markdown(
        """
        <style>
        :root {
            --md-sys-color-primary: #5E7CE2;
            --md-sys-color-on-primary: #FFFFFF;
            --md-sys-color-primary-container: #E8EEFF;
            --md-sys-color-secondary: #4BAF39;
            --md-sys-color-on-surface: #1C1B1F;
            --md-sys-color-surface: #FFFFFF;
            --md-sys-color-surface-variant: #E7E0EC;
            --md-sys-color-background: #F7F8FA;
            --md-sys-color-outline: #79747E;
            --md-sys-color-outline-variant: #CAC5D0;
            --md-elevation-1: 0px 1px 3px rgba(0,0,0,0.12);
            --md-elevation-2: 0px 2px 6px rgba(0,0,0,0.12);
            --md-shape-corner-small: 8px;
            --md-shape-corner-medium: 12px;
            --md-shape-corner-large: 16px;
        }

        /* Force light theme across Streamlit DOM */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background-color: var(--md-sys-color-background) !important;
            color: var(--md-sys-color-on-surface) !important;
        }
        [data-testid="stAppViewContainer"] > .main {
            background-color: var(--md-sys-color-background) !important;
        }

        /* Header */
        .app-header {
            background: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary) !important;
            padding: 20px;
            border-radius: var(--md-shape-corner-large);
            margin: 12px 0;
            box-shadow: var(--md-elevation-1);
            text-align: center;
        }
        .app-header h1 { margin: 0; font-size: 28px; font-weight: 600; }

        /* Cards */
        .m3-card {
            background: var(--md-sys-color-surface);
            border-radius: var(--md-shape-corner-medium);
            padding: 18px;
            margin-bottom: 18px;
            box-shadow: var(--md-elevation-1);
            border: 1px solid var(--md-sys-color-outline-variant);
        }

        /* Uploader */
        [data-testid="stFileUploader"] {
            background-color: var(--md-sys-color-surface) !important;
            border: 2px dashed var(--md-sys-color-outline) !important;
            border-radius: var(--md-shape-corner-medium) !important;
            padding: 18px !important;
        }
        [data-testid="stFileUploader"] * { color: var(--md-sys-color-on-surface) !important; }

        /* Buttons */
        .stButton button, .stDownloadButton button {
            background-color: var(--md-sys-color-primary) !important;
            color: var(--md-sys-color-on-primary) !important;
            border-radius: var(--md-shape-corner-small) !important;
            padding: 8px 14px !important;
            font-weight: 600 !important;
            border: none !important;
            box-shadow: var(--md-elevation-1) !important;
        }
        .stButton button:hover, .stDownloadButton button:hover {
            box-shadow: var(--md-elevation-2) !important;
            transform: translateY(-2px);
        }

        /* Tabs fill width */
        .stTabs [data-baseweb="tab-list"] { display:flex !important; width:100% !important; }
        button[data-baseweb="tab"] { flex:1 !important; text-align:center !important; border-radius:0 !important; }
        button[data-baseweb="tab"][aria-selected="true"] {
            border-bottom: 3px solid var(--md-sys-color-primary) !important;
            color: var(--md-sys-color-primary) !important;
        }

        /* DataFrames light */
        [data-testid="stDataFrame"] table { background-color: var(--md-sys-color-surface) !important; }
        [data-testid="stDataFrame"] th {
            background-color: var(--md-sys-color-surface-variant) !important;
            color: var(--md-sys-color-on-surface) !important;
            font-weight: 600 !important;
        }
        [data-testid="stDataFrame"] td { background-color: var(--md-sys-color-surface) !important; color: var(--md-sys-color-on-surface) !important; }
        [data-testid="stDataFrame"] tbody tr:hover td {
            background: color-mix(in srgb, var(--md-sys-color-primary-container) 12%, transparent) !important;
        }

        /* Stage progress */
        .stage-row { display:flex; width:100%; justify-content:space-between; align-items:center; margin-bottom:12px; }
        .stage-step { flex:1; text-align:center; }
        .stage-connector { flex:1; height: 2px; background: var(--md-sys-color-outline-variant); margin:0 6px; }
        .stage-connector.completed { background: var(--md-sys-color-success); }

        /* Small utilities */
        .section-divider { height:1px; background: var(--md-sys-color-outline-variant); margin:18px 0; border:none; }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str = ""):
    subtitle_html = f"<div style='opacity:0.9;margin-top:6px'>{subtitle}</div>" if subtitle else ""
    st.markdown(f"<div class='app-header'><h1>{title}</h1>{subtitle_html}</div>", unsafe_allow_html=True)


def render_stage_progress(current_stage_index: int):
    stages = [("Upload",), ("Review & Configure",), ("Results",)]
    total = len(stages)
    idx = max(0, min(current_stage_index, total - 1))

    html = '<div class="stage-row">'
    for i, s in enumerate(stages):
        status = "inactive"
        if i < idx:
            status = "completed"
            icon = "✓"
        elif i == idx:
            status = "active"
            icon = str(i + 1)
        else:
            icon = str(i + 1)

        html += f"""
            <div class='stage-step'>
                <div style='display:inline-block;padding:10px;border-radius:999px;border:2px solid var(--md-sys-color-outline-variant);
                             background: {'var(--md-sys-color-primary)' if status=='active' else 'var(--md-sys-color-surface)'}; color: {'var(--md-sys-color-on-primary)' if status=='active' else 'var(--md-sys-color-on-surface)'}'>
                    {icon}
                </div>
                <div style='margin-top:6px;font-size:0.9rem;color:var(--md-sys-color-on-surface)'>
                    {s[0]}
                </div>
            </div>
        """
        if i < total - 1:
            conn_class = "completed" if i < idx else ""
            html += f"<div class='stage-connector {conn_class}'></div>"

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_alert(message: str, kind: str = "info"):
    color_map = {
        "info": "var(--md-sys-color-primary-container)",
        "success": "var(--md-sys-color-success-container)",
        "warning": "var(--md-sys-color-tertiary)",
        "error": "var(--md-sys-color-error-container)"
    }
    bg = color_map.get(kind, "var(--md-sys-color-primary-container)")
    st.markdown(f"<div class='m3-card' style='background:{bg};'>{message}</div>", unsafe_allow_html=True)


def render_section_divider():
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, col):
    with col:
        st.markdown(f"""
            <div class="m3-card" style="text-align:center">
                <div style="font-size:0.9rem;color:var(--md-sys-color-on-surface)">{label}</div>
                <div style="font-size:1.6rem;font-weight:600;color:var(--md-sys-color-primary)">{value}</div>
            </div>
        """, unsafe_allow_html=True)


def render_download_template_button():
    # Lightweight placeholder: creates a small CSV in-memory template for download
    import io
    import pandas as pd
    df = pd.DataFrame({"Example": []})
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Plant", index=False)
        df.to_excel(writer, sheet_name="Inventory", index=False)
        df.to_excel(writer, sheet_name="Demand", index=False)
    buf.seek(0)
    st.download_button("📥 Download Template", data=buf, file_name="template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
