"""
Post-processing and visualization of optimization results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
from typing import Dict, List
from constants import CHART_COLORS


def create_production_summary(solution: Dict, grades: List[str], lines: List[str], solver) -> pd.DataFrame:
    """Create production summary DataFrame"""
    
    production_totals = {}
    grade_totals = {}
    plant_totals = {line: 0 for line in lines}
    stockout_totals = {}
    
    for grade in grades:
        production_totals[grade] = {}
        grade_totals[grade] = 0
        stockout_totals[grade] = 0
        
        # Sum production by line
        for line in lines:
            total_prod = 0
            for date, prod in solution['production'].get(grade, {}).items():
                # This is simplified - in reality we'd need line-specific data
                total_prod += prod
            production_totals[grade][line] = total_prod // len(lines)  # Rough estimate
            grade_totals[grade] += production_totals[grade][line]
            plant_totals[line] += production_totals[grade][line]
        
        # Sum stockouts
        for date, stockout in solution['stockout'].get(grade, {}).items():
            stockout_totals[grade] += stockout
    
    # Build DataFrame
    data = []
    for grade in grades:
        row = {'Grade': grade}
        for line in lines:
            row[line] = production_totals[grade][line]
        row['Total Produced'] = grade_totals[grade]
        row['Total Stockout'] = stockout_totals[grade]
        data.append(row)
    
    # Totals row
    totals_row = {'Grade': 'Total'}
    for line in lines:
        totals_row[line] = plant_totals[line]
    totals_row['Total Produced'] = sum(plant_totals.values())
    totals_row['Total Stockout'] = sum(stockout_totals.values())
    data.append(totals_row)
    
    return pd.DataFrame(data)


def create_gantt_chart(solution: Dict, line: str, dates: List, shutdown_periods: Dict, grade_colors: Dict) -> go.Figure:
    """Create Gantt chart for a production line"""
    
    grades = sorted(solution['is_producing'][line].keys())
    grade_color_map = grade_colors
    
    gantt_data = []
    for date_str, grade in solution['is_producing'][line].items():
        if grade:
            # Convert date string back to date object
            date = pd.to_datetime(date_str, format='%d-%b-%y').date()
            gantt_data.append({
                "Grade": grade,
                "Start": date,
                "Finish": date + timedelta(days=1),
                "Line": line
            })
    
    if not gantt_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No production data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    gantt_df = pd.DataFrame(gantt_data)
    
    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Grade",
        color="Grade",
        color_discrete_map=grade_color_map,
        title=f"Production Schedule - {line}"
    )
    
    # Add shutdown periods
    if line in shutdown_periods and shutdown_periods[line]:
        shutdown_days = shutdown_periods[line]
        start_shutdown = dates[shutdown_days[0]]
        end_shutdown = dates[shutdown_days[-1]] + timedelta(days=1)
        
        fig.add_vrect(
            x0=start_shutdown,
            x1=end_shutdown,
            fillcolor="red",
            opacity=0.2,
            layer="below",
            line_width=0,
            annotation_text="Shutdown",
            annotation_position="top left",
            annotation_font_size=14,
            annotation_font_color="red"
        )
    
    fig.update_yaxes(autorange="reversed", title=None)
    fig.update_xaxes(title="Date")
    fig.update_layout(
        height=350,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    
    return fig


def create_schedule_table(solution: Dict, line: str, dates: List, grade_colors: Dict) -> pd.DataFrame:
    """Create production schedule table for a line"""
    
    schedule_data = []
    current_grade = None
    start_day = None
    
    sorted_dates = sorted(dates)
    
    for i, date in enumerate(sorted_dates):
        date_str = date.strftime('%d-%b-%y')
        grade_today = solution['is_producing'][line].get(date_str)
        
        if grade_today != current_grade:
            if current_grade is not None:
                end_date = sorted_dates[i - 1]
                duration = (end_date - start_day).days + 1
                schedule_data.append({
                    "Grade": current_grade,
                    "Start Date": start_day.strftime("%d-%b-%y"),
                    "End Date": end_date.strftime("%d-%b-%y"),
                    "Days": duration
                })
            current_grade = grade_today
            start_day = date
    
    if current_grade is not None:
        end_date = sorted_dates[-1]
        duration = (end_date - start_day).days + 1
        schedule_data.append({
            "Grade": current_grade,
            "Start Date": start_day.strftime("%d-%b-%y"),
            "End Date": end_date.strftime("%d-%b-%y"),
            "Days": duration
        })
    
    return pd.DataFrame(schedule_data) if schedule_data else pd.DataFrame()


def create_inventory_chart(solution: Dict, grade: str, dates: List,
                           min_inventory: float, max_inventory: float,
                           allowed_lines: List[str], shutdown_periods: Dict,
                           initial_inventory: float) -> go.Figure:
    """Create inventory level chart for a grade"""
    
    inventory_values = []
    # Inject opening inventory on the first day
    first_date_str = dates[0].strftime('%d-%b-%y')
    if first_date_str not in solution['inventory'][grade]:
        solution['inventory'][grade][first_date_str] = initial_inventory
             
    for date in dates:
        date_str = date.strftime('%d-%b-%y')
        inv = solution['inventory'][grade].get(date_str, initial_inventory if date == dates[0] else 0)
        inventory_values.append(inv)

    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=inventory_values,
        mode="lines+markers",
        name=grade,
        line=dict(color=CHART_COLORS[0], width=3),
        marker=dict(size=6),
        hovertemplate="Date: %{x|%d-%b-%y}<br>Inventory: %{y:.0f} MT<extra></extra>"
    ))
    
    # Add shutdown periods
    for line in allowed_lines:
        if line in shutdown_periods and shutdown_periods[line]:
            shutdown_days = shutdown_periods[line]
            start_shutdown = dates[shutdown_days[0]]
            end_shutdown = dates[shutdown_days[-1]]
            
            fig.add_vrect(
                x0=start_shutdown,
                x1=end_shutdown + timedelta(days=1),
                fillcolor="red",
                opacity=0.1,
                layer="below",
                line_width=0
            )
    
    # Add min/max lines
    fig.add_hline(
        y=min_inventory,
        line=dict(color="red", width=2, dash="dash"),
        annotation_text=f"Min: {min_inventory:,.0f}",
        annotation_position="top left"
    )
    fig.add_hline(
        y=max_inventory,
        line=dict(color="green", width=2, dash="dash"),
        annotation_text=f"Max: {max_inventory:,.0f}",
        annotation_position="bottom left"
    )
    
    # Add annotations
    if inventory_values:
        start_val = inventory_values[0]
        end_val = inventory_values[-1]
        highest_val = max(inventory_values)
        lowest_val = min(inventory_values)
        
        annotations = [
            dict(x=dates[0], y=start_val, text=f"Start: {start_val:.0f}",
                 showarrow=True, arrowhead=2, ax=-40, ay=30),
            dict(x=dates[-1], y=end_val, text=f"End: {end_val:.0f}",
                 showarrow=True, arrowhead=2, ax=40, ay=30),
            dict(x=dates[inventory_values.index(highest_val)], y=highest_val,
                 text=f"High: {highest_val:.0f}", showarrow=True, arrowhead=2, ax=0, ay=-40),
            dict(x=dates[inventory_values.index(lowest_val)], y=lowest_val,
                 text=f"Low: {lowest_val:.0f}", showarrow=True, arrowhead=2, ax=0, ay=40)
        ]
        
        for ann in annotations:
            fig.add_annotation(**ann)
    
    fig.update_layout(
        title=f"Inventory Level - {grade}",
        xaxis_title="Date",
        yaxis_title="Inventory Volume (MT)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=420,
        showlegend=False
    )
    
    return fig
