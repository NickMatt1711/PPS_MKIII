def render_stage_progress(current_stage: int):
    # Define stages and labels
    stages = [
        ("1", "Upload"),
        ("2", "Preview & Configure"),
        ("3", "Results")
    ]
    
    total = len(stages)
    
    # Ensuring current_stage is within valid range
    current_stage = max(0, min(current_stage, total))  # current_stage should be <= len(stages)

    blocks = []
    connectors = []

    # Create each stage's block and connector
    for idx, (num, label) in enumerate(stages):
        if idx < current_stage:  # Stage is completed
            status = "completed"
            icon = "✓"  # Show tick for completed stages
        elif idx == current_stage:  # Current active stage
            status = "active"
            icon = num  # Show stage number for active stage
        else:  # Future stages
            status = "inactive"
            icon = num  # Show stage number for inactive stages

        blocks.append(
            f"""
            <div class="stage-step">
                <div class="stage-circle {status}">{icon}</div>
                <div class="stage-label {'active' if idx == current_stage else ''}">
                    {label}
                </div>
            </div>
            """
        )

        # Add connectors between stages
        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            connectors.append(f'<div class="stage-connector {connector_class}"></div>')

    # Combine blocks and connectors into HTML
    html = ""
    for i, block in enumerate(blocks):
        html += block
        if i < len(connectors):
            html += connectors[i]

    # Render the entire container for stage progress
    st.markdown(
        f"""
        <div class="stage-container">
            <div class="stage-row">{html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
