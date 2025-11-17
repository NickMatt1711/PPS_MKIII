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
    Convert the new solver output format to the display format expected by visualization functions.
    """
    best = solver_result.get('best')
    if not best:
        return None

    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    num_days = len(dates)
    formatted_dates = [d.strftime('%d-%b-%y') for d in dates]

    # Initialize the display structure
    production = {g: {} for g in grades}
    inventory = {g: {} for g in grades}
    stockout = {g: {} for g in grades}
    is_producing_map = {}

    # DEBUG: Show what we're working with
    st.write("🔍 Debug - Best solution keys:", list(best.keys()))
    
    # Process production data from the new format
    if 'production' in best:
        st.write("🔍 Processing production data from new format")
        for grade, date_production in best['production'].items():
            for date_str, qty in date_production.items():
                if qty > 0:
                    production[grade][date_str] = qty
                    st.write(f"  - {grade} on {date_str}: {qty} MT")

    # Process is_producing data from the new format
    if 'is_producing' in best:
        st.write("🔍 Processing production assignments")
        for line, date_assignments in best['is_producing'].items():
            for date_str, grade in date_assignments.items():
                if grade:  # Only if there's an assignment
                    # Find the day index for this date
                    try:
                        day_index = formatted_dates.index(date_str)
                        is_producing_map[(grade, line, day_index)] = True
                        st.write(f"  - {line} on {date_str}: producing {grade}")
                    except ValueError:
                        pass  # Date not found in formatted dates

    # Process inventory data
    if 'inventory' in best:
        st.write("🔍 Processing inventory data")
        for grade, inv_data in best['inventory'].items():
            inventory[grade] = inv_data
            for date_str, inv_val in inv_data.items():
                st.write(f"  - {grade} inventory on {date_str}: {inv_val} MT")

    # Process stockout data
    if 'stockout' in best:
        st.write("🔍 Processing stockout data")
        for grade, stockout_data in best['stockout'].items():
            for date_str, stockout_val in stockout_data.items():
                if stockout_val > 0:
                    stockout[grade][date_str] = stockout_val
                    st.write(f"  - {grade} stockout on {date_str}: {stockout_val} MT")

    # If we still don't have production data, try to reconstruct from solver values
    if not any(production[g] for g in grades) and solver_result.get('solver'):
        st.write("🔍 Reconstructing production data from solver variables")
        solver = solver_result['solver']
        
        # This would require access to the original model variables
        # For now, we'll rely on the data already extracted
        
    # Final debug summary
    total_production = sum(sum(production[g].values()) for g in grades)
    st.write(f"📊 Total production across all grades: {total_production} MT")
    st.write(f"📊 Production assignments found: {len(is_producing_map)}")

    return {
        'production': production,
        'is_producing_map': is_producing_map,
        'stockout': stockout,
        'inventory': inventory,
        'formatted_dates': formatted_dates,
        'dates': dates,
        'objective': best.get('objective'),
        'transitions': best.get('transitions', {'total': 0})
    }

def plot_production_visuals(display_result, instance, params):
    """
    Draw production visualization (Gantt per line, schedule tables).
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

    # Extract data
    is_producing_map = display_result.get('is_producing_map', {})
    production_data = display_result.get('production', {})
    
    # Debug information
    st.write("🎯 Visualization Debug Info:")
    st.write(f"- Grades: {sorted_grades}")
    st.write(f"- Lines: {lines}")
    st.write(f"- Planning horizon: {num_days} days")
    st.write(f"- Production assignments found: {len(is_producing_map)}")
    
    for grade in sorted_grades:
        grade_production = sum(production_data.get(grade, {}).values())
        if grade_production > 0:
            st.write(f"- {grade}: {grade_production} MT total production")

    # Build production summary
    prod_records = []
    for g, day_map in production_data.items():
        for date_label, qty in day_map.items():
            prod_records.append({'Grade': g, 'Date': date_label, 'Quantity': qty})
    
    total_prod_df = pd.DataFrame(prod_records)
    if not total_prod_df.empty:
        st.write("📋 Production Summary Table:")
        st.dataframe(total_prod_df, use_container_width=True)

    # Gantt Charts for each line
    st.header("🏭 Production Gantt Charts")
    
    has_any_production = False
    
    for line in lines:
        st.subheader(f"📅 {line} Production Schedule")
        
        gantt_data = []
        line_production_found = False
        
        # Method 1: Use is_producing_map (most reliable)
        for d in range(num_days):
            date = dates[d]
            date_str = date.strftime('%d-%b-%y')
            
            for grade in sorted_grades:
                if (grade, line, d) in is_producing_map:
                    gantt_data.append({
                        "Grade": grade,
                        "Start": date,
                        "Finish": date + timedelta(days=1),
                        "Line": line
                    })
                    line_production_found = True
                    has_any_production = True
                    st.write(f"  ✅ {line} producing {grade} on {date_str} (from is_producing_map)")
        
        # Method 2: Fallback to production quantities
        if not line_production_found:
            for d in range(num_days):
                date = dates[d]
                date_str = date.strftime('%d-%b-%y')
                
                for grade in sorted_grades:
                    if grade in production_data and date_str in production_data[grade]:
                        qty = production_data[grade][date_str]
                        if qty > 0:
                            # Check if this line can produce this grade
                            if line in instance.get('allowed_lines', {}).get(grade, []):
                                gantt_data.append({
                                    "Grade": grade,
                                    "Start": date,
                                    "Finish": date + timedelta(days=1),
                                    "Line": line
                                })
                                line_production_found = True
                                has_any_production = True
                                st.write(f"  ✅ {line} producing {grade} on {date_str} ({qty} MT)")

        if not gantt_data:
            st.info(f"No production scheduled for {line}")
            continue

        # Create Gantt chart
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

        # Add shutdown periods
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
            margin=dict(l=60, r=160, t=60, b=60),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=12),
        )

        st.plotly_chart(fig, use_container_width=True)

    if not has_any_production:
        st.error("""
        **No production data found in the optimization results.**
        
        **Possible causes:**
        1. **Infeasible problem** - Constraints cannot be satisfied
        2. **All production in buffer days** - Try reducing buffer days to 0
        3. **Data format issue** - Solution data not being processed correctly
        
        **Check:**
        - Solver status should be OPTIMAL or FEASIBLE
        - Total production should be greater than 0
        - Verify that production constraints allow for production
        """)
        return

    # Production Schedule Tables
    st.header("📋 Detailed Production Schedule")
    
    def color_grade(val):
        if val in grade_color_map:
            color = grade_color_map[val]
            return f'background-color: {color}; color: white; font-weight: bold; text-align: center;'
        return ''

    for line in lines:
        st.subheader(f"🏭 {line}")
        
        schedule_data = []
        current_grade = None
        start_day = None
        run_length = 0

        for d in range(num_days):
            date = dates[d]
            grade_today = None

            # Find what's being produced today
            for grade in sorted_grades:
                if (grade, line, d) in is_producing_map:
                    grade_today = grade
                    break

            # Handle grade changes
            if grade_today != current_grade:
                # Save the previous run
                if current_grade is not None and run_length > 0:
                    end_date = dates[d - 1]
                    schedule_data.append({
                        "Grade": current_grade,
                        "Start Date": start_day.strftime("%d-%b-%y"),
                        "End Date": end_date.strftime("%d-%b-%y"),
                        "Days": run_length
                    })
                
                # Start new run
                current_grade = grade_today
                start_day = date
                run_length = 1 if grade_today is not None else 0
            elif grade_today is not None:
                # Continue current run
                run_length += 1

        # Don't forget the last run
        if current_grade is not None and run_length > 0:
            end_date = dates[num_days - 1]
            schedule_data.append({
                "Grade": current_grade,
                "Start Date": start_day.strftime("%d-%b-%y"),
                "End Date": end_date.strftime("%d-%b-%y"),
                "Days": run_length
            })

        if not schedule_data:
            st.info(f"No production campaigns scheduled for {line}")
            continue

        schedule_df = pd.DataFrame(schedule_data)
        styled_df = schedule_df.style.applymap(color_grade, subset=['Grade'])
        st.dataframe(styled_df, use_container_width=True)

    # Production Summary
    st.header("📊 Production Summary")
    if not total_prod_df.empty:
        # Pivot for better summary view
        summary_df = total_prod_df.pivot_table(
            index='Grade', 
            columns='Date', 
            values='Quantity', 
            aggfunc='sum',
            fill_value=0
        )
        st.dataframe(summary_df, use_container_width=True)
        
        # Total by grade
        grade_totals = total_prod_df.groupby('Grade')['Quantity'].sum()
        st.write("**Total Production by Grade:**")
        for grade, total in grade_totals.items():
            st.write(f"- {grade}: {total:,.0f} MT")
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
