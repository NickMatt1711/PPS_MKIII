"""
UI helper to preview and validate uploaded data.
"""

import streamlit as st
import pandas as pd

def show_preview(plant_df: pd.DataFrame, inventory_df: pd.DataFrame, demand_df: pd.DataFrame):
    st.subheader("🏭 Plant Data")
    st.dataframe(plant_df, use_container_width=True)
    st.subheader("📦 Inventory Data")
    st.dataframe(inventory_df, use_container_width=True)
    st.subheader("📊 Demand Data (first 40 rows)")
    st.dataframe(demand_df.head(40), use_container_width=True)
