"""
Postprocessing and Visualization Module
========================================

Transform solver results and create interactive Plotly visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
from typing import Dict, Any, List

import constants


def convert_solver_output_to_display(solver_result: Dict, instance: Dict) -> Dict[str, Any]:
    """
    Convert solver output to display-friendly format.
    
    Args:
        solver_result: Result dict from solve()
        instance: Problem instance data
        
    Returns:
        Display-ready dict with formatted data
    """
    best = solver_result.get('best')
    if not best:
        return None
    
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    formatted_dates = [d.strftime(constants.DATE_FORMAT_DISPLAY) for d in dates]
    
    # Build production summary
    production = {g: {} for g in grades}
    for (line, d), entries in best.get('production', {}).items():
        date_label = formatted_dates[d]
        for grade, qty in entries.items():
            production[grade].setdefault(date_label, 0)
            production[grade][date_label] += qty
    
    # Build inventory summary
    inventory = {g: {} for g in grades}
    for (grade, d), val in best.get('inventory', {}).items():
        if d == 0:
            inventory[grade]['initial'] = val
        elif d < len(dates):
            inventory[grade][formatted_dates[d]] = val
        else:
            inventory[grade]['final'] = val
    
    # Build stockout summary
    stockout = {g: {} for g in grades}
    for (grade, d), val in best.get('unmet', {}).items():
        if val > 0:
            stockout[grade][formatted_dates[d]] = val
    
    # Build assignment map for Gantt charts
    is_producing_map = {}
    for (line, d), grade in best.get('assign', {}).items():
        is_producing_map[(grade, line, d)] = True
    
    # Calculate transition count
    transitions = _count_transitions(best.get('assign', {}), lines, len(dates))
    
    return {
        'production': production,
        'inventory': inventory,
        'stockout': stockout,
        'is_producing_map': is_producing_map,
        'formatted_dates': formatted_dates,
        'dates': dates,
        'objective': best.get('objective'),
        'transitions': transitions,
    }


def _count_transitions(assign: Dict, lines: List[str], num_days: int) -> Dict:
    """Count grade transitions per line."""
    transition_count = {line: 0 for line in lines}
    
    for line in lines:
        last_grade = None
        for d in range(num_days):
            current_grade = assign.get((line, d))
            if current_grade and last_grade and current_grade != last_grade:
                transition_count[line] += 1
            if current_grade:
                last_grade = current_grade
    
    return {
        'per_line': transition_count,
        'total': sum(transition_count.values())
    }


def _build_grade_color_map(sorted_grades: List[str]) -> Dict[str, str]:
    """Generate consistent color mapping for grades."""
    color_map = {}
    for i, grade in enumerate(sorted_grades):
        color_map[grade] = constants.GRADE_COLORS[i % len(constants.GRADE_COLORS)]
    return color_map


def plot_production_visuals(display_result: Dict, instance: Dict, params: Dict) -> None:
    """
    Render production Gantt charts and schedule tables.
    
    Args:
        display_result: Processed solver output
        instance: Problem instance data
        params: Parameters including buffer_days
    """
    if display_result is None:
        st.info("No results to display.")
        return
    
    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = len(dates)
    sorted_grades = sorted(grades)
    grade_color_map = _build_grade_color_map(sorted_grades)
    shutdown_periods = instance.get('shutdown_day_indices', {})
    is_producing = display_result.get('is_producing_map', {})
    
    st.markdown("## 📅 Production Schedule")
    
    # Gantt chart for each line
    for line in lines:
        st.markdown(f"### 🏭 {line}")
        
        # Build Gantt data
        gantt_data = []
        for d in range(num_days):
            date = dates[d]
            for grade in sorted_grades:
                if (grade, line, d) in is_producing and is_producing[(grade, line, d)]:
                    gantt_data.append({
                        "Grade": grade,
                        "Start": date,
                        "Finish": date + timedelta(days=1),
                        "Line": line
                    })
        
        if not gantt_data:
            st.info(f"No production scheduled for {line}")
            continue
        
        gantt_df = pd.DataFrame(gantt_data)
        
        # Create Plotly timeline
        fig = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Grade",
            color="Grade",
            color_discrete_map=grade_color_map,
            category_orders={"Grade": sorted_grades},
        )
        
        # Add shutdown overlay
        if line in shutdown_periods and shutdown_periods[line]:
            shutdown_days = sorted(list(shutdown_periods[line]))
            start_shutdown = dates[shutdown_days[0]]
            end_shutdown = dates[shutdown_days[-1]] + timedelta(days=1)
            
            fig.add_vrect(
                x0=start_shutdown,
                x1=end_shutdown,
                fillcolor="red",
                opacity=0.15,
                layer="below",
                line_width=0,
                annotation_text="Shutdown",
                annotation_position="top left",
                annotation_font_size=12,
                annotation_font_color="#c62828"
            )
        
        # Styling
        fig.update_yaxes(
            autorange="reversed",
            title=None,
            showgrid=True,
            gridcolor="#e0e0e0"
        )
        
        fig.update_xaxes(
            title="Date",
            showgrid=True,
            gridcolor="#e0e0e0",
            tickformat="%d-%b"
        )
        
        fig.update_layout(
            height=350,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=60, r=160, t=40, b=60),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Schedule table
        _render_schedule_table(line, dates, sorted_grades, is_producing, grade_color_map)


def _render_schedule_table(line: str, dates: List, sorted_grades: List[str],
                           is_producing: Dict, grade_color_map: Dict) -> None:
    """Render detailed schedule table for a line."""
    st.markdown(f"**Detailed Schedule - {line}**")
    
    schedule_data = []
    current_grade = None
    start_day = None
    
    for d in range(len(dates)):
        date = dates[d]
        grade_today = None
        
        for grade in sorted_grades:
            if (grade, line, d) in is_producing and is_producing[(grade, line, d)]:
                grade_today = grade
                break
        
        if grade_today != current_grade:
            if current_grade is not None:
                end_date = dates[d - 1]
                duration = (end_date - start_day).days + 1
                schedule_data.append({
                    "Grade": current_grade,
                    "Start Date": start_day.strftime(constants.DATE_FORMAT_DISPLAY),
                    "End Date": end_date.strftime(constants.DATE_FORMAT_DISPLAY),
                    "Days": duration
                })
            current_grade = grade_today
            start_day = date
    
    if current_grade is not None:
        end_date = dates[-1]
        duration = (end_date - start_day).days + 1
        schedule_data.append({
            "Grade": current_grade,
            "Start Date": start_day.strftime(constants.DATE_FORMAT_DISPLAY),
            "End Date": end_date.strftime(constants.DATE_FORMAT_DISPLAY),
            "Days": duration
        })
    
    if schedule_data:
        schedule_df = pd.DataFrame(schedule_data)
        
        def color_grade(val):
            if val in grade_color_map:
                color = grade_color_map[val]
                return f'background-color: {color}; color: white; font-weight: bold; text-align: center;'
            return ''
        
        styled_df = schedule_df.style.applymap(color_grade, subset=['Grade'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info(f"No production data for {line}")


def plot_inventory_charts(display_result: Dict, instance: Dict, params: Dict) -> None:
    """
    Render inventory trend charts for each grade.
    
    Args:
        display_result: Processed solver output
        instance: Problem instance data
        params: Parameters including buffer_days
    """
    if display_result is None:
        st.info("No results to display.")
        return
    
    grades = instance['grades']
    dates = instance['dates']
    formatted_dates = display_result['formatted_dates']
    sorted_grades = sorted(grades)
    grade_color_map = _build_grade_color_map(sorted_grades)
    shutdown_periods = instance.get('shutdown_day_indices', {})
    buffer_days = params.get('buffer_days', 3)
    
    min_inventory = instance.get('min_inventory', {})
    max_inventory = instance.get('max_inventory', {})
    
    st.markdown("## 📦 Inventory Trends")
    
    for grade in sorted_grades:
        inv_map = display_result['inventory'].get(grade, {})
        
        # Build inventory time series
        inventory_values = []
        for d_idx, d in enumerate(dates):
            label = formatted_dates[d_idx]
            val = inv_map.get(label, inv_map.get('initial', 0) if d_idx == 0 else 0)
            inventory_values.append(val)
        
        last_actual_day = max(0, len(dates) - buffer_days - 1)
        
        # Key statistics
        start_val = inventory_values[0]
        end_val = inventory_values[last_actual_day]
        highest_val = max(inventory_values[:last_actual_day + 1]) if inventory_values else 0
        lowest_val = min(inventory_values[:last_actual_day + 1]) if inventory_values else 0
        
        start_x = dates[0]
        end_x = dates[last_actual_day]
        highest_x = dates[inventory_values.index(highest_val)] if highest_val in inventory_values else dates[0]
        lowest_x = dates[inventory_values.index(lowest_val)] if lowest_val in inventory_values else dates[0]
        
        # Create figure
        fig = go.Figure()
        
        # Main inventory line
        fig.add_trace(go.Scatter(
            x=dates,
            y=inventory_values,
            mode="lines+markers",
            name=grade,
            line=dict(color=grade_color_map.get(grade, '#636EFA'), width=3),
            marker=dict(size=6),
            hovertemplate="Date: %{x|%d-%b-%y}<br>Inventory: %{y:.0f} MT<extra></extra>"
        ))
        
        # Shutdown overlays
        shutdown_added = False
        for line in instance.get('allowed_lines', {}).get(grade, []):
            if line in shutdown_periods and shutdown_periods[line]:
                shutdown_days = sorted(list(shutdown_periods[line]))
                start_shutdown = dates[shutdown_days[0]]
                end_shutdown = dates[shutdown_days[-1]]
                
                fig.add_vrect(
                    x0=start_shutdown,
                    x1=end_shutdown + timedelta(days=1),
                    fillcolor="red",
                    opacity=0.1,
                    layer="below",
                    line_width=0,
                    annotation_text=f"Shutdown: {line}" if not shutdown_added else "",
                    annotation_position="top left",
                    annotation_font_size=12,
                    annotation_font_color="#c62828"
                )
                shutdown_added = True
        
        # Min/Max inventory lines
        min_inv_val = min_inventory.get(grade, 0)
        max_inv_val = max_inventory.get(grade, 10**9)
        
        if min_inv_val > 0:
            fig.add_hline(
                y=min_inv_val,
                line=dict(color="#ef4444", width=2, dash="dash"),
                annotation_text=f"Min: {min_inv_val:,.0f}",
                annotation_position="top left",
                annotation_font_color="#ef4444"
            )
        
        if max_inv_val < 10**9:
            fig.add_hline(
                y=max_inv_val,
                line=dict(color="#10b981", width=2, dash="dash"),
                annotation_text=f"Max: {max_inv_val:,.0f}",
                annotation_position="bottom left",
                annotation_font_color="#10b981"
            )
        
        # Key point annotations
        annotations = [
            dict(
                x=start_x, y=start_val,
                text=f"Start: {start_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=-40, ay=30,
                font=dict(color="#212121", size=11),
                bgcolor="white", bordercolor="#bdbdbd", borderwidth=1
            ),
            dict(
                x=end_x, y=end_val,
                text=f"End: {end_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=40, ay=30,
                font=dict(color="#212121", size=11),
                bgcolor="white", bordercolor="#bdbdbd", borderwidth=1
            ),
            dict(
                x=highest_x, y=highest_val,
                text=f"Peak: {highest_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=0, ay=-40,
                font=dict(color="#10b981", size=11),
                bgcolor="white", bordercolor="#bdbdbd", borderwidth=1
            ),
            dict(
                x=lowest_x, y=lowest_val,
                text=f"Low: {lowest_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=0, ay=40,
                font=dict(color="#ef4444", size=11),
                bgcolor="white", bordercolor="#bdbdbd", borderwidth=1
            )
        ]
        
        fig.update_layout(
            title=dict(
                text=f"Inventory Level - {grade}",
                font=dict(size=16, color="#212121")
            ),
            xaxis=dict(
                title="Date",
                showgrid=True,
                gridcolor="#e0e0e0",
                tickformat="%d-%b"
            ),
            yaxis=dict(
                title="Inventory Volume (MT)",
                showgrid=True,
                gridcolor="#e0e0e0"
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=60, r=80, t=80, b=60),
            height=420,
            showlegend=False
        )
        
        for ann in annotations:
            fig.add_annotation(
                x=ann['x'],
                y=ann['y'],
                text=ann['text'],
                showarrow=ann['showarrow'],
                arrowhead=ann['arrowhead'],
                ax=ann['ax'],
                ay=ann['ay'],
                font=ann['font'],
                bgcolor=ann['bgcolor'],
                bordercolor=ann['bordercolor'],
                borderwidth=ann.get('borderwidth', 1),
                borderpad=4,
                opacity=0.9
            )
        
        st.plotly_chart(fig, use_container_width=True)


def render_production_summary(display_result: Dict, instance: Dict) -> None:
    """Render production summary table."""
    st.markdown("## 📊 Production Summary")
    
    grades = instance['grades']
    lines = instance['lines']
    
    # Build summary data
    summary_data = []
    for grade in sorted(grades):
        row = {'Grade': grade}
        total = 0
        
        for line in lines:
            line_total = sum(
                display_result['production'].get(grade, {}).values()
            )
            row[line] = f"{line_total:,.0f}"
            total += line_total
        
        row['Total'] = f"{total:,.0f}"
        stockout_total = sum(display_result['stockout'].get(grade, {}).values())
        row['Stockout'] = f"{stockout_total:,.0f}"
        
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
