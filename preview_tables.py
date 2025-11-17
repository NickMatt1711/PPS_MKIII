# preview_tables.py
import streamlit as st
import pandas as pd

def format_dates_if_any(df):
    df2 = df.copy()
    for col in df2.columns:
        try:
            if pd.api.types.is_datetime64_any_dtype(df2[col]):
                df2[col] = df2[col].dt.strftime('%d-%b-%y')
        except Exception:
            pass
    return df2

def show_preview_tables(instance):  # Changed from show_core_previews to show_preview_tables
    """
    Show Plant, Inventory, Demand and transition sheets in the preview.
    """
    plant_df = instance.get('plant_df')
    inventory_df = instance.get('inventory_df')
    demand_df = instance.get('demand_df')

    st.markdown("### 📋 Data Preview & Validation")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🏭 Plant Data")
        st.dataframe(format_dates_if_any(plant_df), use_container_width=True, height=300)
    with col2:
        st.subheader("📦 Inventory Data")
        st.dataframe(format_dates_if_any(inventory_df), use_container_width=True, height=300)
    with col3:
        st.subheader("📊 Demand Data")
        st.dataframe(format_dates_if_any(demand_df), use_container_width=True, height=300)

    # Show transition rules from instance
    transition_rules = instance.get('transition_rules', {})
    if transition_rules:
        st.markdown("---")
        st.subheader("🔁 Transition Rules (processed)")
        for plant_name, rules in transition_rules.items():
            with st.expander(f"Transition Rules for {plant_name}"):
                rules_df = pd.DataFrame({
                    'From Grade': list(rules.keys()),
                    'Allowed Next Grades': [', '.join(allowed) for allowed in rules.values()]
                })
                st.dataframe(rules_df, use_container_width=True)

    # Show rerun rules
    rerun_allowed = instance.get('rerun_allowed', {})
    if rerun_allowed:
        st.markdown("---")
        st.subheader("🔄 Rerun Rules")
        rerun_df = pd.DataFrame({
            'Grade': list(rerun_allowed.keys()),
            'Rerun Allowed': ['Yes' if allowed else 'No' for allowed in rerun_allowed.values()]
        })
        st.dataframe(rerun_df, use_container_width=True)
