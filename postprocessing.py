"""
Postprocessing utilities for solution visualization
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import streamlit as st
from constants import CHART_COLORS


def get_or_create_grade_colors(grades: List[str]) -> Dict[str, str]:
    """Get or create consistent colors for grades"""
    if 'grade_colors' not in st.session_state:
        st.session_state['grade_colors'] = {}
    
    grade_colors = st.session_state['grade_colors']
    
    # Assign colors to new grades
    for i, grade in enumerate(sorted(grades)):
        if grade not in grade_colors:
            grade_colors[grade] = CHART_COLORS[i % len(CHART_COLORS)]
    
    st.session_state['grade_colors'] = grade_colors
    return grade_colors


def create_gantt_chart(solution: Dict, line: str, dates: List, shutdown_periods: Dict, grade_colors: Dict):
    """Create Gantt chart for production schedule"""
    
    # Prepare data for Gantt chart
    tasks = []
    current_grade = None
    start_date = None
    
    schedule = solution['is_producing'][line]
    
    for i, date in enumerate(dates):
        date_str = date.strftime('%d-%b-%y')
        grade = schedule.get(date_str)
        
        # Check if shutdown
        is_shutdown = line in shutdown_periods and i in shutdown_periods[line]
        
        if is_shutdown:
            if current_grade:
                tasks.append({
                    'Task': line,
                    'Start': start_date,
                    'Finish': dates[i-1],
                    'Resource': current_grade,
                    'Color': grade_colors.get(current_grade, '#999999')
                })
                current_grade = None
            continue
        
        if grade != current_grade:
            if current_grade:
                tasks.append({
                    'Task': line,
                    'Start': start_date,
                    'Finish': dates[i-1],
                    'Resource': current_grade,
                    'Color': grade_colors.get(current_grade, '#999999')
                })
            current_grade = grade
            start_date = date
    
    # Add final task
    if current_grade:
        tasks.append({
            'Task': line,
            'Start': start_date,
            'Finish': dates[-1],
            'Resource': current_grade,
            'Color': grade_colors.get(current_grade, '#999999')
        })
    
    # Create figure
    fig = go.Figure()
    
    for task in tasks:
        fig.add_trace(go.Bar(
            x=[task['Finish'] - task['Start']],
            y=[task['Task']],
            orientation='h',
            name=task['Resource'],
            marker=dict(color=task['Color']),
            base=task['Start'],
            showlegend=False,
            hovertemplate=f"<b>{task['Resource']}</b><br>Start: {task['Start'].strftime('%d-%b-%y')}<br>End: {task['Finish'].strftime('%d-%b-%y')}<extra></extra>"
        ))
    
    fig.update_layout(
        title=f"Production Schedule - {line}",
        xaxis_title="Date",
        yaxis_title="",
        height=200,
        margin=dict(l=100, r=20, t=40, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_inventory_chart(solution: Dict, grade: str, dates: List, min_inv: float, max_inv: float, 
                          allowed_lines: List, shutdown_periods: Dict, grade_colors: Dict,
                          initial_inv: float, buffer_days: int):
    """Create inventory level chart"""
    
    inventory = solution['inventory'][grade]
    date_strs = [date.strftime('%d-%b-%y') for date in dates]
    
    inv_values = [initial_inv] + [inventory.get(ds, 0) for ds in date_strs]
    plot_dates = ['Initial'] + date_strs
    
    fig = go.Figure()
    
    # Inventory line
    fig.add_trace(go.Scatter(
        x=plot_dates,
        y=inv_values,
        mode='lines+markers',
        name='Inventory',
        line=dict(color=grade_colors.get(grade, '#5E7CE2'), width=3),
        marker=dict(size=6)
    ))
    
    # Min/Max lines
    if min_inv > 0:
        fig.add_trace(go.Scatter(
            x=plot_dates,
            y=[min_inv] * len(plot_dates),
            mode='lines',
            name='Min Inventory',
            line=dict(color='red', dash='dash', width=2)
        ))
    
    if max_inv < 1000000:
        fig.add_trace(go.Scatter(
            x=plot_dates,
            y=[max_inv] * len(plot_dates),
            mode='lines',
            name='Max Inventory',
            line=dict(color='orange', dash='dash', width=2)
        ))
    
    fig.update_layout(
        title=f"Inventory Profile - {grade}",
        xaxis_title="Date",
        yaxis_title="Inventory (MT)",
        height=400,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_schedule_table(solution: Dict, line: str, dates: List, grade_colors: Dict) -> pd.DataFrame:
    """Create schedule table for a production line"""
    
    schedule = solution['is_producing'][line]
    
    rows = []
    current_grade = None
    start_date = None
    run_days = 0
    
    for date in dates:
        date_str = date.strftime('%d-%b-%y')
        grade = schedule.get(date_str)
        
        if grade != current_grade:
            if current_grade:
                rows.append({
                    'Grade': current_grade,
                    'Start Date': start_date,
                    'End Date': dates[dates.index(start_date) + run_days - 1].strftime('%d-%b-%y'),
                    'Run Days': run_days
                })
            current_grade = grade
            start_date = date_str
            run_days = 1
        else:
            run_days += 1
    
    # Add final run
    if current_grade:
        rows.append({
            'Grade': current_grade,
            'Start Date': start_date,
            'End Date': dates[-1].strftime('%d-%b-%y'),
            'Run Days': run_days
        })
    
    return pd.DataFrame(rows)


def create_production_summary(solution: Dict, production_vars: Dict, solver, grades: List, lines: List, num_days: int) -> pd.DataFrame:
    """Create production summary table"""
    
    rows = []
    
    for grade in sorted(grades):
        total_production = 0
        
        # Calculate total production for this grade
        for line in lines:
            for d in range(num_days):
                key = (grade, line, d)
                if key in production_vars:
                    try:
                        total_production += solver.Value(production_vars[key])
                    except:
                        pass
        
        if total_production > 0:
            rows.append({
                'Grade': grade,
                'Total Production (MT)': int(total_production)
            })
    
    # Add total row
    total = sum(row['Total Production (MT)'] for row in rows)
    rows.append({
        'Grade': 'Total',
        'Total Production (MT)': int(total)
    })
    
    return pd.DataFrame(rows)
