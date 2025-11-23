"""
Postprocessing functions for production optimization results
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from constants import CHART_COLORS, SS_GRADE_COLORS


def get_or_create_grade_colors(grades):
    """Get or create consistent colors for grades"""
    if SS_GRADE_COLORS in st.session_state and st.session_state[SS_GRADE_COLORS]:
        grade_colors = st.session_state[SS_GRADE_COLORS]
        # Check if we have colors for all grades
        if all(grade in grade_colors for grade in grades):
            return grade_colors
    else:
        grade_colors = {}

    # Assign colors from CHART_COLORS, repeating if necessary
    for i, grade in enumerate(grades):
        grade_colors[grade] = CHART_COLORS[i % len(CHART_COLORS)]

    st.session_state[SS_GRADE_COLORS] = grade_colors
    return grade_colors


def create_gantt_chart(solution, line, dates, shutdown_periods, grade_colors):
    """Create a Gantt chart for a production line"""
    
    # Extract production data for this line
    production_data = []
    for d, date in enumerate(dates):
        date_str = date.strftime('%d-%b-%y')
        grade = solution['is_producing'][line].get(date_str)
        if grade and grade != 'None':
            production_data.append({
                'Grade': grade,
                'Start': d,
                'Finish': d + 1,
                'Date': date_str,
                'Color': grade_colors.get(grade, '#CCCCCC')
            })
    
    if not production_data:
        # Return empty figure if no production data
        fig = go.Figure()
        fig.update_layout(
            title=f"Production Schedule - {line}",
            xaxis_title="Day",
            yaxis_title="Grade",
            showlegend=False
        )
        return fig
    
    # Create Gantt chart
    fig = go.Figure()
    
    # Add production bars
    for item in production_data:
        fig.add_trace(go.Bar(
            x=[item['Finish'] - item['Start']],
            y=[item['Grade']],
            base=item['Start'],
            orientation='h',
            marker=dict(color=item['Color']),
            hoverinfo='text',
            hovertext=f"Grade: {item['Grade']}<br>Date: {item['Date']}<br>Day: {item['Start']}",
            name=item['Grade'],
            showlegend=False
        ))
    
    # Add shutdown periods
    if line in shutdown_periods and shutdown_periods[line]:
        for shutdown_day in shutdown_periods[line]:
            if shutdown_day < len(dates):
                fig.add_vrect(
                    x0=shutdown_day - 0.5,
                    x1=shutdown_day + 0.5,
                    fillcolor="red",
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                    annotation_text="Shutdown",
                    annotation_position="top left"
                )
    
    fig.update_layout(
        title=f"Production Schedule - {line}",
        xaxis_title="Day",
        yaxis_title="Grade",
        barmode='stack',
        showlegend=False,
        height=400
    )
    
    return fig


def create_schedule_table(solution, line, dates, grade_colors):
    """Create a schedule table for a production line"""
    
    schedule_data = []
    for d, date in enumerate(dates):
        date_str = date.strftime('%d-%b-%y')
        grade = solution['is_producing'][line].get(date_str)
        schedule_data.append({
            'Date': date_str,
            'Day': d + 1,
            'Grade': grade if grade and grade != 'None' else '-',
            'Production (MT)': solution['production'].get(grade, {}).get(date_str, 0) if grade and grade != 'None' else 0
        })
    
    return pd.DataFrame(schedule_data)


def create_inventory_chart(solution, grade, dates, min_inventory, max_inventory, allowed_lines, shutdown_periods, grade_colors, initial_inventory, buffer_days=0):
    """Create an inventory chart for a grade"""
    
    inventory_levels = []
    dates_formatted = []
    
    # Add initial inventory
    inventory_levels.append(initial_inventory)
    dates_formatted.append('Initial')
    
    # Add daily inventory levels
    for d, date in enumerate(dates):
        date_str = date.strftime('%d-%b-%y')
        inventory = solution['inventory'][grade].get(date_str, 0)
        inventory_levels.append(inventory)
        dates_formatted.append(date_str)
    
    # Add final inventory if available
    if 'final' in solution['inventory'][grade]:
        inventory_levels.append(solution['inventory'][grade]['final'])
        dates_formatted.append('Final')
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    # Add inventory line
    fig.add_trace(
        go.Scatter(
            x=dates_formatted,
            y=inventory_levels,
            mode='lines+markers',
            name='Inventory',
            line=dict(color=grade_colors.get(grade, '#5E7CE2'), width=3),
            marker=dict(size=6)
        ),
        secondary_y=False
    )
    
    # Add minimum inventory line
    if min_inventory > 0:
        fig.add_trace(
            go.Scatter(
                x=dates_formatted,
                y=[min_inventory] * len(dates_formatted),
                mode='lines',
                name='Min Inventory',
                line=dict(color='red', width=2, dash='dash'),
                opacity=0.7
            ),
            secondary_y=False
        )
    
    # Add maximum inventory line
    if max_inventory < float('inf'):
        fig.add_trace(
            go.Scatter(
                x=dates_formatted,
                y=[max_inventory] * len(dates_formatted),
                mode='lines',
                name='Max Inventory',
                line=dict(color='orange', width=2, dash='dash'),
                opacity=0.7
            ),
            secondary_y=False
        )
    
    # Add stockout markers
    stockout_dates = []
    stockout_values = []
    if grade in solution['stockout']:
        for date_str, stockout in solution['stockout'][grade].items():
            if stockout > 0:
                stockout_dates.append(date_str)
                stockout_values.append(stockout)
    
    if stockout_dates:
        fig.add_trace(
            go.Scatter(
                x=stockout_dates,
                y=[inventory_levels[dates_formatted.index(date)] if date in dates_formatted else 0 for date in stockout_dates],
                mode='markers',
                name='Stockout',
                marker=dict(color='red', size=10, symbol='x'),
                hovertext=[f"Stockout: {val} MT" for val in stockout_values]
            ),
            secondary_y=False
        )
    
    # Update layout
    fig.update_layout(
        title=f"Inventory Profile - {grade}",
        xaxis_title="Date",
        yaxis_title="Inventory (MT)",
        hovermode='closest',
        height=400,
        showlegend=True
    )
    
    return fig


def create_production_summary(solution, grades, lines, solver):
    """Create a production summary table"""
    
    summary_data = []
    
    for grade in grades:
        total_production = sum(solution['production'][grade].values()) if grade in solution['production'] else 0
        total_demand = 0  # This would need to be calculated from demand data
        total_stockout = sum(solution['stockout'][grade].values()) if grade in solution['stockout'] else 0
        
        # Count production days
        production_days = 0
        for line in lines:
            for date, prod_grade in solution['is_producing'][line].items():
                if prod_grade == grade:
                    production_days += 1
        
        summary_data.append({
            'Grade': grade,
            'Total Production (MT)': total_production,
            'Production Days': production_days,
            'Total Stockout (MT)': total_stockout
        })
    
    # Add totals row
    if summary_data:
        total_production = sum(item['Total Production (MT)'] for item in summary_data)
        total_days = sum(item['Production Days'] for item in summary_data)
        total_stockout = sum(item['Total Stockout (MT)'] for item in summary_data)
        
        summary_data.append({
            'Grade': 'Total',
            'Total Production (MT)': total_production,
            'Production Days': total_days,
            'Total Stockout (MT)': total_stockout
        })
    
    return pd.DataFrame(summary_data)


def calculate_line_utilization(solution, lines, capacities, num_days):
    """Calculate line utilization rates"""
    
    utilization_data = []
    
    for line in lines:
        total_capacity = capacities[line] * num_days
        actual_production = 0
        
        for grade in solution['production']:
            for date, production in solution['production'][grade].items():
                # Check if this production was on this line
                if (date in solution['is_producing'][line] and 
                    solution['is_producing'][line][date] == grade):
                    actual_production += production
        
        utilization = (actual_production / total_capacity * 100) if total_capacity > 0 else 0
        
        utilization_data.append({
            'Line': line,
            'Utilization (%)': round(utilization, 1),
            'Actual Production (MT)': actual_production,
            'Total Capacity (MT)': total_capacity
        })
    
    return pd.DataFrame(utilization_data)
