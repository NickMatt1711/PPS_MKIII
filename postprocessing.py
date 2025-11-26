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
    """Compatibility wrapper so existing app.py continues to work."""
    return build_grade_color_map(grades)


# ===============================================================
#  GANTT CHART (OPTION A — GRADE ON Y-AXIS)
# ===============================================================

def create_gantt_chart(
    solution: Dict,
    line: str,
    dates: List[date],
    shutdown_periods: Dict,
    grade_colors: Dict
):
    """
    Creates a Plotly Express timeline chart matching Option A visuals:
    - Y-axis: Grade
    - Color by Grade
    - Shutdown shading using vrect
    """
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
        gridcolor="#B0B0B0",
        tickfont=dict(color="#222222", size=12)
    )
    fig.update_xaxes(
        tickformat="%d-%b",
        dtick="D1",
        showgrid=True,
        gridcolor="#B0B0B0",
        tickfont=dict(color="#222222", size=12)
    )

    fig.update_layout(
        height=350,
        bargap=0.2,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=80, r=160, t=60, b=60),
        font=dict(size=12, color="#222222")
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
            tickfont=dict(color="#333333", size=12),
            dtick="D1"
        ),
        yaxis=dict(
            title="Inventory Volume (MT)",
            showgrid=True,
            tickfont=dict(color="#333333", size=12),
            gridcolor="lightgray"
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=80, t=80, b=60),
        font=dict(size=12, color="#222222"),
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
    grade_colors: Dict
):
    """Tabular schedule structure for Streamlit."""
    dates = [_ensure_date(d) for d in dates]
    schedule = solution.get("is_producing", {}).get(line, {})

    rows = []
    current_grade = None
    start_idx = None

    for i, d in enumerate(dates):
        ds = d.strftime("%d-%b-%y")
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

def create_production_summary(solution, production_vars, solver, grades, lines, num_days):
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
        rows.append(row)

    # Total row
    total_row = {"Grade": "Total"}
    for line in lines:
        total_row[line] = sum(r[line] for r in rows)
    total_row["Total Produced"] = sum(r["Total Produced"] for r in rows)

    rows.append(total_row)
    return pd.DataFrame(rows)
