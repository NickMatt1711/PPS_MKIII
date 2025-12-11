"""
Postprocessing utilities for solution visualization (FINAL REFACTORED VERSION)
Fully aligned with Option A visuals + compatibility wrapper + robust fallbacks.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
import streamlit as st


# ===============================================================
#  UTILITY HELPERS
# ===============================================================

def _ensure_date(d: Any) -> date:
    """Ensure value is a date object."""
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    try:
        return datetime.strptime(str(d), "%d-%b-%y").date()
    except Exception:
        return datetime.strptime(str(d), "%Y-%m-%d").date()


# ===============================================================
#  COLOR MAPPING (NEW SYSTEM)
# ===============================================================

def build_grade_color_map(grades: List[str]) -> Dict[str, str]:
    """Consistent grade color mapping using qualitative palette."""
    base_colors = px.colors.qualitative.Vivid
    return {grade: base_colors[i % len(base_colors)] for i, grade in enumerate(sorted(grades))}


# ===============================================================
#  COMPATIBILITY WRAPPER (FOR app.py)
# ===============================================================

def get_or_create_grade_colors(grades):
    return build_grade_color_map(grades)


# ===============================================================
#  GANTT CHART (OPTION A – GRADE ON Y-AXIS)
# ===============================================================

def create_gantt_chart(
    solution: Dict,
    line: str,
    dates: List[date],
    shutdown_periods: Dict,
    grade_colors: Dict
):

    dates = [_ensure_date(d) for d in dates]

    schedule = solution.get("is_producing", {}).get(line, {})

    gantt_rows = []

    for d in range(len(dates)):
        ds = dates[d].strftime("%d-%b-%y")

        for grade in grade_colors:
            if schedule.get(ds) == grade:
                gantt_rows.append({
                    "Grade": grade,
                    "Start": dates[d],
                    "Finish": dates[d] + timedelta(days=1),
                    "Line": line
                })

    if not gantt_rows:
        return None

    df = pd.DataFrame(gantt_rows)

    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Grade",
        color="Grade",
        color_discrete_map=grade_colors,
        category_orders={"Grade": sorted(grade_colors.keys())},
    )

    # Shutdown shading
    if line in shutdown_periods and shutdown_periods[line]:
        sd = shutdown_periods[line]
        x0 = dates[sd[0]]
        x1 = dates[sd[-1]] + timedelta(days=1)

        fig.add_vrect(
            x0=x0,
            x1=x1,
            fillcolor="red",
            opacity=0.12,
            layer="below",
            line_width=0,
            annotation_text="Shutdown",
            annotation_position="top left",
            annotation_font_color="red"
        )

    fig.update_yaxes(
        autorange="reversed",
        showgrid=True,
        gridcolor="lightgray"
    )
    fig.update_xaxes(
        tickformat="%d-%b",
        dtick="D1",
        showgrid=True,
        gridcolor="lightgray"
    )

    fig.update_layout(
        height=350,
        bargap=0.2,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=80, r=160, t=60, b=60),
        font=dict(size=12),
        showlegend=True,
        legend_title_text="Grade",
        legend=dict(
            traceorder="normal",
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0)"
        )
    )
    
    return fig


# ===============================================================
#  INVENTORY CHART
# ===============================================================

def create_inventory_chart(
    solution: Dict,
    grade: str,
    dates: List[date],
    min_inv: float,
    max_inv: float,
    allowed_lines: Any,
    shutdown_periods: Dict,
    grade_colors: Dict,
    initial_inv: float,
    buffer_days: int
):
    dates = [_ensure_date(d) for d in dates]

    inv_dict = solution.get("inventory", {}).get(grade, {})
    inv_vals = [inv_dict.get(d.strftime("%d-%b-%y"), 0) for d in dates]

    # Determine last actual planning day (before buffer)
    last_actual_day = len(dates) - buffer_days

    start_val = inv_vals[0]
    end_val = inv_vals[last_actual_day]
    highest_val = max(inv_vals[:last_actual_day + 1])
    lowest_val = min(inv_vals[:last_actual_day + 1])

    start_x = dates[0]
    end_x = dates[last_actual_day]
    highest_x = dates[inv_vals.index(highest_val)]
    lowest_x = dates[inv_vals.index(lowest_val)]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=inv_vals,
        mode="lines+markers",
        name=grade,
        line=dict(color=grade_colors.get(grade, "#5E7CE2"), width=3),
        marker=dict(size=6),
        hovertemplate="Date: %{x|%d-%b-%y}<br>Inventory: %{y:.0f} MT<extra></extra>"
    ))

    # Handle allowed_lines (dict or list)
    if isinstance(allowed_lines, dict):
        lines_for_grade = allowed_lines.get(grade, [])
    else:
        lines_for_grade = allowed_lines

    # Shutdown shading
    shutdown_added = False
    for line in lines_for_grade:
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
                line_width=0,
                annotation_text=f"Shutdown: {line}" if not shutdown_added else "",
                annotation_position="top left",
                annotation_font_size=14,
                annotation_font_color="red"
            )
            shutdown_added = True

    # Min/Max lines
    if min_inv is not None:
        fig.add_hline(
            y=min_inv,
            line=dict(color="red", width=2, dash="dash"),
            annotation_text=f"Min: {min_inv:,.0f}",
            annotation_position="top left",
            annotation_font_color="red"
        )

    if max_inv is not None:
        fig.add_hline(
            y=max_inv,
            line=dict(color="green", width=2, dash="dash"),
            annotation_text=f"Max: {max_inv:,.0f}",
            annotation_position="bottom left",
            annotation_font_color="green"
        )

    # Annotations
    annotations = [
        dict(
            x=start_x, y=start_val,
            text=f"Start: {start_val:.0f}",
            showarrow=True, arrowhead=2,
            ax=-40, ay=30,
            font=dict(color="black", size=11),
            bgcolor="white", bordercolor="gray"
        ),
        dict(
            x=end_x, y=end_val,
            text=f"End: {end_val:.0f}",
            showarrow=True, arrowhead=2,
            ax=40, ay=30,
            font=dict(color="black", size=11),
            bgcolor="white", bordercolor="gray"
        ),
        dict(
            x=highest_x, y=highest_val,
            text=f"High: {highest_val:.0f}",
            showarrow=True, arrowhead=2,
            ax=0, ay=-40,
            font=dict(color="darkgreen", size=11),
            bgcolor="white", bordercolor="gray"
        ),
        dict(
            x=lowest_x, y=lowest_val,
            text=f"Low: {lowest_val:.0f}",
            showarrow=True, arrowhead=2,
            ax=0, ay=40,
            font=dict(color="firebrick", size=11),
            bgcolor="white", bordercolor="gray"
        )
    ]

    fig.update_layout(
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor="lightgray",
            tickvals=dates,
            tickformat="%d-%b",
            dtick="D1"
        ),
        yaxis=dict(
            title="Inventory Volume (MT)",
            showgrid=True,
            gridcolor="lightgray"
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=80, t=80, b=60),
        font=dict(size=12),
        height=420,
        showlegend=False
    )
    
    # Add annotations one by one
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
            borderwidth=1,
            borderpad=4,
            opacity=0.9
        )

    return fig


# ===============================================================
#  SCHEDULE TABLE
# ===============================================================

def create_schedule_table(
    solution: Dict,
    line: str,
    dates: List[date],
    grade_colors: Dict,
    shutdown_periods: Dict = None  # ADD THIS PARAMETER
):
    """Tabular schedule structure for Streamlit."""
    dates = [_ensure_date(d) for d in dates]
    schedule = solution.get("is_producing", {}).get(line, {})
    
    # Get shutdown days for this line
    shutdown_days = []
    if shutdown_periods and line in shutdown_periods:
        shutdown_days = shutdown_periods[line]

    rows = []
    current_grade = None
    start_idx = None

    for i, d in enumerate(dates):
        ds = d.strftime("%d-%b-%y")
        
        # Check if this is a shutdown day
        if i in shutdown_days:
            grade_today = "SHUTDOWN"
        else:
            grade_today = schedule.get(ds)

        if grade_today != current_grade:
            if current_grade is not None:
                end_date = dates[i - 1]
                rows.append({
                    "Grade": current_grade,
                    "Start Date": dates[start_idx].strftime("%d-%b-%y"),
                    "End Date": end_date.strftime("%d-%b-%y"),
                    "Days": (end_date - dates[start_idx]).days + 1
                })
            current_grade = grade_today
            start_idx = i

    if current_grade is not None:
        end_date = dates[-1]
        rows.append({
            "Grade": current_grade,
            "Start Date": dates[start_idx].strftime("%d-%b-%y"),
            "End Date": end_date.strftime("%d-%b-%y"),
            "Days": (end_date - dates[start_idx]).days + 1
        })

    return pd.DataFrame(rows)


# ===============================================================
#  PRODUCTION SUMMARY
# ===============================================================

def create_production_summary(solution, production_vars, solver, grades, lines, num_days, buffer_days=0):
    """Builds production summary table."""
    rows = []

    for grade in sorted(grades):
        row = {"Grade": grade}
        total = 0

        for line in lines:
            val = 0
            for d in range(num_days):
                key = (grade, line, d)
                if key in production_vars:
                    try:
                        val += solver.Value(production_vars[key])
                    except:
                        pass
            row[line] = int(val)
            total += val

        row["Total Produced"] = int(total)
        stockout_dict = solution.get('stockout', {}).get(grade, {})
        total_stockout = sum(stockout_dict.values()) if stockout_dict else 0
        row["Total Stockout"] = int(total_stockout)
        rows.append(row)

    # Total row
    total_row = {"Grade": "Total"}
    for line in lines:
        total_row[line] = sum(r[line] for r in rows)
    total_row["Total Produced"] = sum(r["Total Produced"] for r in rows)
    total_row["Total Stockout"] = sum(r["Total Stockout"] for r in rows)

    rows.append(total_row)
    return pd.DataFrame(rows)


# ===============================================================
#  STOCKOUT DETAILS TABLE (MISSING FUNCTION)
# ===============================================================

def create_stockout_details_table(solution: Dict, grades: List[str], dates: List[date], buffer_days: int = 0):
    """Create detailed stockout summary table by grade."""
    rows = []
    
    # Only analyze actual planning days (exclude buffer)
    actual_days = len(dates) - buffer_days
    
    for grade in sorted(grades):
        stockout_dict = solution.get('stockout', {}).get(grade, {})
        
        # Sum stockouts only for actual planning days
        total_stockout = 0
        stockout_days = 0
        
        for d_idx in range(actual_days):
            date_str = dates[d_idx].strftime("%d-%b-%y")
            stockout_val = stockout_dict.get(date_str, 0)
            if stockout_val > 0:
                total_stockout += stockout_val
                stockout_days += 1
        
        if total_stockout > 0:  # Only include grades with stockouts
            rows.append({
                "Grade": grade,
                "Total Stockout (MT)": int(total_stockout),
                "Days with Stockout": stockout_days
            })
    
    if not rows:
        # Return empty dataframe with correct structure if no stockouts
        return pd.DataFrame(columns=["Grade", "Total Stockout (MT)", "Days with Stockout"])
    
    return pd.DataFrame(rows)
