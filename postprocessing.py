# postprocessing.py
import pandas as pd

def convert_solver_output_to_display(solver_result, instance):
    """
    Convert solver 'best' to dict matching plotting expectations.
    Returns: dict with keys production, inventory, stockout, is_producing, formatted_dates, objective
    """
    best = solver_result.get('best')
    if not best:
        return None

    grades = instance['grades']
    lines = instance['lines']
    dates = instance['dates']
    formatted_dates = [d.strftime('%d-%b-%y') for d in dates]

    production = {g: {} for g in grades}
    is_producing = {line: {} for line in lines}
    stockout = {g: {} for g in grades}
    inventory = {g: {} for g in grades}

    for (line, d), g in best.get('assign', {}).items():
        date_label = formatted_dates[d]
        is_producing[line][date_label] = g

    for (line, d), entries in best.get('production', {}).items():
        date_label = formatted_dates[d]
        for g, qty in entries.items():
            production[g].setdefault(date_label, 0)
            production[g][date_label] += qty

    for (g, d), inv in best.get('inventory', {}).items():
        if d == 0:
            inventory[g]['initial'] = inv
        elif d <= len(formatted_dates):
            inventory[g][formatted_dates[d-1]] = inv
        else:
            inventory[g]['final'] = inv

    for (g, d), val in best.get('unmet', {}).items():
        date_label = formatted_dates[d]
        stockout[g].setdefault(date_label, 0)
        stockout[g][date_label] += val

    return {
        'production': production,
        'is_producing': is_producing,
        'stockout': stockout,
        'inventory': inventory,
        'formatted_dates': formatted_dates,
        'objective': best.get('objective')
    }

# -----------------------
# PLOTLY FUNCTIONS (PLACEHOLDERS)
# -----------------------
# You MUST paste your exact Plotly chart functions below (copy from your original app.py)
# Replace the placeholder function bodies with verbatim Plotly code so visuals remain unchanged.
#
# Example placeholders follow. Replace them.
def plot_inventory_chart(grade, dates, inventory_series, min_inventory=None, max_inventory=None):
    """
    Placeholder. Replace the body with your original Plotly code.
    """
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=inventory_series, mode='lines+markers', name=f'Inventory - {grade}'))
    fig.update_layout(title=f"Inventory - {grade}", xaxis_title="Date", yaxis_title="Inventory")
    return fig

def plot_production_schedule_plotly(display_result):
    """
    Placeholder for production schedule plotly function.
    Replace with the exact function you use in the current app.py (copy & paste).
    """
    raise NotImplementedError("Paste your production schedule Plotly function here (verbatim).")
