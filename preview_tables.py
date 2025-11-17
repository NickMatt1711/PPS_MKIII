# preview_tables.py
import streamlit as st
import pandas as pd

def format_dates_if_any(df):
    """Format datetime columns to readable date strings."""
    df2 = df.copy()
    for col in df2.columns:
        try:
            if pd.api.types.is_datetime64_any_dtype(df2[col]):
                df2[col] = df2[col].dt.strftime('%d-%b-%y')
        except Exception:
            pass
    return df2

def show_preview_tables(instance):
    """
    Display preview tables for Plant, Inventory, and Demand data.
    Also shows transition matrices if available.
    """
    plant_df = instance['plant_df']
    inventory_df = instance['inventory_df']
    demand_df = instance['demand_df']
    
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
    
    # Display shutdown information
    st.markdown("---")
    st.subheader("🔧 Scheduled Shutdowns")
    shutdown_found = False
    for _, row in plant_df.iterrows():
        plant = row['Plant']
        shutdown_start = row.get('Shutdown Start Date')
        shutdown_end = row.get('Shutdown End Date')
        
        if pd.notna(shutdown_start) and pd.notna(shutdown_end):
            try:
                start_date = pd.to_datetime(shutdown_start).date()
                end_date = pd.to_datetime(shutdown_end).date()
                duration = (end_date - start_date).days + 1
                
                if start_date > end_date:
                    st.warning(f"⚠️ Invalid shutdown period for {plant}: Start date is after end date")
                else:
                    st.info(f"**{plant}**: Scheduled for shutdown from {start_date.strftime('%d-%b-%y')} to {end_date.strftime('%d-%b-%y')} ({duration} days)")
                    shutdown_found = True
            except Exception as e:
                st.warning(f"⚠️ Invalid shutdown dates for {plant}: {e}")
    
    if not shutdown_found:
        st.info("ℹ️ No plant shutdowns scheduled")
    
    # Display transition matrices
    transition_rules = instance.get('transition_rules', {})
    if transition_rules:
        st.markdown("---")
        st.subheader("🔄 Transition Matrices")
        for plant, rules in transition_rules.items():
            if rules:
                st.markdown(f"**{plant} Transition Rules**")
                # Convert rules dict to DataFrame for display
                grades = list(set(list(rules.keys()) + [g for allowed in rules.values() for g in allowed]))
                trans_df = pd.DataFrame(index=grades, columns=grades, data='No')
                for prev_grade, allowed_list in rules.items():
                    for next_grade in allowed_list:
                        trans_df.loc[prev_grade, next_grade] = 'Yes'
                st.dataframe(trans_df, use_container_width=True, height=240)
    else:
        st.info("ℹ️ No transition matrices detected")
