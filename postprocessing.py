from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Try to import matplotlib colormap as fallback for many grades
try:
    from matplotlib import cm
except Exception:
    cm = None

# Default qualitative palette
BASE_PALETTE = px.colors.qualitative.Vivid


def _dtize(d):
    """Convert input to a pandas Timestamp (safe for plotly)."""
    if isinstance(d, (pd.Timestamp, datetime)):
        return pd.to_datetime(d)
    if isinstance(d, date):
        return pd.to_datetime(datetime(d.year, d.month, d.day))
    # Try parsing string
    try:
        return pd.to_datetime(str(d))
    except Exception:
        raise ValueError(f"Unable to parse date: {d}")


def build_grade_color_map(grades: List[str]) -> Dict[str, str]:
    """
    Build a deterministic color map for grades.
    Uses px.colors.qualitative.Vivid, falls back to matplotlib 'tab20' if more colors required.
    """
    if not grades:
        return {}

    sorted_grades = list(sorted(grades))
    color_map: Dict[str, str] = {}

    # Primary palette
    n_base = len(BASE_PALETTE)
    if len(sorted_grades) <= n_base:
        for i, g in enumerate(sorted_grades):
            color_map[g] = BASE_PALETTE[i % n_base]
        return color_map

    # Fallback: try matplotlib tab20 (gives up to 20 distinct)
    if cm is not None:
        cmap = cm.get_cmap("tab20")
        for i, g in enumerate(sorted_grades):
            rgba = cmap(i % 20)
            # Convert rgba to hex
            color_map[g] = "#{:02x}{:02x}{:02x}".format(
                int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)
            )
        return color_map

    # Ultimate fallback: cycle the base palette
    for i, g in enumerate(sorted_grades):
        color_map[g] = BASE_PALETTE[i % n_base]
    return color_map


def build_production_totals(
    grades: List[str],
    lines: List[str],
    num_days: int,
    production_vars: Dict[Any, Any],
    is_producing_vars: Dict[Any, Any],
    stockout_vars: Dict[Any, Any],
    solver=None,
) -> pd.DataFrame:
    """
    Build a DataFrame with production totals per grade and per line, plus stockout totals.
    - production_vars is expected keyed by (grade, line, day) with either solver var or numeric
    - is_producing_vars keyed by (grade, line, day)
    - stockout_vars keyed by (grade, day)
    - solver may be OR-Tools solver with Value(var) method. If None, raw values are used.
    """
    def _value(v):
        if solver is not None:
            try:
                return solver.Value(v)
            except Exception:
                pass
        # fallback: assume numeric
        try:
            return float(v)
        except Exception:
            return 0.0

    # compute
    production_totals: Dict[str, Dict[str, float]] = {}
    grade_totals: Dict[str, float] = {}
    plant_totals: Dict[str, float] = {line: 0.0 for line in lines}
    stockout_totals: Dict[str, float] = {}

    for grade in grades:
        production_totals[grade] = {}
        grade_totals[grade] = 0.0
        stockout_totals[grade] = 0.0

        for line in lines:
            total_prod = 0.0
            for d in range(num_days):
                key = (grade, line, d)
                if key in production_vars:
                    total_prod += float(_value(production_vars[key]))
            production_totals[grade][line] = total_prod
            grade_totals[grade] += total_prod
            plant_totals[line] += total_prod

        # stockout per grade (over days)
        for d in range(num_days):
            key = (grade, d)
            if key in stockout_vars:
                stockout_totals[grade] += float(_value(stockout_vars[key]))

    rows = []
    for grade in grades:
        row = {"Grade": grade}
        for line in lines:
            row[line] = production_totals[grade].get(line, 0.0)
        row["Total Produced"] = grade_totals[grade]
        row["Total Stockout"] = stockout_totals.get(grade, 0.0)
        rows.append(row)

    totals_row = {"Grade": "Total"}
    for line in lines:
        totals_row[line] = plant_totals[line]
    totals_row["Total Produced"] = sum(plant_totals.values())
    totals_row["Total Stockout"] = sum(stockout_totals.values())
    rows.append(totals_row)

    return pd.DataFrame(rows)


def build_gantt_fig_for_line(
    line: str,
    dates: List[Any],
    grades: List[str],
    is_producing_vars: Dict[Any, Any],
    solver=None,
    shutdown_periods: Optional[Dict[str, List[int]]] = None,
    grade_color_map: Optional[Dict[str, str]] = None,
    title: Optional[str] = None,
) -> go.Figure:
    """
    Build a grade-on-Y-axis timeline (one chart per line).
    - dates: list of date-like (strings / datetime / pd.Timestamp). Must be in order.
    - is_producing_vars keyed by (grade, line, day) and solver.Value(var)==1 when producing.
    - shutdown_periods: { line: [day_idx,...] }
    - grade_color_map: mapping grade->hex color
    Returns a plotly.graph_objects Figure.
    """

    # Normalize dates to pandas datetime for plotly express
    dates_pd = [pd.to_datetime(d) for d in dates]
    num_days = len(dates_pd)
    sorted_grades = sorted(grades)
    grade_color_map = grade_color_map or build_grade_color_map(sorted_grades)
    shutdown_periods = shutdown_periods or {}

    # Build gantt_data list in the px.timeline format: each entry has Start, Finish, Grade
    gantt_data = []
    for d_idx in range(num_days):
        day_dt = dates_pd[d_idx]
        for grade in sorted_grades:
            key = (grade, line, d_idx)
            producing = False
            if key in is_producing_vars:
                try:
                    producing = bool(solver.Value(is_producing_vars[key])) if solver is not None else bool(is_producing_vars[key])
                except Exception:
                    try:
                        producing = bool(is_producing_vars[key])
                    except Exception:
                        producing = False
            if producing:
                # We'll represent one-day tasks as [Start = date, Finish = date + 1 day]
                gantt_data.append({
                    "Grade": grade,
                    "Start": day_dt,
                    "Finish": day_dt + pd.Timedelta(days=1),
                    "Line": line
                })

    # If no data, return a small empty figure with message text
    if not gantt_data:
        fig = go.Figure()
        fig.update_layout(
            title=title or f"Production Schedule - {line}",
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=240
        )
        # Add annotation to show no data
        fig.add_annotation(text=f"No production data available for {line}.", showarrow=False, xref="paper", yref="paper", x=0.5, y=0.5)
        return fig

    gantt_df = pd.DataFrame(gantt_data)

    # Use px.timeline
    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Grade",
        color="Grade",
        color_discrete_map=grade_color_map,
        category_orders={"Grade": sorted_grades},
        title=title or f"Production Schedule - {line}"
    )

    # Add shutdown vrects if present
    if line in shutdown_periods and shutdown_periods[line]:
        sd_indices = sorted(shutdown_periods[line])
        # make sure indices are inside range
        sd_indices = [i for i in sd_indices if 0 <= i < num_days]
        if sd_indices:
            start_shutdown = dates_pd[sd_indices[0]]
            end_shutdown = dates_pd[sd_indices[-1]] + pd.Timedelta(days=1)
            fig.add_vrect(
                x0=start_shutdown,
                x1=end_shutdown,
                fillcolor="red",
                opacity=0.20,
                layer="below",
                line_width=0,
                annotation_text="Shutdown",
                annotation_position="top left",
                annotation_font_size=14,
                annotation_font_color="red"
            )

    # Axis and layout styling similar to your snippet
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
        tickvals=dates_pd,
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


def build_schedule_table_for_line(
    line: str,
    dates: List[Any],
    grades: List[str],
    is_producing_vars: Dict[Any, Any],
    solver=None
) -> pd.DataFrame:
    """
    Build the schedule summary table for a line: runs with start/end/days (Grade on each run).
    Matches the behavior in your snippet (group consecutive days with same grade).
    """

    dates_pd = [pd.to_datetime(d) for d in dates]
    num_days = len(dates_pd)
    sorted_grades = sorted(grades)

    rows = []
    current_grade = None
    start_day = None

    def _is_producing(grade, line, day_idx):
        key = (grade, line, day_idx)
        if key in is_producing_vars:
            try:
                if solver is not None:
                    return bool(solver.Value(is_producing_vars[key]))
                return bool(is_producing_vars[key])
            except Exception:
                try:
                    return bool(is_producing_vars[key])
                except Exception:
                    return False
        return False

    for d_idx in range(num_days):
        day_dt = dates_pd[d_idx]
        grade_today = None
        for grade in sorted_grades:
            if _is_producing(grade, line, d_idx):
                grade_today = grade
                break

        if grade_today != current_grade:
            if current_grade is not None:
                end_date = dates_pd[d_idx - 1]
                duration = (end_date - start_day).days + 1
                rows.append({
                    "Grade": current_grade,
                    "Start Date": start_day.strftime("%d-%b-%y"),
                    "End Date": end_date.strftime("%d-%b-%y"),
                    "Days": duration
                })
            current_grade = grade_today
            start_day = day_dt
        # else: continue the run

    if current_grade is not None and start_day is not None:
        end_date = dates_pd[-1]
        duration = (end_date - start_day).days + 1
        rows.append({
            "Grade": current_grade,
            "Start Date": start_day.strftime("%d-%b-%y"),
            "End Date": end_date.strftime("%d-%b-%y"),
            "Days": duration
        })

    if not rows:
        return pd.DataFrame(columns=["Grade", "Start Date", "End Date", "Days"])
    return pd.DataFrame(rows)


def build_inventory_fig_for_grade(
    grade: str,
    dates: List[Any],
    inventory_vars: Dict[Any, Any],
    solver=None,
    grade_color_map: Optional[Dict[str, str]] = None,
    allowed_lines: Optional[Dict[str, List[str]]] = None,
    shutdown_periods: Optional[Dict[str, List[int]]] = None,
    min_inventory: Optional[Dict[str, float]] = None,
    max_inventory: Optional[Dict[str, float]] = None,
    buffer_days: int = 0
) -> go.Figure:
    """
    Build an inventory time-series plot for a given grade, with annotations and shutdown shading.
    - inventory_vars expected keyed by (grade, day)
    - allowed_lines: { grade: [line1,line2,...] } used for showing shutdowns relevant to this grade
    - min_inventory/max_inventory: dicts keyed by grade
    """

    dates_pd = [pd.to_datetime(d) for d in dates]
    num_days = len(dates_pd)

    def _val(key):
        if solver is not None:
            try:
                return float(solver.Value(key))
            except Exception:
                pass
        try:
            return float(key)
        except Exception:
            return 0.0

    # Build inventory series (one value per day). If a (grade, 0) exists we include it as day 0.
    inv_values = []
    for d_idx in range(num_days):
        key = (grade, d_idx)
        if key in inventory_vars:
            inv_values.append(_val(inventory_vars[key]))
        else:
            # default zero if missing
            inv_values.append(0.0)

    # Last actual day index used in your snippet
    last_actual_day = max(0, num_days - 1 - buffer_days)

    # Determine start/end/high/low and their x positions
    start_val = inv_values[0] if inv_values else 0.0
    end_val = inv_values[last_actual_day] if inv_values else 0.0
    highest_val = max(inv_values[: last_actual_day + 1]) if inv_values else 0.0
    lowest_val = min(inv_values[: last_actual_day + 1]) if inv_values else 0.0

    # Get the x positions (dates) for those stats
    highest_idx = inv_values.index(highest_val) if inv_values else 0
    lowest_idx = inv_values.index(lowest_val) if inv_values else 0
    highest_x = dates_pd[highest_idx]
    lowest_x = dates_pd[lowest_idx]
    start_x = dates_pd[0] if dates_pd else None
    end_x = dates_pd[last_actual_day] if dates_pd else None

    # Build plotly figure
    fig = go.Figure()
    grade_color_map = grade_color_map or {}
    line_color = grade_color_map.get(grade, BASE_PALETTE[0])

    fig.add_trace(go.Scatter(
        x=dates_pd,
        y=inv_values,
        mode="lines+markers",
        name=grade,
        line=dict(color=line_color, width=3),
        marker=dict(size=6),
        hovertemplate="Date: %{x|%d-%b-%y}<br>Inventory: %{y:.0f} MT<extra></extra>"
    ))

    # Add shutdown shaded regions from allowed_lines (if given)
    shutdown_added = False
    allowed_lines = allowed_lines or {}
    for line in allowed_lines.get(grade, []):
        if shutdown_periods and line in shutdown_periods and shutdown_periods[line]:
            sd_idxs = [i for i in shutdown_periods[line] if 0 <= i < num_days]
            if sd_idxs:
                start_shutdown = dates_pd[sd_idxs[0]]
                end_shutdown = dates_pd[sd_idxs[-1]] + pd.Timedelta(days=1)
                fig.add_vrect(
                    x0=start_shutdown,
                    x1=end_shutdown,
                    fillcolor="red",
                    opacity=0.10,
                    layer="below",
                    line_width=0,
                    annotation_text=f"Shutdown: {line}" if not shutdown_added else "",
                    annotation_position="top left",
                    annotation_font_size=12,
                    annotation_font_color="red"
                )
                shutdown_added = True

    # Min/Max lines
    if min_inventory and grade in min_inventory:
        fig.add_hline(
            y=min_inventory[grade],
            line=dict(color="red", width=2, dash="dash"),
            annotation_text=f"Min: {min_inventory[grade]:,.0f}",
            annotation_position="top left",
            annotation_font_color="red"
        )
    if max_inventory and grade in max_inventory:
        fig.add_hline(
            y=max_inventory[grade],
            line=dict(color="green", width=2, dash="dash"),
            annotation_text=f"Max: {max_inventory[grade]:,.0f}",
            annotation_position="bottom left",
            annotation_font_color="green"
        )

    # Annotations: start, end, high, low (if we have valid dates)
    annotations = []
    if start_x is not None:
        annotations.append(dict(
            x=start_x, y=start_val,
            text=f"Start: {start_val:.0f}",
            showarrow=True, arrowhead=2, ax=-40, ay=30,
            font=dict(color="black", size=11),
            bgcolor="white", bordercolor="gray"
        ))
    if end_x is not None:
        annotations.append(dict(
            x=end_x, y=end_val,
            text=f"End: {end_val:.0f}",
            showarrow=True, arrowhead=2, ax=40, ay=30,
            font=dict(color="black", size=11),
            bgcolor="white", bordercolor="gray"
        ))
    annotations.append(dict(
        x=highest_x, y=highest_val,
        text=f"High: {highest_val:.0f}",
        showarrow=True, arrowhead=2, ax=0, ay=-40,
        font=dict(color="darkgreen", size=11),
        bgcolor="white", bordercolor="gray"
    ))
    annotations.append(dict(
        x=lowest_x, y=lowest_val,
        text=f"Low: {lowest_val:.0f}",
        showarrow=True, arrowhead=2, ax=0, ay=40,
        font=dict(color="firebrick", size=11),
        bgcolor="white", bordercolor="gray"
    ))

    fig.update_layout(
        title=f"Inventory Level - {grade}",
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor="lightgray",
            tickvals=dates_pd,
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

    # add the annotations one by one so Streamlit stays happy with types
    for ann in annotations:
        try:
            fig.add_annotation(
                x=ann["x"],
                y=ann["y"],
                text=ann["text"],
                showarrow=ann["showarrow"],
                arrowhead=ann["arrowhead"],
                ax=ann["ax"],
                ay=ann["ay"],
                font=ann["font"],
                bgcolor=ann["bgcolor"],
                bordercolor=ann["bordercolor"],
                borderwidth=1,
                borderpad=4,
                opacity=0.9
            )
        except Exception:
            # If annotation params cause issues, skip silently to avoid crashing UI
            pass

    return fig
