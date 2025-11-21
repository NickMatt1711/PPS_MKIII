"""
Data preview and validation display module.

Provides interactive previews of input data with validation feedback.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any


def format_dates_in_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Format datetime columns in dataframe for display."""
    df_display = df.copy()
    for col in df_display.columns:
        try:
            if pd.api.types.is_datetime64_any_dtype(df_display[col]):
                df_display[col] = df_display[col].dt.strftime('%d-%b-%y')
        except Exception:
            pass
    return df_display


def show_data_preview_tabs(instance: Dict[str, Any]):
    """
    Display interactive tabs with data previews.
    
    Args:
        instance: Solver instance containing raw dataframes
    """
    plant_df = instance['raw_plant_df']
    inventory_df = instance['raw_inventory_df']
    demand_df = instance['raw_demand_df']
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏭 Plant Data",
        "📦 Inventory Data",
        "📊 Demand Data",
        "🔄 Transition Matrices"
    ])
    
    with tab1:
        _show_plant_preview(plant_df, instance)
    
    with tab2:
        _show_inventory_preview(inventory_df, instance)
    
    with tab3:
        _show_demand_preview(demand_df, instance)
    
    with tab4:
        _show_transition_matrices(instance)


def _show_plant_preview(plant_df: pd.DataFrame, instance: Dict[str, Any]):
    """Display plant data preview with validation."""
    plant_display = format_dates_in_dataframe(plant_df)
    st.dataframe(plant_display, use_container_width=True, height=300)
    
    # Shutdown summary
    shutdown_count = 0
    for plant in instance['lines']:
        if plant in instance['shutdown_day_indices'] and instance['shutdown_day_indices'][plant]:
            shutdown_count += 1
    
    if shutdown_count > 0:
        st.markdown(f'<span class="chip warning">🔧 {shutdown_count} plant(s) with scheduled shutdowns</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="chip success">✓ No shutdowns scheduled</span>', unsafe_allow_html=True)
    
    # Capacity summary
    st.markdown("**Capacity Summary**")
    capacity_data = []
    for plant, capacity in instance['capacities'].items():
        capacity_data.append({
            "Plant": plant,
            "Daily Capacity (MT)": capacity,
            "Material Running": instance['material_running_info'].get(plant, (None, None))[0] or "—",
            "Expected Days": instance['material_running_info'].get(plant, (None, None))[1] or "—"
        })
    st.dataframe(pd.DataFrame(capacity_data), use_container_width=True, hide_index=True)


def _show_inventory_preview(inventory_df: pd.DataFrame, instance: Dict[str, Any]):
    """Display inventory data preview with validation."""
    inventory_display = format_dates_in_dataframe(inventory_df)
    st.dataframe(inventory_display, use_container_width=True, height=300)
    
    grade_count = len(instance['grades'])
    st.markdown(f'<span class="chip info">📦 {grade_count} unique grade(s)</span>', unsafe_allow_html=True)
    
    # Inventory summary
    st.markdown("**Inventory Summary**")
    inv_summary = []
    for grade in instance['grades']:
        inv_summary.append({
            "Grade": grade,
            "Opening (MT)": instance['initial_inventory'][grade],
            "Min (MT)": instance['min_inventory'][grade],
            "Max (MT)": instance['max_inventory'][grade] if instance['max_inventory'][grade] < 1000000000 else "∞",
            "Min Closing (MT)": instance['min_closing_inventory'][grade],
            "Allowed Lines": ", ".join(instance['allowed_lines'][grade])
        })
    st.dataframe(pd.DataFrame(inv_summary), use_container_width=True, hide_index=True)


def _show_demand_preview(demand_df: pd.DataFrame, instance: Dict[str, Any]):
    """Display demand data preview with statistics."""
    demand_display = format_dates_in_dataframe(demand_df)
    st.dataframe(demand_display, use_container_width=True, height=300)
    
    num_days = len(instance['dates'])
    st.markdown(f'<span class="chip info">📅 {num_days} day(s) planning horizon</span>', unsafe_allow_html=True)
    
    # Demand statistics
    st.markdown("**Demand Statistics**")
    demand_stats = []
    for grade in instance['grades']:
        total_demand = sum(
            instance['demand'].get((grade, d), 0)
            for d in range(len(instance['dates']))
        )
        demand_stats.append({
            "Grade": grade,
            "Total Demand (MT)": f"{total_demand:,.0f}",
            "Avg Daily Demand (MT)": f"{total_demand / num_days:,.1f}" if num_days > 0 else "0"
        })
    st.dataframe(pd.DataFrame(demand_stats), use_container_width=True, hide_index=True)


def _show_transition_matrices(instance: Dict[str, Any]):
    """Display transition matrices for each plant."""
    transition_rules = instance['transition_rules']
    
    plants_with_transitions = [
        plant for plant, rules in transition_rules.items()
        if rules is not None
    ]
    
    if not plants_with_transitions:
        st.info("ℹ️ No transition matrices defined. All grade transitions are allowed.")
        return
    
    st.markdown(f"**Transition Matrices Loaded: {len(plants_with_transitions)} plant(s)**")
    
    for plant in plants_with_transitions:
        rules = transition_rules[plant]
        
        with st.expander(f"🔄 Transition Matrix - {plant}", expanded=False):
            # Create transition matrix dataframe for display
            all_grades = sorted(set(list(rules.keys()) + 
                                  [g for grades in rules.values() for g in grades]))
            
            matrix_data = []
            for prev_grade in all_grades:
                row = {"From Grade": prev_grade}
                for next_grade in all_grades:
                    if prev_grade in rules:
                        row[next_grade] = "✓" if next_grade in rules[prev_grade] else "✗"
                    else:
                        row[next_grade] = "—"
                matrix_data.append(row)
            
            matrix_df = pd.DataFrame(matrix_data)
            
            # Style the dataframe
            def style_transition(val):
                if val == "✓":
                    return 'background-color: #e8f5e9; color: #2e7d32; font-weight: bold; text-align: center;'
                elif val == "✗":
                    return 'background-color: #ffebee; color: #c62828; font-weight: bold; text-align: center;'
                return 'text-align: center;'
            
            styled_df = matrix_df.style.applymap(
                style_transition,
                subset=[col for col in matrix_df.columns if col != "From Grade"]
            )
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Transition statistics
            total_combinations = len(all_grades) * len(all_grades)
            allowed_transitions = sum(
                len(allowed) for allowed in rules.values()
            )
            
            st.caption(f"**Transition Rules**: {allowed_transitions} allowed out of {total_combinations} possible combinations")


def show_validation_summary(instance: Dict[str, Any]):
    """Display data validation summary."""
    st.markdown("### ✅ Data Validation Summary")
    
    validation_items = []
    
    # Check plants
    validation_items.append({
        "Category": "Plants",
        "Status": "✓",
        "Details": f"{len(instance['lines'])} plants configured"
    })
    
    # Check grades
    validation_items.append({
        "Category": "Grades",
        "Status": "✓",
        "Details": f"{len(instance['grades'])} grades defined"
    })
    
    # Check planning horizon
    validation_items.append({
        "Category": "Planning Horizon",
        "Status": "✓",
        "Details": f"{len(instance['dates'])} days"
    })
    
    # Check shutdowns
    shutdown_count = sum(
        1 for plant in instance['lines']
        if instance['shutdown_day_indices'].get(plant, [])
    )
    validation_items.append({
        "Category": "Shutdowns",
        "Status": "ℹ️" if shutdown_count > 0 else "✓",
        "Details": f"{shutdown_count} plants with scheduled shutdowns" if shutdown_count > 0 else "No shutdowns"
    })
    
    # Check transition matrices
    transition_count = sum(
        1 for rules in instance['transition_rules'].values()
        if rules is not None
    )
    validation_items.append({
        "Category": "Transition Matrices",
        "Status": "ℹ️" if transition_count > 0 else "—",
        "Details": f"{transition_count} plants with transition rules" if transition_count > 0 else "None defined"
    })
    
    validation_df = pd.DataFrame(validation_items)
    st.dataframe(validation_df, use_container_width=True, hide_index=True)
