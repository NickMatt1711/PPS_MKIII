# ui_components.py
import streamlit as st

def inject_test1_css():
    st.markdown("""
    <style>
    .app-bar { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color: white; text-align:center; padding:1.4rem; border-radius:12px; }
    .metric-card { background:white; border-radius:12px; padding:1rem; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
    [data-testid="stFileUploader"] { background: linear-gradient(135deg,#f5f7fa 0%,#e8eef5 100%); border-radius:12px; padding:1rem; border:2px dashed #667eea; }
    .chip { display:inline-block; padding:0.3rem 0.6rem; border-radius:12px; font-weight:600; }
    </style>
    """, unsafe_allow_html=True)

def header():
    st.markdown("""
    <div class="app-bar">
        <h1>🏭 Polymer Production Scheduler</h1>
        <p style="margin-top:0.3rem; opacity:0.95;">Optimized Multi-Plant Production Planning</p>
    </div>
    """, unsafe_allow_html=True)

def footer():
    st.markdown("""
    <div style="text-align:center; color:#9e9e9e; font-size:0.9rem; padding:1rem 0;">
        <strong>Polymer Production Scheduler</strong> • Powered by OR-Tools & Streamlit
    </div>
    """, unsafe_allow_html=True)
