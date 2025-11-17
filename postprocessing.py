# postprocessing.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
import streamlit as st
import math

def _build_grade_color_map(sorted_grades):
    # generate a color map deterministically for grades
    palette = px.colors.qualitative.Plotly
    color_map = {}
    for i, g in enumerate(sorted_grades):
        color_map[g] = palette[i % len(palette)]
    return color_map

def convert_solver_output_to_display(solver_result, instance):
    """
    Convert solver 'best' into display_result dict used by plotting functions.
    Handle both old and new solution formats.
    """
    best = solver_result.get('best')
    if not best:
        return None

    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = len(dates)
    formatted_dates = [d.strftime('%d-%b-%y') for d in dates]

    # Check if we have the new solution format with is_producing data
    if 'is_producing' in best:
        # New format: use the data already structured in the solution
        return {
            'production': best.get('production', {}),
            'is_producing_map': best.get('is_producing', {}),
            'stockout': best.get('stockout', {}),
            'inventory': best.get('inventory', {}),
            'formatted_dates': formatted_dates,
            'dates': dates,
            'objective': best.get('objective'),
            'transitions': best.get('transitions', {'total': 0})
        }
    else:
        # Old format: reconstruct the data structure
        is_producing_map = {}
        production = {g: {} for g in grades}
        inventory = {g: {} for g in grades}
        stockout = {g: {} for g in grades}

        # Reconstruct is_producing_map from solver values
        solver = solver_result.get('solver')
        if solver and 'assign' in best:
            for (line, d), grade in best.get('assign', {}).items():
                date_label = formatted_dates[d]
                is_producing_map[(grade, line, d)] = True

        # Reconstruct production data
        if 'production' in best:
            for (line, d), entries in best.get('production', {}).items():
                date_label = formatted_dates[d]
                for g, qty in entries.items():
                    production[g].setdefault(date_label, 0)
                    production[g][date_label] += qty

        # Reconstruct inventory data
        if 'inventory' in best:
            for (g, d), val in best.get('inventory', {}).items():
                if d == 0:
                    inventory[g]['initial'] = val
                elif 1 <= d <= len(formatted_dates):
                    inventory[g][formatted_dates[d-1]] = val
                else:
                    inventory[g]['final'] = val

        # Reconstruct stockout data
        if 'unmet' in best:
            for (g, d), val in best.get('unmet', {}).items():
                date_label = formatted_dates[d]
                stockout[g].setdefault(date_label, 0)
                stockout[g][date_label] += val

        return {
            'production': production,
            'is_producing_map': is_producing_map,
            'stockout': stockout,
            'inventory': inventory,
            'formatted_dates': formatted_dates,
            'dates': dates,
            'objective': best.get('objective')
        }

def plot_production_visuals(display_result, instance, params):
    """
    Draw production visualization (Gantt per line, schedule tables).
    Updated to handle new solution format.
    """
    if display_result is None:
        st.info("No results to plot.")
        return

    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = len(dates)
    sorted_grades = sorted(grades)
    grade_color_map = _build_grade_color_map(sorted_grades)
    shutdown_periods = instance.get('shutdown_day_indices', {})
    buffer_days = params.get('buffer_days', 3)

    # Extract production data - handle both old and new formats
    is_producing_map = display_result.get('is_producing_map', {})
    production_data = display_result.get('production', {})
    
    # Debug info
    st.write(f"Debug: Found {len(is_producing_map)} production assignments")
    st.write(f"Debug: Production data keys: {list(production_data.keys())}")

    # Build total production summary
    prod_records = []
    for g, day_map in production_data.items():
        for date_label, qty in day_map.items():
            prod_records.append({'Grade': g, 'Date': date_label, 'Quantity': qty})
    
    total_prod_df = pd.DataFrame(prod_records)
    if total_prod_df.empty:
        total_prod_df = pd.DataFrame(columns=['Grade', 'Date', 'Quantity'])
        st.warning("No production data found in results")

    # Gantt and schedule visualization
    st.subheader("Production Visualization")
    
    # Check if we have any production data
    has_production_data = False
    
    for line in lines:
        st.markdown(f"### Production Schedule - {line}")

        gantt_data = []
        line_has_data = False
        
        # Check both production formats
        for d in range(num_days):
            date = dates[d]
            
            # Method 1: Check is_producing_map (new format)
            for grade in sorted_grades:
                if (grade, line, d) in is_producing_map and is_producing_map[(grade, line, d)]:
                    gantt_data.append({
                        "Grade": grade,
                        "Start": date,
                        "Finish": date + timedelta(days=1),
                        "Line": line
                    })
                    line_has_data = True
                    has_production_data = True
            
            # Method 2: Check production data directly
            date_label = dates[d].strftime('%d-%b-%y')
            for grade in sorted_grades:
                if grade in production_data and date_label in production_data[grade]:
                    qty = production_data[grade][date_label]
                    if qty > 0:
                        # Check if this line produces this grade
                        if line in instance.get('allowed_lines', {}).get(grade, []):
                            # Only add if not already added via is_producing_map
                            if not any(g['Grade'] == grade and g['Start'] == date for g in gantt_data):
                                gantt_data.append({
                                    "Grade": grade,
                                    "Start": date,
                                    "Finish": date + timedelta(days=1),
                                    "Line": line
                                })
                                line_has_data = True
                                has_production_data = True

        if not gantt_data:
            st.info(f"No production data available for {line}.")
            continue

        gantt_df = pd.DataFrame(gantt_data)

        fig = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Grade",
            color="Grade",
            color_discrete_map=grade_color_map,
            category_orders={"Grade": sorted_grades},
            title=f"Production Schedule - {line}"
        )

        # Add shutdown period visualization
        if line in shutdown_periods and shutdown_periods[line]:
            shutdown_days = shutdown_periods[line]
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

        st.plotly_chart(fig, use_container_width=True)

    if not has_production_data:
        st.error("""
        **No production data found in optimization results.**
        
        This could be due to:
        1. **Infeasible constraints** - The solver couldn't find a valid production schedule
        2. **Data format mismatch** - The solution format isn't being processed correctly
        3. **All production assigned to buffer days** - Check if buffer days are too high
        
        **Debugging steps:**
        - Check solver status in the results section
        - Reduce buffer days to 0 and try again
        - Check if demand can be satisfied with available capacity
        - Verify that production constraints aren't too restrictive
        """)
        return

    # Production schedule tables
    st.subheader("Production Schedule by Line")

    def color_grade(val):
        if val in grade_color_map:
            color = grade_color_map[val]
            return f'background-color: {color}; color: white; font-weight: bold; text-align: center;'
        return ''

    for line in lines:
        st.markdown(f"### 🏭 {line}")

        schedule_data = []
        current_grade = None
        start_day = None

        for d in range(num_days):
            date = dates[d]
            grade_today = None

            # Find which grade is producing today
            for grade in sorted_grades:
                # Check both data formats
                if (grade, line, d) in is_producing_map and is_producing_map[(grade, line, d)]:
                    grade_today = grade
                    break
                
                # Also check production quantities
                date_label = dates[d].strftime('%d-%b-%y')
                if grade in production_data and date_label in production_data[grade]:
                    qty = production_data[grade][date_label]
                    if qty > 0 and line in instance.get('allowed_lines', {}).get(grade, []):
                        grade_today = grade
                        break

            if grade_today != current_grade:
                if current_grade is not None:
                    end_date = dates[d - 1]
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
            end_date = dates[num_days - 1]
            duration = (end_date - start_day).days + 1
            schedule_data.append({
                "Grade": current_grade,
                "Start Date": start_day.strftime("%d-%b-%y"),
                "End Date": end_date.strftime("%d-%b-%y"),
                "Days": duration
            })

        if not schedule_data:
            st.info(f"No production schedule data available for {line}.")
            continue

        schedule_df = pd.DataFrame(schedule_data)
        styled_df = schedule_df.style.applymap(color_grade, subset=['Grade'])
        st.dataframe(styled_df, use_container_width=True)

    # Production Summary
    with st.expander("Production Summary & Inventory"):
        with st.container():
            st.subheader("Production Summary")
            if not total_prod_df.empty:
                st.dataframe(total_prod_df, use_container_width=True)
            else:
                st.info("No production summary data available")

def plot_inventory_charts(display_result, instance, params):
    """
    Plot inventory time series for each grade.
    Updated to handle new solution format.
    """
    if display_result is None:
        st.info("No results to display.")
        return

    grades = instance['grades']
    dates = instance['dates']
    formatted_dates = display_result['formatted_dates']
    sorted_grades = sorted(grades)
    grade_color_map = _build_grade_color_map(sorted_grades)
    shutdown_periods = instance.get('shutdown_day_indices', {})
    buffer_days = params.get('buffer_days', 3)

    min_inventory = instance.get('min_inventory', {})
    max_inventory = instance.get('max_inventory', {})

    # For each grade, construct inventory_values aligned to dates[]
    for grade in sorted_grades:
        inv_map = display_result['inventory'].get(grade, {})
        
        # inventory_values for plotting: len=num_days (use 0 when missing)
        inventory_values = []
        for d_idx, d in enumerate(dates):
            label = formatted_dates[d_idx]
            val = inv_map.get(label, None)
            # if label missing, try 'initial' for day 0
            if val is None and d_idx == 0:
                val = inv_map.get('initial', 0)
            if val is None:
                val = 0
            inventory_values.append(val)

        if not inventory_values or all(v == 0 for v in inventory_values):
            st.info(f"No inventory data available for grade {grade}")
            continue

        last_actual_day = max(0, len(dates) - buffer_days - 1)

        start_val = inventory_values[0] if inventory_values else 0
        end_val = inventory_values[last_actual_day] if inventory_values else 0
        highest_val = max(inventory_values[: last_actual_day + 1]) if inventory_values else 0
        lowest_val = min(inventory_values[: last_actual_day + 1]) if inventory_values else 0

        start_x = dates[0]
        end_x = dates[last_actual_day] if last_actual_day < len(dates) else dates[-1]
        highest_x = dates[inventory_values.index(highest_val)] if highest_val in inventory_values else dates[0]
        lowest_x = dates[inventory_values.index(lowest_val)] if lowest_val in inventory_values else dates[0]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=dates,
            y=inventory_values,
            mode="lines+markers",
            name=grade,
            line=dict(color=grade_color_map.get(grade, '#636EFA'), width=3),
            marker=dict(size=6),
            hovertemplate="Date: %{x|%d-%b-%y}<br>Inventory: %{y:.0f} MT<extra></extra>"
        ))

        # Add shutdown periods for plants that produce this grade
        shutdown_added = False
        for line in instance.get('allowed_lines', {}).get(grade, []):
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

        # Add min/max lines
        min_inv_val = min_inventory.get(grade, 0)
        max_inv_val = max_inventory.get(grade, 10**9)
        
        if min_inv_val > 0:
            fig.add_hline(
                y=min_inv_val,
                line=dict(color="red", width=2, dash="dash"),
                annotation_text=f"Min: {min_inv_val:,.0f}",
                annotation_position="top left",
                annotation_font_color="red"
            )
        
        if max_inv_val < 10**9:
            fig.add_hline(
                y=max_inv_val,
                line=dict(color="green", width=2, dash="dash"),
                annotation_text=f"Max: {max_inv_val:,.0f}",
                annotation_position="bottom left",
                annotation_font_color="green"
            )

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
            title=f"Inventory Level - {grade}",
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

        st.plotly_chart(fig, use_container_width=True)
