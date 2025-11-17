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

def show_core_previews(xls):
    """
    Show Plant, Inventory, Demand and transition sheets in the preview.
    Returns plant_df, inventory_df, demand_df, transition_map
    """
    plant_df = pd.read_excel(xls, sheet_name='Plant')
    inventory_df = pd.read_excel(xls, sheet_name='Inventory')
    demand_df = pd.read_excel(xls, sheet_name='Demand')

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

    # Show transition sheets (those that contain 'transition' in the name)
    all_names = xls.sheet_names
    transition_sheets = [s for s in all_names if 'transition' in s.lower()]
    if transition_sheets:
        st.markdown("---")
        st.subheader("🔁 Transition Matrices (detected)")
        for s in transition_sheets:
            try:
                df = pd.read_excel(xls, sheet_name=s, index_col=0)
                st.markdown(f"**{s}**")
                st.dataframe(df, use_container_width=True, height=240)
            except Exception:
                try:
                    df = pd.read_excel(xls, sheet_name=s)
                    st.markdown(f"**{s}**")
                    st.dataframe(df, use_container_width=True, height=240)
                except Exception as e:
                    st.warning(f"Could not load transition sheet {s}: {e}")
    else:
        st.info("No transition sheets detected (no sheet names contain 'transition').")

    # Return loaded dataframes for downstream use
    transition_map = {}
    for s in transition_sheets:
        try:
            df = pd.read_excel(xls, sheet_name=s, index_col=0)
            transition_map[s] = df
        except Exception:
            transition_map[s] = None

    return plant_df, inventory_df, demand_df, transition_map
