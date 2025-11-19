"""
Main Streamlit application orchestrating UI and solver.
"""

import streamlit as st
from constants import DEFAULT_PARAMS
from data_loader import parse_input_excel, get_sample_workbook
from preview_tables import show_preview
from ui_components import render_header, step_indicator, metric_row, results_tabs
from solver_cp_sat import solve_schedule
from postprocessing import gantt_figure_from_schedule, inventory_df_from_results
import io

st.set_page_config(page_title="Polymer Production Scheduler", layout="wide", initial_sidebar_state="collapsed")

# session init
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'params' not in st.session_state:
    st.session_state.params = DEFAULT_PARAMS.copy()
if 'parsed_inputs' not in st.session_state:
    st.session_state.parsed_inputs = None
if 'solution' not in st.session_state:
    st.session_state.solution = None

render_header()
step_indicator(st.session_state.step)

# STEP 1: Upload
if st.session_state.step == 1:
    col1, col2 = st.columns([3,1])
    with col1:
        uploaded = st.file_uploader("Upload Excel file (Plant, Inventory, Demand)", type=["xlsx"])
        if uploaded:
            st.session_state.uploaded_file = uploaded.read()
            st.success("File uploaded")
            st.session_state.step = 2
            st.experimental_rerun()
    with col2:
        sample = get_sample_workbook()
        if sample:
            st.download_button("Download template", data=sample, file_name="polymer_production_template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# STEP 2: Configure & Preview
elif st.session_state.step == 2:
    try:
        excel_bytes = st.session_state.uploaded_file
        inputs = parse_input_excel(excel_bytes, buffer_days=st.session_state.params["buffer_days"])
        # attach allowed_lines into inputs (data_loader returns via parse_input_excel)
        inputs["allowed_lines"] = inputs.get("allowed_lines") if inputs.get("allowed_lines") else inputs.get("allowed_lines", {})
        st.session_state.parsed_inputs = inputs
        st.header("Configure Optimization")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.params["time_limit_min"] = st.number_input("Time limit (min)", min_value=1, max_value=120, value=st.session_state.params["time_limit_min"])
            st.session_state.params["buffer_days"] = st.number_input("Buffer days", min_value=0, max_value=14, value=st.session_state.params["buffer_days"])
        with col2:
            st.session_state.params["stockout_penalty"] = st.number_input("Stockout penalty", min_value=1, value=st.session_state.params["stockout_penalty"])
            st.session_state.params["transition_penalty"] = st.number_input("Transition penalty", min_value=0, value=st.session_state.params["transition_penalty"])
        st.markdown("---")
        st.subheader("Data Preview")
        show_preview(inputs["plant_df"], inputs["inventory_df"], inputs["demand_df"])
        st.markdown("---")
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("← Back"):
                st.session_state.step = 1
                st.experimental_rerun()
        with col2:
            if st.button("Run Optimization ▶️"):
                st.session_state.step = 3
                st.experimental_rerun()
    except Exception as e:
        st.error(f"Error parsing workbook: {e}")
        if st.button("Back"):
            st.session_state.step = 1
            st.experimental_rerun()

# STEP 3: Run solver & show results
elif st.session_state.step == 3:
    if st.session_state.parsed_inputs is None:
        st.error("No parsed inputs available. Please re-upload.")
        if st.button("Back to Upload"):
            st.session_state.step = 1
            st.experimental_rerun()
    else:
        inputs = st.session_state.parsed_inputs
        params = st.session_state.params
        st.markdown("### 🔧 Running optimization")
        progress = st.progress(0)
        status_text = st.empty()
        try:
            status_text.info("Building & solving model...")
            progress.progress(10)
            # Microprogress callback (ignored for now)
            def on_progress(pct, msg):
                try:
                    progress.progress(min(100, max(0, pct)))
                    status_text.info(msg)
                except Exception:
                    pass
            # run solver (this may take time)
            result = solve_schedule(inputs, params, on_progress=on_progress)
            st.session_state.solution = result
            progress.progress(100)
            status_text.success("Solver finished")
            # prepare visuals
            if result.get("final"):
                final = result["final"]
                production_df = []
                for g, mapping in final["production"].items():
                    for date, val in mapping.items():
                        production_df.append({"Grade": g, "Date": date, "Produced": val})
                import pandas as pd
                production_df = pd.DataFrame(production_df)
                inventory_df = inventory_df_from_results(final.get("inventory", {}))
                gantt_fig = gantt_figure_from_schedule(final.get("schedule", {}))
                # KPIs
                objective = final.get("objective", "N/A")
                total_transitions = sum(final.get("schedule", {}).get(l, {}).get(list(inputs["formatted_dates"])[0], 0) for l in inputs["lines"]) if False else sum(0 for _ in [])
                # Show KPI cards (simple)
                metric_row({"Objective": f"{objective}", "Producing Grades": str(len(final["production"].keys())), "Horizon days": str(inputs["num_days"])})
                results_tabs(production_df, inventory_df, gantt_fig)
            else:
                st.warning("No feasible solution found.")
                if "solutions" in result and result["solutions"]:
                    st.write("Intermediate solutions captured.")
        except Exception as e:
            st.error(f"Solver error: {e}")
            import traceback
            st.code(traceback.format_exc())
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Configure"):
                st.session_state.step = 2
                st.experimental_rerun()
        with col2:
            if st.button("New Upload"):
                st.session_state.step = 1
                st.session_state.uploaded_file = None
                st.session_state.parsed_inputs = None
                st.experimental_rerun()
