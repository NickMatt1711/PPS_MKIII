"""
Postprocessing utilities for solution visualization (fixed)
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any
import streamlit as st
from constants import CHART_COLORS
from datetime import datetime, date


def get_or_create_grade_colors(grades: List[str]) -> Dict[str, str]:
    """Get or create consistent colors for grades"""
    if 'grade_colors' not in st.session_state:
        st.session_state['grade_colors'] = {}

    grade_colors = st.session_state['grade_colors']

    for i, grade in enumerate(sorted(grades)):
        if grade not in grade_colors:
            grade_colors[grade] = CHART_COLORS[i % len(CHART_COLORS)]

    st.session_state['grade_colors'] = grade_colors
    return grade_colors


def _ensure_date(dt: Any) -> date:
    """Convert a datetime/date-like object to a date."""
    if isinstance(dt, datetime):
        return dt.date()
    if isinstance(dt, date):
        return dt
    # fallback: parse dd-MMM-yy
    return datetime.strptime(str(dt), "%d-%b-%y").date()


def create_gantt_chart(solution: Dict, line: str, dates: List[date],
                       shutdown_periods: Dict, grade_colors: Dict):
    """
    Create JSON-safe Gantt chart.
    """

    # Normalize dates
    dates = [_ensure_date(d) for d in dates]

    tasks = []
    current_grade = None
    start_idx = None

    schedule = solution.get('is_producing', {}).get(line, {})

    for i, d in enumerate(dates):
        ds = d.strftime('%d-%b-%y')
        grade = schedule.get(ds)

        is_shutdown = line in shutdown_periods and i in shutdown_periods[line]

        if is_shutdown:
            if current_grade is not None:
                tasks.append({
                    "Task": line,
                    "Start": dates[start_idx],
                    "Finish": dates[i - 1],
                    "Resource": current_grade,
                    "Color": grade_colors.get(current_grade, "#999999")
                })
                current_grade = None
                start_idx = None
            continue

        if grade != current_grade:
            if current_grade is not None:
                tasks.append({
                    "Task": line,
                    "Start": dates[start_idx],
                    "Finish": dates[i - 1],
                    "Resource": current_grade,
                    "Color": grade_colors.get(current_grade, "#999999")
                })
            current_grade = grade
            start_idx = i

    # final task
    if current_grade is not None and start_idx is not None:
        tasks.append({
            "Task": line,
            "Start": dates[start_idx],
            "Finish": dates[-1],
            "Resource": current_grade,
            "Color": grade_colors.get(current_grade, "#999999")
        })

    fig = go.Figure()

    for t in tasks:
        start = _ensure_date(t["Start"])
        finish = _ensure_date(t["Finish"])

        duration = (finish - start).days + 1
        start_str = start.strftime("%Y-%m-%d")
        hover_s = start.strftime("%d-%b-%y")
        hover_e = finish.strftime("%d-%b-%y")

        fig.add_trace(go.Bar(
            x=[duration],
            y=[t["Task"]],
            orientation="h",
            name=str(t["Resource"]),
            marker=dict(color=t["Color"]),
            base=[start_str],
            hovertemplate=f"<b>{t['Resource']}</b><br>Start: {hover_s}<br>End: {hover_e}<extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        title=f"Production Schedule - {line}",
        xaxis_title="Days",
        yaxis_title="",
        height=max(220, 40 * (len(tasks) or 1)),
        margin=dict(l=150, r=20, t=50, b=40),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def create_inventory_chart(solution: Dict, grade: str, dates: List[date],
                           min_inv: float, max_inv: float,
                           allowed_lines: List[str], shutdown_periods: Dict,
                           grade_colors: Dict, initial_inv: float, buffer_days: int):
    """
    Inventory chart (fix: ensure JSON-safe x and y values)
    """

    dates = [_ensure_date(d) for d in dates]
    ds_list = [d.strftime("%d-%b-%y") for d in dates]

    inventory = solution.get("inventory", {}).get(grade, {})

    inv_values = [initial_inv] + [inventory.get(ds, 0) for ds in ds_list]
    plot_dates = ["Initial"] + ds_list

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_dates,
        y=inv_values,
        mode="lines+markers",
        name="Inventory",
        line=dict(color=grade_colors.get(grade, "#5E7CE2"), width=3),
        marker=dict(size=6)
    ))

    if min_inv is not None:
        fig.add_trace(go.Scatter(
            x=plot_dates,
            y=[min_inv] * len(plot_dates),
            mode="lines",
            name="Min Inventory",
            line=dict(color="red", dash="dash", width=2)
        ))

    if max_inv is not None:
        fig.add_trace(go.Scatter(
            x=plot_dates,
            y=[max_inv] * len(plot_dates),
            mode="lines",
            name="Max Inventory",
            line=dict(color="orange", dash="dash", width=2)
        ))

    fig.update_layout(
        title=f"Inventory Profile - {grade}",
        xaxis_title="Date",
        yaxis_title="Inventory (MT)",
        hovermode="x unified",
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def create_schedule_table(solution: Dict, line: str, dates: List[date],
                          grade_colors: Dict) -> pd.DataFrame:
    """
    Tabular interpretation of schedule (fixed)
    """

    dates = [_ensure_date(d) for d in dates]
    schedule = solution.get("is_producing", {}).get(line, {})

    rows = []
    current_grade = None
    start_idx = None
    run_days = 0

    for i, d in enumerate(dates):
        ds = d.strftime("%d-%b-%y")
        grade = schedule.get(ds)

        if grade != current_grade:
            if current_grade is not None and start_idx is not None:
                rows.append({
                    "Grade": current_grade,
                    "Start Date": dates[start_idx].strftime("%d-%b-%y"),
                    "End Date": dates[i - 1].strftime("%d-%b-%y"),
                    "Run Days": run_days
                })
            current_grade = grade
            start_idx = i
            run_days = 1
        else:
            run_days += 1

    if current_grade is not None:
        rows.append({
            "Grade": current_grade,
            "Start Date": dates[start_idx].strftime("%d-%b-%y"),
            "End Date": dates[-1].strftime("%d-%b-%y"),
            "Run Days": run_days
        })

    return pd.DataFrame(rows)


def create_production_summary(solution: Dict, production_vars: Dict,
                              solver, grades: List[str], lines: List[str],
                              num_days: int) -> pd.DataFrame:
    """
    Production summary (robust to CP-SAT Value() calls)
    """

    rows = []

    for grade in sorted(grades):
        total_prod = 0

        for line in lines:
            for d in range(num_days):
                key = (grade, line, d)
                if key in production_vars:
                    try:
                        val = solver.Value(production_vars[key])
                        total_prod += float(val)
                    except Exception:
                        try:
                            total_prod += float(production_vars[key])
                        except:
                            pass

        if total_prod > 0:
            rows.append({
                "Grade": grade,
                "Total Production (MT)": int(round(total_prod))
            })

    total = sum(r["Total Production (MT)"] for r in rows)

    rows.append({
        "Grade": "Total",
        "Total Production (MT)": int(round(total))
    })

    return pd.DataFrame(rows)
