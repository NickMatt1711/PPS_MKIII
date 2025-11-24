"""
Post-processing and visualization of optimization results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
from typing import Dict, List
from constants import CHART_COLORS, SS_GRADE_COLORS


def get_or_create_grade_colors(grades: List[str]) -> Dict[str, str]:
    """Get or create consistent color mapping for grades"""
    if SS_GRADE_COLORS not in st.session_state:
        sorted_grades = sorted(grades)
        st.session_state[SS_GRADE_COLORS] = {
            grade: CHART_COLORS[i % len(CHART_COLORS)] 
            for i, grade in enumerate(sorted_grades)
        }
    return st.session_state[SS_GRADE_COLORS]


def create_production_summary(solution: Dict, grades: List[str], lines: List[str], solver) -> pd.DataFrame:
    """Create production summary DataFrame"""
    
    from ortools.sat.python import cp_model
    
    production_totals = {}
    grade_totals = {}
    plant_totals = {line: 0 for line in lines}
    stockout_totals = {}
    
    # Get actual production data from solution
    for grade in grades:
        production_totals[grade] = {line: 0 for line in lines}
        grade_totals[grade] = 0
        stockout_totals[grade] = 0
        
        # Sum production per line from solution variables
        for line in lines:
            prod_key = f'production_{grade}_{line}'
            # Check if this grade-line combination exists in production
            if 'production' in solution and grade in solution['production']:
                for date, prod_val in solution['production'][grade].items():
                    # This is aggregated already, we need the original per-line data
                    pass
        
        # Calculate from solution structure
        for line in lines:
            line_prod = 0
            if 'is_producing' in solution and line in solution['is_producing']:
                for date, prod_grade in solution['is_producing'][line].items():
                    if prod_grade == grade:
                        # Assume full capacity production (will be replaced with actual values)
                        line_prod += 1  # Placeholder
            production_totals[grade][line] = line_prod
            grade_totals[grade] += line_prod
            plant_totals[line] += line_prod
        
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
    """Create Gantt chart for a production line - matching old logic design"""
    
    gantt_data = []
    for date_str, grade in solution['is_producing'][line].items():
        if grade:
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
    sorted_grades = sorted(gantt_df['Grade'].unique())
    
    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Grade",
        color="Grade",
        color_discrete_map=grade_colors,
        category_orders={"Grade": sorted_grades},
        title=f"Production Schedule - {line}"
    )
    
    # Add shutdown period visualization (matching old logic)
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
                annotation_text="Shutdown",
                annotation_position="top left",
                annotation_font_size=14,
                annotation_font_color="red"
            )
    
    # Match old logic layout exactly
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
        tickvals=dates,
        tickformat="%d-%b",
        dtick="D1"
    )
    
    fig.update_layout(
        height=350,
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
            bgcolor="rgba(255,255,255,0)",
            bordercolor="lightgray",
            borderwidth=0
        ),
        xaxis=dict(showline=True, showticklabels=True),
        yaxis=dict(showline=True),
        margin=dict(l=60, r=160, t=60, b=60),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
    )
    
    return fig


def create_schedule_table(solution: Dict, line: str, dates: List, grade_colors: Dict) -> pd.DataFrame:
    """Create production schedule table for a line with colored grades"""
    
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
    
    if not schedule_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(schedule_data)
    
    # Apply color styling
    def color_grade(row):
        grade = row['Grade']
        if grade in grade_colors:
            color = grade_colors[grade]
            return [f'background-color: {color}; color: white; font-weight: bold; text-align: center;'] + [''] * (len(row) - 1)
        return [''] * len(row)
    
    return df


def create_inventory_chart(solution: Dict, grade: str, dates: List, 
                           min_inventory: float, max_inventory: float,
                           allowed_lines: List[str], shutdown_periods: Dict,
                           grade_colors: Dict, initial_inventory: float) -> go.Figure:
    """Create inventory level chart for a grade"""
    
    # Build inventory values including opening inventory
    inventory_dates = [dates[0]] + dates  # Add day before for opening
    inventory_values = [initial_inventory]  # Start with opening inventory
    
    for date in dates:
        date_str = date.strftime('%d-%b-%y')
        inv = solution['inventory'][grade].get(date_str, 0)
        inventory_values.append(inv)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=inventory_dates,
        y=inventory_values,
        mode="lines+markers",
        name=grade,
        line=dict(color=grade_colors.get(grade, CHART_COLORS[0]), width=3),
        marker=dict(size=6),
        hovertemplate="Date: %{x|%d-%b-%y}<br>Inventory: %{y:.0f} MT<extra></extra>"
    ))
    
    # Add shutdown periods for allowed plants
    for line in allowed_lines:
        if line in shutdown_periods and shutdown_periods[line]:
            shutdown_days = shutdown_periods[line]
            if shutdown_days:
                start_shutdown = dates[shutdown_days[0]]
                end_shutdown = dates[shutdown_days[-1]]
                
                fig.add_vrect(
                    x0=start_shutdown,
                    x1=end_shutdown + timedelta(days=1),
                    fillcolor="red",
                    opacity=0.1,
                    layer="below",
                    line_width=0,
                    annotation_text=f"Shutdown: {line}",
                    annotation_position="top left",
                    annotation_font_size=10,
                    annotation_font_color="red"
                )
    
    # Add min/max lines
    fig.add_hline(
        y=min_inventory,
        line=dict(color="red", width=2, dash="dash"),
        annotation_text=f"Min: {min_inventory:,.0f}",
        annotation_position="top left",
        annotation_font_color="red"
    )
    fig.add_hline(
        y=max_inventory,
        line=dict(color="green", width=2, dash="dash"),
        annotation_text=f"Max: {max_inventory:,.0f}",
        annotation_position="bottom left",
        annotation_font_color="green"
    )
    
    # Add key point annotations
    if len(inventory_values) > 1:
        start_val = inventory_values[0]
        end_val = inventory_values[-1]
        highest_val = max(inventory_values)
        lowest_val = min(inventory_values)
        
        start_x = inventory_dates[0]
        end_x = inventory_dates[-1]
        highest_x = inventory_dates[inventory_values.index(highest_val)]
        lowest_x = inventory_dates[inventory_values.index(lowest_val)]
        
        annotations = [
            dict(
                x=start_x, y=start_val,
                text=f"Opening: {start_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=-40, ay=30,
                font=dict(color="black", size=11),
                bgcolor="white", bordercolor="gray",
                borderwidth=1, borderpad=4, opacity=0.9
            ),
            dict(
                x=end_x, y=end_val,
                text=f"Closing: {end_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=40, ay=30,
                font=dict(color="black", size=11),
                bgcolor="white", bordercolor="gray",
                borderwidth=1, borderpad=4, opacity=0.9
            ),
            dict(
                x=highest_x, y=highest_val,
                text=f"Peak: {highest_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=0, ay=-40,
                font=dict(color="darkgreen", size=11),
                bgcolor="white", bordercolor="gray",
                borderwidth=1, borderpad=4, opacity=0.9
            ),
            dict(
                x=lowest_x, y=lowest_val,
                text=f"Trough: {lowest_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=0, ay=40,
                font=dict(color="firebrick", size=11),
                bgcolor="white", bordercolor="gray",
                borderwidth=1, borderpad=4, opacity=0.9
            )
        ]
        
        for ann in annotations:
            fig.add_annotation(**ann)
    
    fig.update_layout(
        title=f"Inventory Level - {grade}",
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor="lightgray",
            tickformat="%d-%b"
        ),
        yaxis=dict(
            title="Inventory Volume (MT)",
            showgrid=True,
            gridcolor="lightgray"
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=420,
        showlegend=False,
        margin=dict(l=60, r=80, t=80, b=60)
    )
    
    return fig
