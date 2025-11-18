"""
Preview Tables Module
=====================

Display and validate input data with interactive tables and summaries.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from . import constants


def format_dates_in_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format datetime columns to display format.
    
    Args:
        df: DataFrame potentially containing datetime columns
        
    Returns:
        DataFrame with formatted dates
    """
    df_copy = df.copy()
    for col in df_copy.columns:
        try:
            if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                df_copy[col] = df_copy[col].dt.strftime(constants.DATE_FORMAT_DISPLAY)
        except Exception:
            pass
    return df_copy


def show_preview_tables(instance: Dict[str, Any]) -> None:
    """
    Display comprehensive preview of all input data.
    
    Args:
        instance: Problem instance dictionary from data_loader
    """
    st.markdown("## 📋 Input Data Preview")
    
    # Create tabs for different data views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏭 Plants",
        "📦 Grades & Inventory",
        "📊 Demand",
        "🔄 Transitions",
        "📈 Summary"
    ])
    
    with tab1:
        _show_plant_info(instance)
    
    with tab2:
        _show_inventory_info(instance)
    
    with tab3:
        _show_demand_info(instance)
    
    with tab4:
        _show_transition_info(instance)
    
    with tab5:
        _show_summary_statistics(instance)


def _show_plant_info(instance: Dict[str, Any]) -> None:
    """Display plant/line information."""
    st.markdown("### Production Lines Overview")
    
    # Build plant summary DataFrame
    plant_data = []
    for line in instance['lines']:
        capacity = instance['capacities'][line]
        shutdown_days = len(instance['shutdown_day_indices'].get(line, set()))
        
        material_info = instance['material_running'].get(line, None)
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
    st.dataframe(plant_df, use_container_width=True, hide_index=True)
    
    # Show shutdown details
    shutdowns = [
        line for line in instance['lines']
        if instance['shutdown_day_indices'].get(line, set())
    ]
    
    if shutdowns:
        st.markdown("#### 🔧 Planned Shutdowns")
        for line in shutdowns:
            shutdown_indices = sorted(list(instance['shutdown_day_indices'][line]))
            if shutdown_indices:
                start_date = instance['dates'][shutdown_indices[0]]
                end_date = instance['dates'][shutdown_indices[-1]]
                st.info(
                    f"**{line}**: {start_date.strftime(constants.DATE_FORMAT_DISPLAY)} "
                    f"to {end_date.strftime(constants.DATE_FORMAT_DISPLAY)} "
                    f"({len(shutdown_indices)} days)"
                )
    else:
        st.success("✓ No shutdowns scheduled during planning horizon")


def _show_inventory_info(instance: Dict[str, Any]) -> None:
    """Display inventory and grade information."""
    st.markdown("### Grade Configuration")
    
    # Build inventory DataFrame
    inv_data = []
    for grade in instance['grades']:
        allowed = ", ".join(instance['allowed_lines'].get(grade, []))
        
        force_start = instance['force_start_date'].get(grade, None)
        force_str = force_start.strftime(constants.DATE_FORMAT_DISPLAY) if force_start else "-"
        
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
    st.dataframe(inv_df, use_container_width=True, hide_index=True)
    
    # Show run length constraints per grade-line combination
    st.markdown("### Run Length Constraints")
    
    run_data = []
    for grade in instance['grades']:
        for line in instance['allowed_lines'].get(grade, []):
            key = (grade, line)
            min_run = instance['min_run_days'].get(key, 1)
            max_run = instance['max_run_days'].get(key, 9999)
            rerun = "Yes" if instance['rerun_allowed'].get(key, True) else "No"
            
            run_data.append({
                "Grade": grade,
                "Line": line,
                "Min Run Days": min_run,
                "Max Run Days": max_run if max_run < 9999 else "Unlimited",
                "Rerun Allowed": rerun
            })
    
    run_df = pd.DataFrame(run_data)
    st.dataframe(run_df, use_container_width=True, hide_index=True, height=300)


def _show_demand_info(instance: Dict[str, Any]) -> None:
    """Display demand forecast information."""
    st.markdown("### Demand Forecast")
    
    # Build demand DataFrame
    demand_data = []
    dates = instance['dates']
    
    for d_idx, date in enumerate(dates):
        row = {"Date": date.strftime(constants.DATE_FORMAT_DISPLAY)}
        for grade in instance['grades']:
            demand_qty = instance['demand'].get((grade, d_idx), 0)
            row[grade] = f"{demand_qty:,.1f}"
        demand_data.append(row)
    
    demand_df = pd.DataFrame(demand_data)
    st.dataframe(demand_df, use_container_width=True, height=400)
    
    # Demand statistics
    st.markdown("### Demand Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Total Demand by Grade")
        total_demand = {}
        for grade in instance['grades']:
            total = sum(
                instance['demand'].get((grade, d), 0)
                for d in range(len(dates))
            )
            total_demand[grade] = total
        
        demand_summary = pd.DataFrame([
            {"Grade": g, "Total Demand (MT)": f"{qty:,.1f}"}
            for g, qty in total_demand.items()
        ])
        st.dataframe(demand_summary, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### Daily Demand Range")
        demand_ranges = {}
        for grade in instance['grades']:
            demands = [
                instance['demand'].get((grade, d), 0)
                for d in range(len(dates))
            ]
            demand_ranges[grade] = (min(demands), max(demands), sum(demands) / len(demands))
        
        range_df = pd.DataFrame([
            {
                "Grade": g,
                "Min": f"{r[0]:,.1f}",
                "Max": f"{r[1]:,.1f}",
                "Avg": f"{r[2]:,.1f}"
            }
            for g, r in demand_ranges.items()
        ])
        st.dataframe(range_df, use_container_width=True, hide_index=True)


def _show_transition_info(instance: Dict[str, Any]) -> None:
    """Display transition matrix information."""
    st.markdown("### Grade Transition Rules")
    
    has_transitions = any(
        instance['transition_rules'].get(line) is not None
        for line in instance['lines']
    )
    
    if not has_transitions:
        st.info("ℹ️ No transition matrices defined. All grade transitions are allowed.")
        return
    
    for line in instance['lines']:
        rules = instance['transition_rules'].get(line)
        if rules is None:
            st.markdown(f"#### {line}")
            st.info("No transition matrix. All transitions allowed.")
            continue
        
        st.markdown(f"#### {line} - Transition Matrix")
        
        # Build transition matrix for display
        grades = instance['grades']
        matrix_data = []
        
        for prev_grade in grades:
            row = {"From Grade": prev_grade}
            for curr_grade in grades:
                if prev_grade == curr_grade:
                    row[curr_grade] = "Same"
                else:
                    allowed_next = rules.get(prev_grade, [])
                    row[curr_grade] = "✓" if curr_grade in allowed_next else "✗"
            matrix_data.append(row)
        
        matrix_df = pd.DataFrame(matrix_data)
        st.dataframe(matrix_df, use_container_width=True)
        
        # Transition statistics
        total_transitions = len(grades) * (len(grades) - 1)
        allowed_count = sum(
            len([ng for ng in rules.get(pg, []) if ng != pg])
            for pg in grades
        )
        
        st.caption(
            f"Allowed transitions: {allowed_count} / {total_transitions} "
            f"({100 * allowed_count / total_transitions:.1f}%)"
        )


def _show_summary_statistics(instance: Dict[str, Any]) -> None:
    """Display overall summary statistics."""
    st.markdown("### Problem Instance Summary")
    
    # Calculate key metrics
    num_grades = len(instance['grades'])
    num_lines = len(instance['lines'])
    num_days = len(instance['dates'])
    
    total_capacity = sum(instance['capacities'].values()) * num_days
    total_demand = sum(instance['demand'].values())
    
    # Calculate potential decision variables
    potential_vars = num_grades * num_lines * num_days
    
    # Count constraints
    num_shutdowns = sum(
        len(instance['shutdown_day_indices'].get(line, set()))
        for line in instance['lines']
    )
    
    num_force_starts = len(instance['force_start_date'])
    
    has_transitions = sum(
        1 for line in instance['lines']
        if instance['transition_rules'].get(line) is not None
    )
    
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Problem Dimensions")
        st.metric("Grades", num_grades)
        st.metric("Production Lines", num_lines)
        st.metric("Planning Days", num_days)
        st.metric("Decision Variables", f"~{potential_vars:,}")
    
    with col2:
        st.markdown("#### Capacity & Demand")
        st.metric("Total Capacity", f"{total_capacity:,.0f} MT")
        st.metric("Total Demand", f"{total_demand:,.0f} MT")
        utilization = (total_demand / total_capacity * 100) if total_capacity > 0 else 0
        st.metric("Capacity Utilization", f"{utilization:.1f}%")
    
    with col3:
        st.markdown("#### Constraints")
        st.metric("Shutdown Days", num_shutdowns)
        st.metric("Force Start Dates", num_force_starts)
        st.metric("Lines with Transitions", has_transitions)
    
    # Problem complexity assessment
    st.markdown("### Complexity Assessment")
    
    if potential_vars < 1000:
        complexity = "Low"
        color = "success"
        message = "This is a small problem that should solve quickly (< 1 minute)"
    elif potential_vars < 10000:
        complexity = "Medium"
        color = "info"
        message = "This is a medium-sized problem (may take 1-5 minutes)"
    else:
        complexity = "High"
        color = "warning"
        message = "This is a large problem (may take 5-15 minutes or more)"
    
    st.markdown(f"""
    <div class="material-card">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="flex: 1;">
                <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
                    Complexity: <span style="color: {constants.COLOR_SUCCESS if complexity == 'Low' else constants.COLOR_INFO if complexity == 'Medium' else constants.COLOR_WARNING};">{complexity}</span>
                </div>
                <div style="color: #757575;">{message}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Data quality checks
    st.markdown("### Data Quality Checks")
    
    checks = []
    
    # Check 1: Capacity vs demand
    if total_demand > total_capacity * 1.1:
        checks.append(("❌", "Warning: Total demand exceeds capacity by >10%"))
    elif total_demand > total_capacity:
        checks.append(("⚠️", "Caution: Total demand slightly exceeds capacity"))
    else:
        checks.append(("✅", "Capacity is sufficient for total demand"))
    
    # Check 2: Opening inventory
    low_inventory_grades = [
        g for g in instance['grades']
        if instance['initial_inventory'][g] < instance['min_inventory'][g]
    ]
    if low_inventory_grades:
        checks.append((
            "⚠️",
            f"Opening inventory below minimum for: {', '.join(low_inventory_grades)}"
        ))
    else:
        checks.append(("✅", "Opening inventory meets minimum requirements"))
    
    # Check 3: Force start dates
    invalid_force_starts = []
    for grade, force_date in instance['force_start_date'].items():
        if force_date and force_date not in instance['dates']:
            invalid_force_starts.append(grade)
    
    if invalid_force_starts:
        checks.append((
            "⚠️",
            f"Force start dates outside horizon for: {', '.join(invalid_force_starts)}"
        ))
    else:
        checks.append(("✅", "All force start dates within planning horizon"))
    
    # Check 4: Transition restrictions
    if has_transitions > 0:
        checks.append(("ℹ️", f"Transition rules active for {has_transitions} lines"))
    else:
        checks.append(("ℹ️", "No transition restrictions (fully flexible)"))
    
    for icon, message in checks:
        st.markdown(f"{icon} {message}")
