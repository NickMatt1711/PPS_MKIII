"""
Modern UI elements: step indicator, metric cards, result tabs, progress utilities.
"""

import streamlit as st
from typing import Dict

def render_header():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#667eea,#764ba2);padding:20px;border-radius:12px;color:white;text-align:center;">
      <h1 style="margin:0;">🏭 Polymer Production Scheduler</h1>
      <div>Optimized Multi-Plant Production Planning</div>
    </div>
    """, unsafe_allow_html=True)

def step_indicator(step:int):
    st.markdown(f"<div style='display:flex;gap:12px;margin-top:12px;'>"
                f"<div style='flex:1;text-align:center;'><strong>{'✔' if step>1 else '1'}</strong><div>Upload</div></div>"
                f"<div style='flex:1;text-align:center;'><strong>{'✔' if step>2 else '2'}</strong><div>Configure</div></div>"
                f"<div style='flex:1;text-align:center;'><strong>{3 if step<3 else '✔'}</strong><div>Results</div></div>"
                f"</div>", unsafe_allow_html=True)

def metric_row(kpis: Dict[str, str]):
    cols = st.columns(len(kpis))
    for (label, value), c in zip(kpis.items(), cols):
        with c:
            st.markdown(f"<div style='padding:12px;border-radius:8px;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,0.06)'>"
                        f"<div style='font-size:0.8rem;font-weight:600;color:#666'>{label}</div>"
                        f"<div style='font-size:1.5rem;font-weight:700'>{value}</div></div>", unsafe_allow_html=True)

def results_tabs(production_df, inventory_df, gantt_fig):
    tab1, tab2, tab3 = st.tabs(["📅 Production Schedule", "📦 Inventory", "📊 Analytics"])
    with tab1:
        st.markdown("### Production Schedule")
        st.dataframe(production_df if not production_df.empty else "No production data", use_container_width=True)
        st.plotly_chart(gantt_fig, use_container_width=True)
    with tab2:
        st.markdown("### Inventory trends")
        st.dataframe(inventory_df if not inventory_df.empty else "No inventory data", use_container_width=True)
    with tab3:
        st.markdown("### Analytics")
        st.markdown("- KPI summaries shown above.")
