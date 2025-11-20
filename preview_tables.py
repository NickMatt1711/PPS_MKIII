"""
Preview Tables Module
=====================

Display input data with clean formatting.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

import constants


def format_dates_in_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Format datetime columns to display format."""
    df_copy = df.copy()
    for col in df_copy.columns:
        try:
            if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                df_copy[col] = df_copy[col].dt.strftime(constants.DATE_FORMAT_DISPLAY)
        except Exception:
            pass
    return df_copy


def show_preview_tables(instance: Dict[str, Any]) -> None:
    """Display preview of all input data in tabs."""
    
    tab1, tab2, tab3 = st.tabs(["🏭 Plant Data", "📦 Inventory Data", "📊 Demand Data"])
    
    with tab1:
        _show_plant_info(instance)
    
    with tab2:
        _show_inventory_info(instance)
    
    with tab3:
        _show_demand_info(instance)


def _show_plant_info(instance: Dict[str, Any]) -> None:
    """Display plant information."""
    plant_data = []
    for line in instance['lines']:
        capacity = instance['capacities'][line]
        shutdown_days = len(instance['shutdown_periods'].get(line, []))
        
        material_info = instance['material_running_info'].get(line, None)
        if material_info:
            running = f"{material_info[0]} ({material_info[1]} days)"
        else:
            running = "Not specified"
        
        plant_data.append({
            "Plant": line,
            "Capacity (MT/day)": f"{capacity:,.1f}",
            "Material Running": running,
            "Shutdown Days": shutdown_days
        })
    
    plant_df = pd.DataFrame(plant_data)
    st.dataframe(plant_df, use_container_width=True, hide_index=True, height=300)


def _show_inventory_info(instance: Dict[str, Any]) -> None:
    """Display inventory and grade information."""
    inv_data = []
    for grade in instance['grades']:
        allowed = ", ".join(instance['allowed_lines'].get(grade, []))
        
        # Check force start dates for this grade
        force_dates = []
        for key, date in instance['force_start_date'].items():
            if key[0] == grade and date is not None:
                force_dates.append(f"{key[1]}: {date.strftime(constants.DATE_FORMAT_DISPLAY)}")
        force_str = "; ".join(force_dates) if force_dates else "-"
        
        inv_data.append({
            "Grade": grade,
            "Opening Inv (MT)": f"{instance['initial_inventory'][grade]:,.1f}",
            "Min Inv (MT)": f"{instance['min_inventory'][grade]:,.1f}",
            "Max Inv (MT)": f"{instance['max_inventory'][grade]:,.1f}",
            "Min Closing (MT)": f"{instance['min_closing_inventory'][grade]:,.1f}",
            "Force Start": force_str,
            "Allowed Lines": allowed
        })
    
    inv_df = pd.DataFrame(inv_data)
    st.dataframe(inv_df, use_container_width=True, hide_index=True, height=300)


def _show_demand_info(instance: Dict[str, Any]) -> None:
    """Display demand forecast."""
    demand_data = []
    dates = instance['dates']
    
    for d, date in enumerate(dates):
        row = {"Date": date.strftime(constants.DATE_FORMAT_DISPLAY)}
        for grade in instance['grades']:
            demand_qty = instance['demand_data'][grade].get(date, 0)
            row[grade] = f"{demand_qty:,.1f}"
        demand_data.append(row)
    
    demand_df = pd.DataFrame(demand_data)
    st.dataframe(demand_df, use_container_width=True, height=400)
