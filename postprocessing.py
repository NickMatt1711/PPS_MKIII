"""
Postprocessing utilities for solution visualization (FINAL VERSION)
Fully aligned with Option A visuals + compatibility wrapper.
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
    return datetime.strptime(str(d), "%d-%b-%y").date()


# ===============================================================
#  COLOR MAPPING (NEW SYSTEM)
# ===============================================================

def build_grade_color_map(grades: List[str]) -> Dict[str, str]:
    """
    Consistent grade color mapping using px qualitative palette.
    """
    base_colors = px.colors.qualitative.Vivid
    return {grade: base_colors[i % len(base_colors)] for i, grade in enumerate(sorted(grades))}


# ===============================================================
#  COMPATIBILITY WRAPPER (FOR app.py)
# ===============================================================

def get_or_create_grade_colors(grades):
    """
    Compatibility wrapper so existing app.py continues to work.
    Maps old function name to new color-map builder.
    """
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

        for grade in grade_colors.keys():
            if (grade in schedule and schedule[grade] == ds) or \
               (schedule.get(ds) == grade):
                gantt_rows.append({
                    "Grade": grade,
                    "Start": dates[d],
                    "Finish": dates[d] + timedelta(days=1),
                    "Line": line
                })

    # If nothing to plot
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
        title=f"Production Schedule - {line}"
    )

    # Shutdown shading
    if line in shutdown_periods and shutdown_periods[line]:
        d_list = shutdown_periods[line]
        start_sd = dates[d_list[0]]
        end_sd = dates[d_list[-1]] + timedelta(days=1)

        fig.add_vrect(
            x0=start_sd,
            x1=end_sd,
            fillcolor="red",
            opacity=0.15,
            layer="below",
            line_width=0,
            annotation_text="Shutdown",
            annotation_position="top left",
            annotation_font_color="red"
        )

    fig.update_yaxes(
        autorange="reversed",
        title=None,
        showgrid=True,
        gridcolor="lightgray"
    )

    fig.update_xaxes(
        title="Date",
        tickformat="%d-%b",
        showgrid=True,
        gridcolor="lightgray",
        dtick="D1"
    )

    fig.update_layout(
        height=350,
        bargap=0.2,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=80, r=150, t=50, b=60),
        font=dict(size=12),
        legend_title_text="Grade"
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
    allowed_lines: Dict[str, List[str]],
    shutdown_periods: Dict,
    grade_colors: Dict,
    initial_inv: float,
    buffer_days: int
):
    """
    Inventory chart matching your UI style:
    - timeline on X
    - annotations: start, end, high, low
    - shutdown vrect
    - min/max lines
    """
    dates = [_ensure_date(d) for d in dates]

    inventory_dict = solution.get("inventory", {}).get(grade, {})

    inv_vals = [inventory_dict.get(d.strftime("%d-%b-%y"), 0) for d in dates]

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

    # Shutdown shading
    lines_for_grade = allowed_lines.get(grade, [])

    shaded_once = False
    for line in lines_for_grade:
        if line in shutdown_periods and shutdown_periods[line]:
            sd = shutdown_periods[line]
            x0 = dates[sd[0]]
            x1 = dates[sd[-1]] + timedelta(days=1)

            fig.add_vrect(
                x0=x0,
                x1=x1,
                fillcolor="red",
                opacity=0.1,
                layer="below",
                line_width=0,
                annotation_text=f"Shutdown: {line}" if not shaded_once else "",
                annotation_font_color="red",
                annotation_position="top left"
            )
            shaded_once = True

    # Min/Max Lines
    if min_inv is not None:
        fig.add_hline(
            y=min_inv,
            line=dict(color="red", dash="dash"),
            annotation_text=f"Min {min_inv:.0f}",
            annotation_position="top left"
        )
    if max_inv is not None:
        fig.add_hline(
            y=max_inv,
            line=dict(color="green", dash="dash"),
            annotation_text=f"Max {max_inv:.0f}",
            annotation_position="bottom left"
        )

    # Calculate annotations
    values = inv_vals
    start_val = values[0]
    end_val = values[-1]
    high_val = max(values)
    low_val = min(values)

    start_x = dates[0]
    end_x = dates[-1]
    high_x = dates[values.index(high_val)]
    low_x = dates[values.index(low_val)]

    # Add annotations
    for x, y, text, ax, ay in [
        (start_x, start_val, f"Start: {start_val:.0f}", -40, 30),
        (end_x, end_val, f"End: {end_val:.0f}", 40, 30),
        (high_x, high_val, f"High: {high_val:.0f}", 0, -40),
        (low_x, low_val, f"Low: {low_val:.0f}", 0, 40),
    ]:
        fig.add_annotation(
            x=x, y=y,
            text=text,
            showarrow=True, arrowhead=2,
            ax=ax, ay=ay,
            bgcolor="white", bordercolor="gray",
            opacity=0.9
        )

    fig.update_layout(
        title=f"Inventory Level - {grade}",
        xaxis=dict(
            title="Date",
            showgrid=True,
            tickformat="%d-%b",
            dtick="D1",
            gridcolor="lightgray"
        ),
        yaxis=dict(
            title="Inventory (MT)",
            showgrid=True,
            gridcolor="lightgray"
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=80, t=80, b=60),
        font=dict(size=12),
        showlegend=False,
        height=420
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
    """
    Generates a dataframe showing:
    Grade | Start Date | End Date | Days
    Exactly matching your tabular UI logic.
    """
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
    """
    Generates production summary table:
    Grade | Line1 | Line2 | ... | Total Produced
    """
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
                    except Exception:
                        pass
            row[line] = int(val)
            total += val

        row["Total Produced"] = int(total)
        rows.append(row)

    # Total Row
    total_row = {"Grade": "Total"}
    for line in lines:
        total_row[line] = sum(r[line] for r in rows)
    total_row["Total Produced"] = sum(r["Total Produced"] for r in rows)

    rows.append(total_row)
    return pd.DataFrame(rows)
