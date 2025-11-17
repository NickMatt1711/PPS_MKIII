# app.py
import streamlit as st
import io
import pandas as pd

from ui_components import inject_test1_css, header, footer
from preview_tables import show_core_previews
from data_loader import read_workbook_bytes, load_core_sheets, find_transition_sheets
from solver_cp_sat import solve
from postprocessing import convert_solver_output_to_display, plot_inventory_chart
from constants import DEFAULT_TIME_LIMIT_MIN, DEFAULT_STOCKOUT_PENALTY, DEFAULT_TRANSITION_PENALTY

st.set_page_config(page_title="Polymer Production Scheduler", layout="wide")
inject_test1_css()
header()

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# STEP 1: Upload
if st.session_state.step == 1:
    col1, col2 = st.columns([4, 1])
    with col1:
        uploaded = st.file_uploader("Choose Excel File", type=['xlsx'])
        if uploaded is not None:
            st.session_state.uploaded_file = uploaded
            st.success("✅ File uploaded")
            st.session_state.step = 2
            st.experimental_rerun()
    with col2:
        try:
            with open("polymer_production_template.xlsx", "rb") as f:
                data = f.read()
            st.download_button("📥 Download Template", data=data, file_name="polymer_production_template.xlsx")
        except Exception:
            st.info("Template download not available in this environment.")

# STEP 2: Preview & Configure
elif st.session_state.step == 2:
    uploaded = st.session_state.uploaded_file
    if uploaded is None:
        st.error("No file uploaded.")
        if st.button("← Return to start"):
            st.session_state.step = 1
            st.experimental_rerun()
    else:
        uploaded.seek(0)
        xls = read_workbook_bytes(io.BytesIO(uploaded.read()))
        plant_df, inventory_df, demand_df, transition_map = show_core_previews(xls)
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            time_limit_min = st.number_input("Time limit (minutes)", min_value=1, value=DEFAULT_TIME_LIMIT_MIN)
        with col2:
            stockout_penalty = st.number_input("Stockout penalty", min_value=1, value=DEFAULT_STOCKOUT_PENALTY)
        with col3:
            transition_penalty = st.number_input("Transition penalty", min_value=1, value=DEFAULT_TRANSITION_PENALTY)

        if st.button("🎯 Run Production Optimization"):
            st.session_state.step = 3
            st.session_state.plant_df = plant_df
            st.session_state.inventory_df = inventory_df
            st.session_state.demand_df = demand_df
            st.session_state.transition_map = transition_map
            st.session_state.params = {
                'time_limit_min': time_limit_min,
                'stockout_penalty': stockout_penalty,
                'transition_penalty': transition_penalty
            }
            st.experimental_rerun()

# STEP 3: Solve & Results
elif st.session_state.step == 3:
    plant_df = st.session_state.get('plant_df')
    inventory_df = st.session_state.get('inventory_df')
    demand_df = st.session_state.get('demand_df')
    transition_map = st.session_state.get('transition_map', {})
    params = st.session_state.get('params', {})

    st.markdown("### ⚙️ Preprocessing input for solver")
    # Build instance
    date_col = demand_df.columns[0]
    dates = pd.to_datetime(demand_df[date_col]).dt.date.tolist()
    grades = [c for c in demand_df.columns if c != date_col]
    capacities = {row['Plant']: int(row.get('Capacity per day', 0)) for _, row in plant_df.iterrows()}

    # Inventory / allowed_lines / rerun_allowed / min/max runs
    allowed_lines = {}
    initial_inventory = {}
    max_inventory = {}
    min_closing_inventory = {}
    min_run_days = {}
    max_run_days = {}
    rerun_allowed = {}
    for _, row in inventory_df.iterrows():
        g = row['Grade Name']
        lines_str = row.get('Lines', '')
        if pd.notna(lines_str) and str(lines_str).strip() != '':
            plants_for_row = [x.strip() for x in str(lines_str).split(',')]
        else:
            plants_for_row = list(capacities.keys())
        allowed_lines[g] = plants_for_row
        initial_inventory[g] = int(row.get('Opening Inventory', 0))
        max_inventory[g] = int(row.get('Max. Inventory', 10**9))
        min_closing_inventory[g] = int(row.get('Min. Closing Inventory', 0))
        min_run = int(row.get('Min. Run Days', 1))
        max_run = int(row.get('Max. Run Days', len(dates)))
        rerun_flag = row.get('Rerun allowed', True)
        for p in plants_for_row:
            min_run_days[(g, p)] = min_run
            max_run_days[(g, p)] = max_run
            rerun_allowed[(g, p)] = bool(rerun_flag)

    # demand mapping
    demand = {}
    for i, r in demand_df.iterrows():
        for g in grades:
            demand[(g, i)] = int(r[g]) if pd.notna(r[g]) else 0

    # transition_rules: convert transition_map into per-plant mapping of allowed next grades
    transition_rules = {}
    for sheet_name, df in transition_map.items():
        if df is None:
            continue
        # try to infer plant name from sheet_name (if sheet name includes plant)
        # We'll store under sheet_name as key; solver expects keys matching plant names in capacities,
        # so we will also attempt to map if sheet_name contains a plant
        transition_rules[sheet_name] = {}
        try:
            df2 = df.copy()
            # ensure index and columns are string typed grades
            df2.index = df2.index.astype(str)
            df2.columns = df2.columns.astype(str)
            for from_g in df2.index:
                allowed_list = []
                for to_g in df2.columns:
                    val = df2.loc[from_g, to_g]
                    if pd.isna(val):
                        continue
                    sval = str(val).strip().lower()
                    if sval in ('yes','y','1','true','t','allowed'):
                        allowed_list.append(to_g)
                transition_rules[sheet_name][from_g] = allowed_list
        except Exception:
            continue

    # Map transition_rules to plants: if any sheet_name contains plant name, attach mapping to that plant
    # Fallback: if sheet_name equals plant name or 'Transition_<plant>' patterns, map accordingly
    mapped_rules = {}
    for plant in capacities.keys():
        mapped_rules[plant] = {}
    for sheet_name, mapping in transition_rules.items():
        lowered = sheet_name.lower()
        matched = None
        for plant in capacities.keys():
            if plant.lower() in lowered:
                matched = plant
                break
        if matched:
            mapped_rules[matched] = mapping
        else:
            # If no plant matched, keep as generic under sheet name
            mapped_rules[sheet_name] = mapping

    # shutdown processing -> day indices per plant
    shutdown_day_indices = {}
    for _, row in plant_df.iterrows():
        plant = row['Plant']
        sstart = row.get('Shutdown Start Date', None)
        send = row.get('Shutdown End Date', None)
        indices = set()
        if pd.notna(sstart) and pd.notna(send):
            try:
                sstart_d = pd.to_datetime(sstart).date()
                send_d = pd.to_datetime(send).date()
                for i, d in enumerate(dates):
                    if sstart_d <= d <= send_d:
                        indices.add(i)
            except Exception:
                indices = set()
        shutdown_day_indices[plant] = indices

    instance = {
        'grades': grades,
        'lines': list(capacities.keys()),
        'dates': dates,
        'capacities': capacities,
        'demand': demand,
        'initial_inventory': initial_inventory,
        'max_inventory': max_inventory,
        'min_closing_inventory': min_closing_inventory,
        'min_run_days': min_run_days,
        'max_run_days': max_run_days,
        'allowed_lines': allowed_lines,
        'rerun_allowed': rerun_allowed,
        'transition_rules': mapped_rules,
        'shutdown_day_indices': shutdown_day_indices
    }

    st.markdown("### 🚀 Running CP-SAT solver")
    with st.spinner("Solving..."):
        params_run = {
            'time_limit_min': params.get('time_limit_min', DEFAULT_TIME_LIMIT_MIN),
            'stockout_penalty': params.get('stockout_penalty', DEFAULT_STOCKOUT_PENALTY),
            'transition_penalty': params.get('transition_penalty', DEFAULT_TRANSITION_PENALTY),
            'num_search_workers': 8
        }
        solver_result = solve(instance, params_run)

    st.markdown("### ✅ Solver status")
    st.write(solver_result.get('status', 'No status'))

    if solver_result.get('best'):
        display_result = convert_solver_output_to_display(solver_result, instance)
        st.markdown("### 📈 Key Metrics")
        st.write(f"Objective: {display_result['objective']}")
        # Show example production/inventory plots (first few grades)
        for g in instance['grades'][:3]:
            dates_label = display_result['formatted_dates']
            inv_series = [display_result['inventory'].get(g, {}).get(d, 0) for d in dates_label]
            fig = plot_inventory_chart(g, dates_label, inv_series)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No feasible solution found. Check data and constraints.")

    footer()
