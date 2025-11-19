"""
Transform solver results to DataFrames and Plotly figures for display.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from constants import GRADE_PALETTE
from typing import Dict, Any, List

def build_gantt_df(schedule: Dict[str, Dict[str, Any]]):
    rows = []
    # schedule: plant -> {date_str: grade or None}
    for plant, daymap in schedule.items():
        current_grade = None
        start = None
        for date_str, grade in daymap.items():
            if grade != current_grade:
                # close old
                if current_grade is not None:
                    rows.append({"Plant": plant, "Grade": current_grade, "Start": start, "End": prev_date})
                current_grade = grade
                start = date_str
            prev_date = date_str
        if current_grade is not None:
            rows.append({"Plant": plant, "Grade": current_grade, "Start": start, "End": prev_date})
    df = pd.DataFrame(rows)
    return df

def gantt_figure_from_schedule(schedule: Dict[str, Dict[str, Any]]):
    df = build_gantt_df(schedule)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Gantt: no production scheduled")
        return fig
    # assign colors to grades
    grades = sorted(df['Grade'].dropna().unique())
    color_map = {g: GRADE_PALETTE[i % len(GRADE_PALETTE)] for i, g in enumerate(grades)}
    fig = go.Figure()
    for _, row in df.iterrows():
        if pd.isna(row['Grade']):
            continue
        fig.add_trace(go.Bar(
            x=[(pd.to_datetime(row['End'], format="%d-%b-%y") - pd.to_datetime(row['Start'], format="%d-%b-%y")).days + 1],
            y=[row['Plant']],
            base=pd.to_datetime(row['Start'], format="%d-%b-%y"),
            orientation='h',
            name=row['Grade'],
            marker=dict(color=color_map[row['Grade']])
        ))
    fig.update_layout(barmode='stack', title="Production Gantt")
    return fig

def inventory_df_from_results(inventory_res: Dict[str, Dict[str, Any]]):
    # inventory_res: grade -> {date_str: value, ..., final: value}
    dfs = []
    for g, series in inventory_res.items():
        s = series.copy()
        final = s.pop("final", None)
        long = pd.DataFrame(list(s.items()), columns=["Date", "Inventory"])
        long["Grade"] = g
        dfs.append(long)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame(columns=["Date", "Inventory", "Grade"])
