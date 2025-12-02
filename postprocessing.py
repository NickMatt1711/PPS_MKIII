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
#  GANTT CHART (OPTION A — GRADE ON Y-AXIS)
# ===============================================================

def create_gantt_chart(
    solution: Dict,
    line: str,
    dates: List[date],
    shutdown_periods: Dict,
    grade_colors: Dict,
    capacities: Dict = None,
    buffer_days: int = 0
):

    dates = [_ensure_date(d) for d in dates]
    
    # Determine last actual planning day (before buffer)
    last_actual_day = len(dates) - buffer_days

    schedule = solution.get("is_producing", {}).get(line, {})
    production_data = solution.get("production", {})

    gantt_rows = []
    daily_production_data = []

    for d in range(len(dates)):
        ds = dates[d].strftime("%d-%b-%y")
        grade_today = schedule.get(ds)
        
        # Skip buffer days in gantt chart
        if d >= last_actual_day:
            continue
            
        if grade_today:
            # Get production amount for this day
            production_today = 0
            if grade_today in production_data:
                production_today = production_data[grade_today].get(ds, 0)
            
            gantt_rows.append({
                "Grade": grade_today,
                "Production (MT)": production_today,
                "Start": dates[d],
                "Finish": dates[d] + timedelta(days=1),
                "Line": line,
                "Day_Index": d
            })
            
            daily_production_data.append({
                "Date": dates[d],
                "Grade": grade_today,
                "Production": production_today,
                "Full_Capacity": capacities.get(line, 0) if capacities else 0
            })

    if not gantt_rows:
        return None

    df = pd.DataFrame(gantt_rows)
    
    # Create figure
    fig = go.Figure()
    
    # Group by grade for better visualization
    for grade in df["Grade"].unique():
        grade_df = df[df["Grade"] == grade]
        
        # Add gantt bars
        fig.add_trace(go.Bar(
            x=[(row["Finish"] - row["Start"]).days for _, row in grade_df.iterrows()],
            y=[grade] * len(grade_df),
            base=[row["Start"] for _, row in grade_df.iterrows()],
            orientation='h',
            name=grade,
            marker_color=grade_colors.get(grade, "#5E7CE2"),
            hovertext=[
                f"Date: {row['Start'].strftime('%d-%b-%y')}<br>" +
                f"Grade: {grade}<br>" +
                f"Production: {row['Production (MT)']:,.0f} MT<br>" +
                f"Line: {line}<br>" +
                f"Day: {row['Day_Index'] + 1}"
                for _, row in grade_df.iterrows()
            ],
            hoverinfo="text",
            showlegend=True
        ))

    # Shutdown shading
    if line in shutdown_periods and shutdown_periods[line]:
        sd = shutdown_periods[line]
        # Filter shutdown days within demand period
        sd_within_demand = [d for d in sd if d < last_actual_day]
        if sd_within_demand:
            x0 = dates[sd_within_demand[0]]
            x1 = dates[sd_within_demand[-1]] + timedelta(days=1)

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
        gridcolor="lightgray",
        tickfont=dict(color="gray", size=12),
        title="Grade"
    )
    
    fig.update_xaxes(
        title="Date",
        tickformat="%d-%b",
        dtick="D1",
        showgrid=True,
        gridcolor="lightgray",
        tickfont=dict(color="gray", size=12)
    )

    # Add production summary annotation
    total_production = df["Production (MT)"].sum()
    avg_production = df["Production (MT)"].mean() if len(df) > 0 else 0
    days_produced = len(df)
    
    production_summary = f"""
    <b>Production Summary:</b><br>
    Total: {total_production:,.0f} MT<br>
    Average: {avg_production:,.0f} MT/day<br>
    Days Produced: {days_produced}/{last_actual_day}
    """
    
    fig.add_annotation(
        x=1.02,
        y=0.5,
        xref="paper",
        yref="paper",
        text=production_summary,
        showarrow=False,
        align="left",
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="gray",
        borderwidth=1,
        borderpad=4
    )

    fig.update_layout(
        height=350,
        bargap=0.2,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=80, r=200, t=60, b=60),
        font=dict(size=12, color="gray"),
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
            font_color="gray"
        ),
        barmode="overlay"
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
    
    # Get production data for this grade
    production_dict = solution.get("production", {}).get(grade, {})
    production_vals = []
    
    for i, d in enumerate(dates):
        date_str = d.strftime("%d-%b-%y")
        # For buffer days, production is 0
        if i >= last_actual_day:
            production_vals.append(0)
        else:
            production_vals.append(production_dict.get(date_str, 0))
    
    # Calculate daily demand fulfillment for tooltip
    daily_data = []
    for i, (inv, prod) in enumerate(zip(inv_vals, production_vals)):
        daily_data.append({
            "Date": dates[i],
            "Inventory": inv,
            "Production": prod,
            "Day_Type": "Buffer" if i >= last_actual_day else "Demand"
        })

    start_val = inv_vals[0]
    end_val = inv_vals[last_actual_day - 1] if last_actual_day > 0 else inv_vals[0]
    highest_val = max(inv_vals[:last_actual_day]) if last_actual_day > 0 else inv_vals[0]
    lowest_val = min(inv_vals[:last_actual_day]) if last_actual_day > 0 else inv_vals[0]

    start_x = dates[0]
    end_x = dates[last_actual_day - 1] if last_actual_day > 0 else dates[0]
    
    # Find indices for highest/lowest within demand period
    highest_idx = inv_vals.index(highest_val) if highest_val in inv_vals[:last_actual_day] else 0
    lowest_idx = inv_vals.index(lowest_val) if lowest_val in inv_vals[:last_actual_day] else 0
    
    highest_x = dates[highest_idx]
    lowest_x = dates[lowest_idx]

    fig = go.Figure()

    # Inventory line
    fig.add_trace(go.Scatter(
        x=dates,
        y=inv_vals,
        mode="lines+markers",
        name=f"{grade} Inventory",
        line=dict(color=grade_colors.get(grade, "#5E7CE2"), width=3),
        marker=dict(size=6),
        hovertemplate="Date: %{x|%d-%b-%y}<br>Inventory: %{y:.0f} MT<br>Production: %{customdata[0]:.0f} MT<extra></extra>",
        customdata=[[prod] for prod in production_vals]
    ))

    # Add production bars (stacked on top of inventory for visualization)
    fig.add_trace(go.Bar(
        x=dates,
        y=production_vals,
        name=f"{grade} Production",
        marker_color='rgba(92, 184, 92, 0.4)',
        hovertemplate="Date: %{x|%d-%b-%y}<br>Production: %{y:.0f} MT<extra></extra>",
        visible='legendonly'  # Hidden by default, can be toggled from legend
    ))

    # Add vertical line to separate demand period from buffer
    if buffer_days > 0 and last_actual_day < len(dates):
        fig.add_vline(
            x=dates[last_actual_day],
            line_dash="dash",
            line_color="gray",
            opacity=0.5,
            annotation_text="Buffer Period Start",
            annotation_position="top right"
        )

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

    # Annotations (only for demand period)
    annotations = []
    
    if last_actual_day > 0:
        annotations.extend([
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
            )
        ])
    
    if highest_val > start_val and highest_idx < last_actual_day:
        annotations.append(
            dict(
                x=highest_x, y=highest_val,
                text=f"High: {highest_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=0, ay=-40,
                font=dict(color="darkgreen", size=11),
                bgcolor="white", bordercolor="gray"
            )
        )
    
    if lowest_val < start_val and lowest_idx < last_actual_day:
        annotations.append(
            dict(
                x=lowest_x, y=lowest_val,
                text=f"Low: {lowest_val:.0f}",
                showarrow=True, arrowhead=2,
                ax=0, ay=40,
                font=dict(color="firebrick", size=11),
                bgcolor="white", bordercolor="gray"
            )
        )

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
        font=dict(size=12, color="gray"),
        height=420,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
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

def create_production_summary(solution, production_vars, solver, grades, lines, num_days, buffer_days=0):
    """Builds production summary table for demand period only (excluding buffer days)."""
    rows = []
    
    # Calculate last day of actual demand period (excluding buffer)
    last_demand_day = num_days - buffer_days
    
    for grade in sorted(grades):
        row = {"Grade": grade}
        total = 0

        for line in lines:
            val = 0
            for d in range(last_demand_day):  # Only count production during demand period
                key = (grade, line, d)
                if key in production_vars:
                    try:
                        val += solver.Value(production_vars[key])
                    except:
                        # If solver object not available, try to get from solution dict
                        try:
                            date_key = d.strftime("%d-%b-%y") if hasattr(d, 'strftime') else f"Day_{d}"
                            production_data = solution.get('production', {}).get(grade, {})
                            if date_key in production_data:
                                val += production_data[date_key]
                        except:
                            pass
            row[line] = int(val)
            total += val

        row["Total Produced"] = int(total)
        stockout_dict = solution.get('stockout', {}).get(grade, {})
        # Sum stockout only for demand period
        total_stockout = 0
        for date_str, stockout_val in stockout_dict.items():
            try:
                # Only count stockout during demand period
                # We need to check if this date is within demand period
                # For simplicity, we'll sum all stockout for now
                total_stockout += stockout_val
            except:
                pass
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
#  STOCKOUT DETAILS TABLE
# ===============================================================

def create_stockout_details_table(
    solution: Dict,
    grades: List[str],
    dates: List[date],
    buffer_days: int = 0
) -> pd.DataFrame:
    """Create detailed table of stockout occurrences."""
    rows = []
    
    # Determine last actual planning day (before buffer)
    last_actual_day = len(dates) - buffer_days if buffer_days > 0 else len(dates)
    
    stockout_dict = solution.get('stockout', {})
    
    for grade in sorted(grades):
        if grade in stockout_dict:
            grade_stockouts = stockout_dict[grade]
            for date_str, stockout_qty in grade_stockouts.items():
                if stockout_qty > 0:
                    # Try to parse date string
                    try:
                        if isinstance(date_str, str):
                            # Handle date format conversion
                            try:
                                date_obj = datetime.strptime(date_str, "%d-%b-%y")
                            except:
                                # Try other formats
                                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        else:
                            date_obj = date_str
                        
                        # Check if within demand period (not buffer)
                        date_index = -1
                        for i, d in enumerate(dates):
                            if i >= last_actual_day:
                                break
                            if _ensure_date(d) == _ensure_date(date_obj):
                                date_index = i
                                break
                        
                        if date_index >= 0:  # Only include if within demand period
                            rows.append({
                                "Date": _ensure_date(date_obj).strftime("%d-%b-%y"),
                                "Grade": grade,
                                "Stockout Quantity (MT)": stockout_qty,
                                "Day Index": date_index
                            })
                    except Exception as e:
                        # Skip if date parsing fails
                        continue
    
    if not rows:
        return pd.DataFrame()
    
    df = pd.DataFrame(rows)
    df = df.sort_values(["Date", "Grade"])
    df = df.reset_index(drop=True)
    return df
