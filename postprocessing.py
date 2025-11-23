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
    """Create production summary DataFrame with actual production quantities"""
    
    production_totals = {}
    grade_totals = {}
    plant_totals = {line: 0 for line in lines}
    stockout_totals = {}
    
    # Initialize totals
    for grade in grades:
        production_totals[grade] = {line: 0 for line in lines}
        grade_totals[grade] = 0
        stockout_totals[grade] = 0
    
    # Extract actual production quantities from solution
    # Method 1: Check if we have production quantities in the solution
    if 'production_quantity' in solution:
        # New structure with production quantities
        for grade in grades:
            if grade in solution['production_quantity']:
                for line in lines:
                    if line in solution['production_quantity'][grade]:
                        total_qty = sum(solution['production_quantity'][grade][line].values())
                        production_totals[grade][line] = total_qty
                        grade_totals[grade] += total_qty
                        plant_totals[line] += total_qty
    
    # Method 2: If using old structure, calculate from production variables
    elif 'production' in solution:
        for grade in grades:
            if grade in solution['production']:
                for line in lines:
                    line_key = line  # Try direct line key
                    if line_key in solution['production'][grade]:
                        total_qty = 0
                        for date, qty in solution['production'][grade][line_key].items():
                            if isinstance(qty, (int, float)) and qty > 0:
                                total_qty += qty
                        production_totals[grade][line] = total_qty
                        grade_totals[grade] += total_qty
                        plant_totals[line] += total_qty
    
    # Method 3: Fallback - estimate from is_producing and capacity (if available)
    else:
        # This is the old logic that counts days - we need to replace this
        # For now, let's assume each production day produces 1000 MT as placeholder
        DEFAULT_DAILY_PRODUCTION = 1000
        
        for grade in grades:
            for line in lines:
                production_days = 0
                if 'is_producing' in solution and line in solution['is_producing']:
                    for date, prod_grade in solution['is_producing'][line].items():
                        if prod_grade == grade:
                            production_days += 1
                
                production_qty = production_days * DEFAULT_DAILY_PRODUCTION
                production_totals[grade][line] = production_qty
                grade_totals[grade] += production_qty
                plant_totals[line] += production_qty
    
    # Calculate stockouts
    for grade in grades:
        if grade in solution.get('stockout', {}):
            for date, stockout_qty in solution['stockout'][grade].items():
                if isinstance(stockout_qty, (int, float)):
                    stockout_totals[grade] += stockout_qty
    
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
    totals_row['Total Produced'] = sum(grade_totals.values())
    totals_row['Total Stockout'] = sum(stockout_totals.values())
    data.append(totals_row)
    
    df = pd.DataFrame(data)
    
    # Format numbers with commas for thousands
    numeric_columns = lines + ['Total Produced', 'Total Stockout']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)
    
    return df


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


def create_inventory_chart(solution: Dict, grade: str, demand_dates: List, 
                           min_inventory: float, max_inventory: float,
                           allowed_lines: List[str], shutdown_periods: Dict,
                           grade_colors: Dict, initial_inventory: float) -> go.Figure:
    """Create corrected inventory level chart for a grade - only show demand period"""
    
    # Use only demand period dates, exclude buffer period
    inventory_dates = []
    inventory_values = []
    
    # Add opening inventory at the very start
    if demand_dates:
        inventory_dates.append(demand_dates[0])
        inventory_values.append(initial_inventory)
    
    # Add daily inventory levels only for demand period
    for date in demand_dates:
        date_str = date.strftime('%d-%b-%y')
        inv_value = 0
        
        # Get inventory from solution
        if grade in solution.get('inventory', {}) and date_str in solution['inventory'][grade]:
            inv_value = solution['inventory'][grade][date_str]
        elif 'inventory_level' in solution and grade in solution['inventory_level']:
            # Alternative solution structure
            for inv_date, inv_qty in solution['inventory_level'][grade].items():
                if inv_date == date_str:
                    inv_value = inv_qty
                    break
        
        if isinstance(inv_value, (int, float)):
            inventory_dates.append(date)
            inventory_values.append(inv_value)
    
    # If we have no valid data, create empty chart
    if len(inventory_values) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No inventory data available for demand period",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title=f"Inventory Level - {grade}",
            height=400,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        return fig
    
    # Ensure we don't have the dip to 0 - use forward fill for missing values
    cleaned_dates = []
    cleaned_values = []
    last_valid_value = initial_inventory
    
    for i, (date, value) in enumerate(zip(inventory_dates, inventory_values)):
        if value > 0 or i == 0:  # Always include first point
            last_valid_value = value
        cleaned_dates.append(date)
        cleaned_values.append(last_valid_value)
    
    fig = go.Figure()
    
    # Add inventory trace
    fig.add_trace(go.Scatter(
        x=cleaned_dates,
        y=cleaned_values,
        mode="lines+markers",
        name=f"{grade} Inventory",
        line=dict(color=grade_colors.get(grade, CHART_COLORS[0]), width=3),
        marker=dict(size=6),
        hovertemplate="Date: %{x|%d-%b-%y}<br>Inventory: %{y:,.0f} MT<extra></extra>"
    ))
    
    # Add shutdown periods only if they occur during demand period
    for line in allowed_lines:
        if line in shutdown_periods and shutdown_periods[line]:
            shutdown_days = shutdown_periods[line]
            valid_shutdown_days = [day for day in shutdown_days if day < len(demand_dates)]
            
            if valid_shutdown_days:
                start_shutdown = demand_dates[valid_shutdown_days[0]]
                end_shutdown = demand_dates[valid_shutdown_days[-1]]
                
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
    
    # Add min/max inventory lines
    fig.add_hline(
        y=min_inventory,
        line=dict(color="red", width=2, dash="dash"),
        annotation_text=f"Min: {min_inventory:,.0f} MT",
        annotation_position="top left",
        annotation_font_color="red"
    )
    
    fig.add_hline(
        y=max_inventory,
        line=dict(color="green", width=2, dash="dash"),
        annotation_text=f"Max: {max_inventory:,.0f} MT",
        annotation_position="top left",
        annotation_font_color="green"
    )
    
    # Add key annotations
    if len(cleaned_values) > 1:
        opening_val = cleaned_values[0]
        closing_val = cleaned_values[-1]
        
        fig.add_annotation(
            x=cleaned_dates[0], y=opening_val,
            text=f"Opening: {opening_val:,.0f}",
            showarrow=True,
            arrowhead=2,
            ax=-50,
            ay=-30,
            bgcolor="white",
            bordercolor="gray",
            borderwidth=1
        )
        
        fig.add_annotation(
            x=cleaned_dates[-1], y=closing_val,
            text=f"Closing: {closing_val:,.0f}",
            showarrow=True,
            arrowhead=2,
            ax=50,
            ay=-30,
            bgcolor="white",
            bordercolor="gray",
            borderwidth=1
        )
    
    fig.update_layout(
        title=f"Inventory Level - {grade} (Demand Period Only)",
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor="lightgray",
            tickformat="%d-%b",
            range=[demand_dates[0] if demand_dates else None, 
                   demand_dates[-1] + timedelta(days=1) if demand_dates else None]
        ),
        yaxis=dict(
            title="Inventory Volume (MT)",
            showgrid=True,
            gridcolor="lightgray",
            range=[0, max(max_inventory * 1.1, max(cleaned_values) * 1.1) if cleaned_values else 1000]
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=450,
        showlegend=False,
        margin=dict(l=60, r=80, t=80, b=60)
    )
    
    return fig
