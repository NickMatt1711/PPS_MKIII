# FILE: app.py
"""
App flow: Upload -> Review & Configure -> Solve -> Results
"""

import streamlit as st
import io
import json
import pandas as pd
from datetime import timedelta

from constants import *
from ui_components import *
from data_loader import ExcelDataLoader, process_plant_data, process_inventory_data, process_demand_data, process_shutdown_dates, process_transition_rules
from preview_tables import render_sheet_preview, render_all_sheets
from solver_cp_sat import build_and_solve_model
from postprocessing import create_gantt_chart, create_inventory_chart, get_or_create_grade_colors

# Page config
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide", initial_sidebar_state="collapsed")
apply_custom_css()

# Session defaults
st.session_state.setdefault(SS_STAGE, 0)
st.session_state.setdefault(SS_UPLOADED_FILE, None)
st.session_state.setdefault(SS_EXCEL_DATA, None)
st.session_state.setdefault(SS_SOLUTION, None)
st.session_state.setdefault(SS_GRADE_COLORS, {})
st.session_state.setdefault(SS_OPTIMIZATION_PARAMS, {
    "time_limit": DEFAULT_TIME_LIMIT_MIN,
    "buffer_days": DEFAULT_BUFFER_DAYS,
    "stockout_penalty": DEFAULT_STOCKOUT_PENALTY,
    "transition_penalty": DEFAULT_TRANSITION_PENALTY,
    "continuity_bonus": DEFAULT_CONTINUITY_BONUS,
})


def stage_upload():
    render_header(f"{APP_ICON} {APP_TITLE}", "Upload production data")
    render_stage_progress(0)

    st.markdown("### 📤 Upload Excel File")
    st.markdown("Please upload an Excel file containing the required sheets: Plant, Inventory, Demand.")
    col1, col2 = st.columns([6, 1])
    with col1:
        uploaded_file = st.file_uploader("Choose an Excel file", type=ALLOWED_EXTENSIONS)
        if uploaded_file:
            st.session_state[SS_UPLOADED_FILE] = uploaded_file
            render_alert("File uploaded — validating...", "info")
            try:
                buf = io.BytesIO(uploaded_file.read())
                loader = ExcelDataLoader(buf)
                ok, data, errors, warnings = loader.load_and_validate()
                if ok:
                    st.session_state[SS_EXCEL_DATA] = data
                    st.success("File validated. Proceed to Review & Configure below.")
                    st.session_state[SS_STAGE] = 1
                else:
                    for e in errors:
                        render_alert(e, "error")
                    for w in warnings:
                        render_alert(w, "warning")
            except Exception as e:
                render_alert(f"Failed to read upload: {e}", "error")

    with col2:
        render_download_template_button()

    st.markdown("<br>")
    if st.button("Proceed to Review & Configure →", disabled=(st.session_state.get(SS_EXCEL_DATA) is None)):
        if st.session_state.get(SS_EXCEL_DATA):
            st.session_state[SS_STAGE] = 1
            st.experimental_rerun()


def render_review_and_configure():
    render_header(f"{APP_ICON} {APP_TITLE}", "Review uploaded sheets and configure optimization")
    render_stage_progress(1)

    excel_data = st.session_state.get(SS_EXCEL_DATA)
    if not excel_data:
        render_alert("No uploaded data. Please upload a file first.", "warning")
        if st.button("← Back to Upload"):
            st.session_state[SS_STAGE] = 0
            st.experimental_rerun()
        return

    # Data preview (all sheets)
    st.markdown("### 📊 Data Preview")
    st.markdown('<div class="m3-card">', unsafe_allow_html=True)
    for sheet_name, df in excel_data.items():
        icon = {"Plant":"🏭","Inventory":"📦","Demand":"📈"}.get(sheet_name, "📄")
        render_sheet_preview(sheet_name, df, icon)
    st.markdown('</div>', unsafe_allow_html=True)

    render_section_divider()

    # Optimization settings (single card under previews)
    st.markdown("### ⚙️ Optimization Settings")
    st.markdown('<div class="m3-card">', unsafe_allow_html=True)
    params = st.session_state[SS_OPTIMIZATION_PARAMS]

    params["time_limit"] = st.number_input("⏱ Time limit (minutes)", min_value=1, max_value=120, value=int(params.get("time_limit", DEFAULT_TIME_LIMIT_MIN)))
    params["buffer_days"] = st.number_input("📆 Buffer days", min_value=0, max_value=14, value=int(params.get("buffer_days", DEFAULT_BUFFER_DAYS)))
    params["stockout_penalty"] = st.number_input("❗ Stockout penalty", min_value=1, value=int(params.get("stockout_penalty", DEFAULT_STOCKOUT_PENALTY)))
    params["transition_penalty"] = st.number_input("🔄 Transition penalty", min_value=0, value=int(params.get("transition_penalty", DEFAULT_TRANSITION_PENALTY)))
    params["continuity_bonus"] = st.number_input("🔁 Continuity bonus", min_value=0, value=int(params.get("continuity_bonus", DEFAULT_CONTINUITY_BONUS)))

    if st.button("Reset to defaults"):
        st.session_state[SS_OPTIMIZATION_PARAMS] = {
            "time_limit": DEFAULT_TIME_LIMIT_MIN,
            "buffer_days": DEFAULT_BUFFER_DAYS,
            "stockout_penalty": DEFAULT_STOCKOUT_PENALTY,
            "transition_penalty": DEFAULT_TRANSITION_PENALTY,
            "continuity_bonus": DEFAULT_CONTINUITY_BONUS,
        }
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>")

    # Solve button and progress area (on same page)
    solve_col1, solve_col2 = st.columns([3,1])
    with solve_col1:
        start = st.button("🚀 Start Optimization", use_container_width=True)
    with solve_col2:
        st.write("")  # placeholder for alignment

    if start:
        # prepare data for solver
        try:
            # extract processed forms using data_loader helpers
            plant_data = process_plant_data(excel_data["Plant"])
            inventory_data = process_inventory_data(excel_data["Inventory"], plant_data["lines"])
            demand_data, dates, num_days = process_demand_data(excel_data["Demand"], buffer_days=int(params["buffer_days"]))
            formatted_dates = [d.strftime("%d-%b-%y") for d in dates]
            shutdown_periods = process_shutdown_dates(plant_data.get("shutdown_periods", {}), dates)
            transition_dfs = {k: v for k, v in excel_data.items() if k.startswith("Transition_")}
            transition_rules = process_transition_rules(transition_dfs)

        except Exception as e:
            render_alert(f"Failed to prepare data for solver: {e}", "error")
            return

        progress_bar = st.progress(0.0)
        status_text = st.empty()
        status_text.info("Building model...")

        def progress_callback(pct, msg):
            try:
                progress_bar.progress(min(max(pct, 0.0), 1.0))
                status_text.info(msg)
            except Exception:
                pass

        try:
            status, solution_callback, solver = build_and_solve_model(
                grades=inventory_data["grades"],
                lines=plant_data["lines"],
                dates=dates,
                formatted_dates=formatted_dates,
                num_days=num_days,
                capacities=plant_data["capacities"],
                initial_inventory=inventory_data["initial_inventory"],
                min_inventory=inventory_data["min_inventory"],
                max_inventory=inventory_data["max_inventory"],
                min_closing_inventory=inventory_data["min_closing_inventory"],
                demand_data=demand_data,
                allowed_lines=inventory_data["allowed_lines"],
                min_run_days=inventory_data["min_run_days"],
                max_run_days=inventory_data["max_run_days"],
                force_start_date=inventory_data.get("force_start_date", {}),
                rerun_allowed=inventory_data.get("rerun_allowed", {}),
                material_running_info=plant_data.get("material_running", {}),
                shutdown_periods=shutdown_periods,
                transition_rules=transition_rules,
                buffer_days=int(params["buffer_days"]),
                stockout_penalty=int(params["stockout_penalty"]),
                transition_penalty=int(params["transition_penalty"]),
                continuity_bonus=int(params["continuity_bonus"]),
                time_limit_min=int(params["time_limit"]),
                progress_callback=progress_callback
            )

            # collect final solution
            final_solution = {}
            try:
                final_solution = solution_callback.solutions[-1] if (hasattr(solution_callback, "solutions") and solution_callback.solutions) else {}
            except Exception:
                final_solution = {}

            st.session_state[SS_SOLUTION] = {
                "status": status,
                "solution_callback": solution_callback,
                "solver": solver,
                "solution": final_solution,
                "data_meta": {
                    "grades": inventory_data["grades"],
                    "lines": plant_data["lines"],
                    "dates": dates,
                    "formatted_dates": formatted_dates,
                    "num_days": num_days,
                    "shutdown_periods": shutdown_periods,
                    "allowed_lines": inventory_data["allowed_lines"],
                    "initial_inventory": inventory_data["initial_inventory"],
                    "min_inventory": inventory_data["min_inventory"],
                    "max_inventory": inventory_data["max_inventory"],
                }
            }

            progress_bar.progress(1.0)
            status_text.success("Optimization finished.")
            st.session_state[SS_STAGE] = 2
            st.experimental_rerun()

        except Exception as e:
            render_alert(f"Error during solve: {e}", "error")
            raise

def render_results():
    render_header(f"{APP_ICON} {APP_TITLE}", "Results")
    render_stage_progress(2)

    sol_pack = st.session_state.get(SS_SOLUTION)
    if not sol_pack:
        render_alert("No solution available. Run optimization first.", "warning")
        if st.button("← Back to Review & Configure"):
            st.session_state[SS_STAGE] = 1
            st.experimental_rerun()
        return

    solution = sol_pack.get("solution", {}) or {}
    meta = sol_pack.get("data_meta", {})
    grade_colors = get_or_create_grade_colors(meta.get("grades", []))

    # KPIs
    st.markdown("### 📊 Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    objective_val = solution.get("objective", 0)
    transitions_total = solution.get("transitions", {}).get("total", 0)
    total_stockouts = sum(sum(v.values()) if isinstance(v, dict) else 0 for v in solution.get("stockout", {}).values())

    render_metric_card("Objective Value", f"{objective_val:,}", c1)
    render_metric_card("Total Transitions", str(transitions_total), c2)
    render_metric_card("Total Stockouts", f"{total_stockouts:,} MT", c3)
    render_metric_card("Run Status", str(sol_pack.get("status")), c4)

    render_section_divider()

    # Production schedule
    st.markdown("### 📅 Production Schedule (Gantt)")
    for line in meta.get("lines", []):
        st.markdown(f"#### {line}")
        try:
            fig = create_gantt_chart(solution, line, meta.get("dates", []), meta.get("shutdown_periods", {}), grade_colors)
        except Exception as e:
            st.error(f"Failed to render gantt for {line}: {e}")
            fig = None
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No schedule available for {line}.")
        render_section_divider()

    # Inventory charts
    st.markdown("### 📦 Inventory Analysis")
    for grade in sorted(meta.get("grades", [])):
        st.markdown(f"#### {grade}")
        try:
            fig = create_inventory_chart(
                solution,
                grade,
                meta.get("dates", []),
                meta.get("min_inventory", {}).get(grade),
                meta.get("max_inventory", {}).get(grade),
                meta.get("allowed_lines", {}),
                meta.get("shutdown_periods", {}),
                grade_colors,
                meta.get("initial_inventory", {}).get(grade, 0),
                meta.get("buffer_days", 0)
            )
        except Exception as e:
            st.error(f"Failed to render inventory for {grade}: {e}")
            fig = None
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        render_section_divider()

    # Raw outputs & downloads
    st.markdown("### 🔽 Download Results")
    result_json = json.dumps(solution, default=str, indent=2)
    st.download_button("Download results (JSON)", data=result_json, file_name="solution.json", mime="application/json")

    st.markdown("<br>")
    if st.button("🔄 New Run (clear state)"):
        theme_val = st.session_state.get(SS_THEME, "light")
        st.session_state.clear()
        st.session_state[SS_THEME] = theme_val
        st.experimental_rerun()


def main():
    stage = st.session_state.get(SS_STAGE, 0)
    if stage == 0:
        stage_upload()
    elif stage == 1:
        render_review_and_configure()
    elif stage == 2:
        render_results()
    else:
        st.session_state[SS_STAGE] = 0
        st.experimental_rerun()


if __name__ == "__main__":
    main()
