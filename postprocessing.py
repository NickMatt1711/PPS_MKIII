"""
Postprocessing functions for production optimization results with rich visuals
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import matplotlib.colors as mcolors
from datetime import timedelta
import numpy as np
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
    """Create a Gantt chart for a production line with shutdown periods"""
    
    # Extract production data for this line
    production_data = []
    for d, date in enumerate(dates):
        date_str = date.strftime('%d-%b-%y')
        grade = solution['is_producing'][line].get(date_str)
        if grade and grade != 'None':
            production_data.append({
                'Grade': grade,
                'Start': date,
                'Finish': date + timedelta(days=1),
                'Date': date_str,
                'Day': d,
                'Color': grade_colors.get(grade, '#CCCCCC')
            })
    
    if not production_data:
        # Return empty figure if no production data
        fig = go.Figure()
        fig.update_layout(
            title=f"Production Schedule - {line}",
            xaxis_title="Date",
            yaxis_title="Grade",
            height=400,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig
    
    # Create DataFrame for plotting
    gantt_df = pd.DataFrame(production_data)
    
    # Create the Gantt chart
    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish", 
        y="Grade",
        color="Grade",
        color_discrete_map=grade_colors,
        title=f"Production Schedule - {line}"
    )
    
    # Add shutdown period visualization
    if line in shutdown_periods and shutdown_periods[line]:
        shutdown_days = shutdown_periods[line]
        if shutdown_days:
            start_shutdown = dates[shutdown_days[0]]
            end_shutdown = dates[shutdown_days[-1]] + timedelta(days=1)
            
            fig.add_vrect(
                x0=start_shutdown,
                x1=end_shutdown,
                fillcolor="red",
                opacity=0.2,
                layer="below",
                line_width=0,
                annotation_text="SHUTDOWN",
                annotation_position="top left",
                annotation_font_size=14,
                annotation_font_color="red"
            )
    
    # Update layout for better appearance
    fig.update_yaxes(
        autorange="reversed",
        title=None,
        showgrid=True,
        gridcolor="lightgray",
        gridwidth=1
    )
    
    fig.update_xaxes(
        title="Date",
        showgrid=True,
        gridcolor="lightgray",
        gridwidth=1,
        tickformat="%d-%b",
        dtick="D1"
    )
    
    fig.update_layout(
        height=400,
        bargap=0.2,
        showlegend=True,
        legend_title_text="Grade",
        legend=dict(
            traceorder="normal",
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="lightgray",
            borderwidth=1
        ),
        xaxis=dict(showline=True, showticklabels=True),
        yaxis=dict(showline=True),
        margin=dict(l=60, r=160, t=60, b=60),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
    )
    
    return fig


def create_schedule_table(solution, line, dates, grade_colors):
    """Create a detailed schedule table for a production line"""
    
    schedule_data = []
    current_grade = None
    start_day = None
    run_length = 0
    
    for d, date in enumerate(dates):
        date_str = date.strftime('%d-%b-%y')
        grade = solution['is_producing'][line].get(date_str)
        
        if grade != current_grade:
            # End the previous run
            if current_grade is not None and current_grade != 'None':
                end_date = dates[d - 1] if d > 0 else dates[0]
                schedule_data.append({
                    'Grade': current_grade,
                    'Start Date': start_day.strftime('%d-%b-%y'),
                    'End Date': end_date.strftime('%d-%b-%y'),
                    'Duration (days)': run_length,
                    'Total Production (MT)': sum(
                        solution['production'].get(current_grade, {}).get(
                            dates[i].strftime('%d-%b-%y'), 0
                        ) for i in range(d - run_length, d)
                    )
                })
            
            # Start new run
            current_grade = grade
            start_day = date
            run_length = 1 if grade and grade != 'None' else 0
        else:
            run_length += 1
    
    # Add the final run
    if current_grade is not None and current_grade != 'None':
        end_date = dates[-1]
        schedule_data.append({
            'Grade': current_grade,
            'Start Date': start_day.strftime('%d-%b-%y'),
            'End Date': end_date.strftime('%d-%b-%y'),
            'Duration (days)': run_length,
            'Total Production (MT)': sum(
                solution['production'].get(current_grade, {}).get(
                    dates[i].strftime('%d-%b-%y'), 0
                ) for i in range(len(dates) - run_length, len(dates))
            )
        })
    
    return pd.DataFrame(schedule_data)


def create_inventory_chart(solution, grade, dates, min_inventory, max_inventory, 
                          allowed_lines, shutdown_periods, grade_colors, 
                          initial_inventory, buffer_days=0):
    """Create an inventory chart for a grade with shutdown periods and stockout markers"""
    
    # Calculate inventory levels
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
    
    # Create figure
    fig = go.Figure()
    
    # Add inventory line
    fig.add_trace(
        go.Scatter(
            x=dates_formatted,
            y=inventory_levels,
            mode='lines+markers',
            name='Inventory Level',
            line=dict(color=grade_colors.get(grade, '#5E7CE2'), width=3),
            marker=dict(size=6, symbol='circle'),
            hovertemplate='<b>%{x}</b><br>Inventory: %{y:,.0f} MT<extra></extra>'
        )
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
                opacity=0.7,
                hovertemplate='Min Inventory: %{y:,.0f} MT<extra></extra>'
            )
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
                opacity=0.7,
                hovertemplate='Max Inventory: %{y:,.0f} MT<extra></extra>'
            )
        )
    
    # Add stockout markers
    stockout_dates = []
    stockout_values = []
    if grade in solution['stockout']:
        for date_str, stockout in solution['stockout'][grade].items():
            if stockout > 0:
                stockout_dates.append(date_str)
                # Find the inventory level for this date
                if date_str in dates_formatted:
                    idx = dates_formatted.index(date_str)
                    stockout_values.append(inventory_levels[idx])
                else:
                    stockout_values.append(0)
    
    if stockout_dates:
        fig.add_trace(
            go.Scatter(
                x=stockout_dates,
                y=stockout_values,
                mode='markers',
                name='Stockout Event',
                marker=dict(
                    color='red', 
                    size=12, 
                    symbol='x-thin',
                    line=dict(width=2, color='darkred')
                ),
                hovertemplate='<b>%{x}</b><br>Stockout Occurred<br>Inventory: %{y:,.0f} MT<extra></extra>'
            )
        )
    
    # Add shutdown periods for plants that produce this grade
    shutdown_added = set()
    for line in allowed_lines:
        if line in shutdown_periods and shutdown_periods[line]:
            for shutdown_day in shutdown_periods[line]:
                if shutdown_day < len(dates):
                    shutdown_date = dates[shutdown_day].strftime('%d-%b-%y')
                    if shutdown_date not in shutdown_added and shutdown_date in dates_formatted:
                        fig.add_vline(
                            x=shutdown_date,
                            line_dash="dot",
                            line_color="red",
                            opacity=0.3,
                            annotation_text=f"Shutdown" if shutdown_date not in shutdown_added else "",
                            annotation_position="top"
                        )
                        shutdown_added.add(shutdown_date)
    
    # Calculate key metrics for annotations
    last_actual_day = len(dates) - buffer_days - 1
    actual_inventory = inventory_levels[1:last_actual_day+2]  # From day 1 to last actual day
    
    if actual_inventory:
        start_val = inventory_levels[1]  # Day 1 inventory
        end_val = inventory_levels[last_actual_day+1] if last_actual_day+1 < len(inventory_levels) else inventory_levels[-1]
        highest_val = max(actual_inventory)
        lowest_val = min(actual_inventory)
        
        # Add annotations for key points
        annotations = []
        
        # Start annotation
        annotations.append(dict(
            x=dates_formatted[1], y=start_val,
            text=f"Start: {start_val:,.0f}",
            showarrow=True,
            arrowhead=2,
            ax=-40, ay=-30,
            bgcolor="white",
            bordercolor="gray",
            borderwidth=1
        ))
        
        # End annotation
        if end_val != start_val:
            annotations.append(dict(
                x=dates_formatted[last_actual_day+1] if last_actual_day+1 < len(dates_formatted) else dates_formatted[-1],
                y=end_val,
                text=f"End: {end_val:,.0f}",
                showarrow=True,
                arrowhead=2,
                ax=40, ay=-30,
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1
            ))
        
        # Highest point annotation
        highest_idx = actual_inventory.index(highest_val) + 1
        if highest_idx < len(dates_formatted) and highest_val != start_val and highest_val != end_val:
            annotations.append(dict(
                x=dates_formatted[highest_idx], y=highest_val,
                text=f"High: {highest_val:,.0f}",
                showarrow=True,
                arrowhead=2,
                ax=0, ay=-40,
                bgcolor="white",
                bordercolor="gray",
                borderwidth=1
            ))
        
        # Lowest point annotation  
        lowest_idx = actual_inventory.index(lowest_val) + 1
        if lowest_idx < len(dates_formatted) and lowest_val != start_val and lowest_val != end_val:
            annotations.append(dict(
                x=dates_formatted[lowest_idx], y=lowest_val,
                text=f"Low: {lowest_val:,.0f}",
                showarrow=True,
                arrowhead=2,
                ax=0, ay=40,
                bgcolor="white",
                bordercolor="gray", 
                borderwidth=1
            ))
    
    # Update layout
    fig.update_layout(
        title=f"Inventory Profile - {grade}",
        xaxis_title="Date",
        yaxis_title="Inventory (MT)",
        hovermode='closest',
        height=500,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            tickangle=45
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray'
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.9)'
        )
    )
    
    # Add annotations to figure
    for annotation in annotations:
        fig.add_annotation(annotation)
    
    return fig


def create_production_summary(solution, grades, lines, solver):
    """Create a comprehensive production summary table"""
    
    summary_data = []
    
    for grade in grades:
        # Calculate total production
        total_production = sum(solution['production'][grade].values()) if grade in solution['production'] else 0
        
        # Calculate production days
        production_days = 0
        for line in lines:
            for date, prod_grade in solution['is_producing'][line].items():
                if prod_grade == grade:
                    production_days += 1
        
        # Calculate total stockout
        total_stockout = sum(solution['stockout'][grade].values()) if grade in solution['stockout'] else 0
        
        # Calculate average daily production
        avg_daily_production = total_production / production_days if production_days > 0 else 0
        
        summary_data.append({
            'Grade': grade,
            'Total Production (MT)': total_production,
            'Production Days': production_days,
            'Avg Daily Production (MT)': round(avg_daily_production, 1),
            'Total Stockout (MT)': total_stockout,
            'Stockout Days': len(solution['stockout'].get(grade, {}))
        })
    
    # Add totals row
    if summary_data:
        total_production = sum(item['Total Production (MT)'] for item in summary_data)
        total_days = sum(item['Production Days'] for item in summary_data)
        total_stockout = sum(item['Total Stockout (MT)'] for item in summary_data)
        total_stockout_days = sum(item['Stockout Days'] for item in summary_data)
        
        summary_data.append({
            'Grade': 'Total',
            'Total Production (MT)': total_production,
            'Production Days': total_days,
            'Avg Daily Production (MT)': round(total_production / total_days, 1) if total_days > 0 else 0,
            'Total Stockout (MT)': total_stockout,
            'Stockout Days': total_stockout_days
        })
    
    return pd.DataFrame(summary_data)


def create_line_utilization_chart(solution, lines, capacities, num_days, buffer_days=0):
    """Create a line utilization chart"""
    
    utilization_data = []
    
    for line in lines:
        # Calculate available production days (excluding shutdown and buffer days)
        available_days = num_days - buffer_days
        total_capacity = capacities[line] * available_days
        
        # Calculate actual production
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
    
    df = pd.DataFrame(utilization_data)
    
    # Create bar chart
    fig = px.bar(
        df,
        x='Line',
        y='Utilization (%)',
        title='Line Utilization Rates',
        color='Utilization (%)',
        color_continuous_scale='Viridis',
        text='Utilization (%)'
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    
    fig.update_layout(
        yaxis_title="Utilization (%)",
        xaxis_title="Production Line",
        showlegend=False,
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig, df


def create_transition_analysis(solution, lines):
    """Create transition analysis by line"""
    
    transition_data = []
    for line, count in solution['transitions']['per_line'].items():
        transition_data.append({
            'Line': line,
            'Transitions': count
        })
    
    df = pd.DataFrame(transition_data)
    
    # Create bar chart
    fig = px.bar(
        df,
        x='Line',
        y='Transitions',
        title='Production Transitions by Line',
        color='Transitions',
        color_continuous_scale='Reds',
        text='Transitions'
    )
    
    fig.update_traces(
        textposition='outside'
    )
    
    fig.update_layout(
        yaxis_title="Number of Transitions",
        xaxis_title="Production Line",
        showlegend=False,
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig, df


def create_stockout_analysis(solution, grades):
    """Create stockout analysis by grade"""
    
    stockout_data = []
    for grade in grades:
        total_stockout = sum(solution['stockout'][grade].values()) if grade in solution['stockout'] else 0
        stockout_days = len(solution['stockout'].get(grade, {}))
        
        stockout_data.append({
            'Grade': grade,
            'Total Stockout (MT)': total_stockout,
            'Stockout Days': stockout_days
        })
    
    df = pd.DataFrame(stockout_data)
    
    # Create bar chart
    fig = px.bar(
        df,
        x='Grade',
        y='Total Stockout (MT)',
        title='Stockout Analysis by Grade',
        color='Total Stockout (MT)',
        color_continuous_scale='Oranges',
        text='Total Stockout (MT)'
    )
    
    fig.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside'
    )
    
    fig.update_layout(
        yaxis_title="Stockout Quantity (MT)",
        xaxis_title="Grade",
        showlegend=False,
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig, df
