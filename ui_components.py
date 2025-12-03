def render_upload_stage():
    """Stage 0: File upload with three colored cards in columns"""
    render_header(f"{APP_ICON} {APP_TITLE}", "Multi-Plant Optimization with Shutdown Management")
    render_stage_progress(STAGE_MAP.get(STAGE_UPLOAD, 0))

    col1, col2, col3 = st.columns(3)

    # Column 1: Quick Start Guide (Blue card)
    with col1:
        st.markdown(
            """
            <div class="upload-card card-blue">
                <h2>🚀 Quick Start Guide</h2>
                <div class="upload-card-content">
                    1️⃣ **Download Template** → Get the Excel structure<br><br>
                    2️⃣ **Fill Data** → Complete Plant, Inventory, Demand, and Transition sheets<br><br>
                    3️⃣ **Upload File** → Validate your data<br><br>
                    4️⃣ **Preview & Configure** → Check sheets and set optimization parameters<br><br>
                    5️⃣ **Run Optimization** → Generate schedule and view results
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Column 2: Uploader (Green card)
    with col2:
        st.markdown(
            """
            <div class="upload-card card-green">
                <h2>📤 Upload Production Data</h2>
                <div class="upload-card-content">
            """,
            unsafe_allow_html=True
        )
        
        uploaded_file = st.file_uploader(
            "Choose an Excel file", 
            type=ALLOWED_EXTENSIONS, 
            help="Upload an Excel file with Plant, Inventory, Demand, and Transition sheets"
        )
        
        if uploaded_file is None:
            st.markdown(
                """
                <div class="drop-zone-hint">
                    <div class="drop-zone-icon">📁</div>
                    <div class="drop-zone-title">Drag & Drop File Here</div>
                    <div class="drop-zone-subtitle">Limit 200MB • XLSX Format</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        if uploaded_file is not None:
            st.session_state[SS_UPLOADED_FILE] = uploaded_file
            render_alert("File uploaded successfully! Processing...", "success")

            try:
                file_buffer = io.BytesIO(uploaded_file.read())
                loader = ExcelDataLoader(file_buffer)
                success, data, errors, warnings = loader.load_and_validate()

                if success:
                    st.session_state[SS_EXCEL_DATA] = data
                    render_alert("File validated successfully!", "success")
                    for warn in warnings:
                        render_alert(warn, "warning")
                    st.session_state[SS_STAGE] = STAGE_PREVIEW
                    st.rerun()
                else:
                    for err in errors:
                        render_alert(err, "error")
                    for warn in warnings:
                        render_alert(warn, "warning")
            except Exception as e:
                render_error_state("Upload Failed", f"Failed to read uploaded file: {e}")

    # Column 3: Download Template (Yellow card)
    with col3:
        st.markdown(
            """
            <div class="upload-card card-yellow">
                <h2>📥 Download Template</h2>
                <div class="upload-card-content">
            """,
            unsafe_allow_html=True
        )
        
        render_download_template_button()
        
        st.markdown("---")
        st.markdown("**Template includes:**")
        st.markdown("""
        - Plant configuration
        - Inventory management  
        - Demand forecasting
        - Transition matrices
        - Pre-filled examples
        """)
        
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Required sheets info
    st.markdown("---")
    st.markdown("### 📋 Required Excel Sheets")
    
    cols = st.columns(4)
    with cols[0]:
        st.markdown("**Plant Sheet**")
        st.markdown("Plant configuration, capacities, shutdown schedules")
    with cols[1]:
        st.markdown("**Inventory Sheet**")
        st.markdown("Opening stock, safety stock, run constraints")
    with cols[2]:
        st.markdown("**Demand Sheet**")
        st.markdown("Daily demand for each product grade")
    with cols[3]:
        st.markdown("**Transition Sheet**")
        st.markdown("Allowed grade changeovers between products")

    # Variable and Constraint Details
    with st.expander("📄 Variable and Constraint Details", expanded=True):
        tab1, tab2, tab3, tab4 = st.tabs(["Plant Sheet", "Inventory Sheet", "Demand Sheet", "Transition Sheets"])
        
        with tab1:
            st.markdown("""
            - **Plant**: Plant name  
            - **Capacity per day**: Max production per day  
            - **Material Running**: Current grade running  
            - **Expected Run Days**: Minimum run days before changeover  
            - **Shutdown Start/End Date**: Planned downtime  
            - **Pre-Shutdown Grade / Restart Grade**: Grade before and after shutdown  
            """)
        
        with tab2:
            st.markdown("""
            - **Grade Name**: Product grade  
            - **Opening Inventory**: Current stock  
            - **Min. Closing Inventory**: Minimum stock at horizon end  
            - **Min./Max Inventory**: Safety stock limits  
            - **Min./Max Run Days**: Consecutive run constraints  
            - **Force Start Date**: Mandatory start date for a grade  
            - **Lines**: Plants where grade can run  
            - **Rerun Allowed**: Yes/No for repeating grade  
            """)
        
        with tab3:
            st.markdown("""
            - **Date**: Planning horizon  
            - **Grade Columns**: Daily demand quantity for each grade  
            """)
        
        with tab4:
            st.markdown("""
            - Allowed grade changes per plant from grade in Row to grade in Column (**Yes/No**)   
            """)
