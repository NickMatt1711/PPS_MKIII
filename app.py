"""
app.py
Main Streamlit application for Multi-Plant Optimization (Upload stage UI).
Place ui_components.py in the same folder.
Run: streamlit run app.py
"""

import streamlit as st
import io
from ui_components import (
    apply_custom_css, render_header, render_stage_progress,
    render_section_card, close_section_card, render_alert,
    render_section_divider, render_download_template_button
)

# ---------------------------
# App constants and session keys
# ---------------------------
APP_ICON = "🧪"
APP_TITLE = "Multi-Plant Scheduler"
ALLOWED_EXTENSIONS = ["xlsx", "xls"]

SS_UPLOADED_FILE = "uploaded_file"
SS_EXCEL_DATA = "excel_data"
SS_STAGE = "stage"

STAGE_UPLOAD = 0
STAGE_PREVIEW = 1
STAGE_MAP = {STAGE_UPLOAD: 0, STAGE_PREVIEW: 1}

# ---------------------------
# Placeholder ExcelDataLoader
# Replace with your implementation for real parsing/validation.
# ---------------------------
class ExcelDataLoader:
    def __init__(self, buffer: io.BytesIO):
        self.buffer = buffer

    def load_and_validate(self):
        """
        Minimal placeholder: returns success with empty dict.
        Replace with actual Excel reading and validation logic.
        Returns: (success: bool, data: dict|None, errors: list, warnings: list)
        """
        try:
            # pretend to parse and validate
            data = {"Plant": [], "Inventory": [], "Demand": []}
            return True, data, [], []
        except Exception as e:
            return False, None, [str(e)], []

# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(page_title=APP_TITLE, layout="wide")
apply_custom_css()

# initialize session state defaults
if SS_UPLOADED_FILE not in st.session_state:
    st.session_state[SS_UPLOADED_FILE] = None
if SS_EXCEL_DATA not in st.session_state:
    st.session_state[SS_EXCEL_DATA] = None
if SS_STAGE not in st.session_state:
    st.session_state[SS_STAGE] = STAGE_UPLOAD

# ---------------------------
# Render Upload Stage (three columns, each section fully inside card)
# ---------------------------
def render_upload_stage():
    render_header(f"{APP_ICON} {APP_TITLE}", "Multi-Plant Optimization with Shutdown Management")
    render_stage_progress(STAGE_MAP.get(STAGE_UPLOAD, 0))

    col1, col2, col3 = st.columns([1, 1, 1])

    # Column 1: Upload + Template (both inside same blue card)
    with col1:
        render_section_card("Upload Production Data", "📤", "blue")
        with st.container():
            uploaded_file = st.file_uploader(
                "Choose an Excel file",
                type=ALLOWED_EXTENSIONS,
                help="Upload an Excel file with Plant, Inventory, Demand, and Transition sheets",
                key="file_uploader_main"
            )

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
                        # st.experimental_rerun()  # uncomment if you want immediate rerun after upload
                    else:
                        for err in errors:
                            render_alert(err, "error")
                        for warn in warnings:
                            render_alert(warn, "warning")
                except Exception as e:
                    render_alert(f"Failed to read uploaded file: {e}", "error")

            # Small spacing
            st.write("")
            st.write("Need a template? Download below.")
            render_download_template_button()
        close_section_card()

    # Column 2: Quick Start Guide (green card)
    with col2:
        render_section_card("Quick Start Guide", "✅", "green")
        with st.container():
            st.markdown("""
            1️⃣ **Download Template** → Get the Excel structure  
            2️⃣ **Fill Data** → Complete Plant, Inventory, Demand, and Transition sheets  
            3️⃣ **Upload File** → Validate your data  
            4️⃣ **Preview & Configure** → Check sheets and set optimization parameters  
            5️⃣ **Run Optimization** → Generate schedule and view results  
            """)
        close_section_card()

    # Column 3: Variables & Constraints (yellow card)
    with col3:
        render_section_card("Variables & Constraints Explained", "🔍", "yellow")
        with st.container():
            st.markdown("""
**Your Excel file should contain the following sheets with these exact column headers:**

---

### 1. Plant Sheet
- **Plant**: Plant names (e.g., Plant1, Plant2)  
- **Capacity per day**: Daily production capacity  
- **Material Running**: Currently running material (optional)  
- **Expected Run Days**: Expected run days (optional)  
- **Shutdown Start Date**: Start date of plant shutdown/maintenance (optional)  
- **Shutdown End Date**: End date of plant shutdown/maintenance (optional)

**Shutdown Period Example:**

| Plant  | Capacity | Shutdown Start Date | Shutdown End Date |
|--------|----------|---------------------|-------------------|
| Plant1 | 1500     | 15-Nov-25           | 18-Nov-25         |

During a shutdown period the plant produces zero and the schedule should visually highlight that.

---

### 2. Inventory Sheet
- **Grade Name**: Material grades (can be repeated for multi-plant configurations)  
- **Opening Inventory**: Starting inventory levels (only first occurrence used)  
- **Min. Inventory**: Minimum inventory requirements (only first occurrence used)  
- **Max. Inventory**: Maximum inventory capacity (only first occurrence used)  
- **Min. Run Days**: Minimum consecutive run days (per plant)  
- **Max. Run Days**: Maximum consecutive run days (per plant)  
- **Force Start Date**: Mandatory start dates (per plant, can be different for same grade)  
- **Lines**: Allowed production lines (specify one plant per row for multi-plant grades)  
- **Rerun Allowed**: Whether rerun is allowed (per plant, Yes/No)  
- **Min. Closing Inventory**: Minimum closing inventory (only first occurrence used)

**Multi-Plant Example:**

| Grade Name | Lines  | Force Start Date | Min. Run Days |
|------------|--------|------------------|---------------|
| BOPP       | Plant1 |                  | 5             |
| BOPP       | Plant2 | 01-Dec-24        | 5             |

This allows BOPP to run on both Plant1 and Plant2, but with a forced start on Plant2 on Dec 1.

**Shutdown Period Example:**

| Plant  | Capacity | Shutdown Start Date | Shutdown End Date |
|--------|----------|---------------------|-------------------|
| Plant1 | 1500     | 15-Nov-25           | 18-Nov-25         |

---

### 3. Demand Sheet
- **First column**: Dates  
- **Subsequent columns**: Daily demand for each grade (column names must match grade names)

---

### 4. Transition Sheets (optional)
- Sheet name format: **Transition_[PlantName]** (e.g., `Transition_Plant1`)  
- Row labels: Previous grade  
- Column labels: Next grade  
- Cell values: `"yes"` to indicate allowed transitions
            """)
        close_section_card()

    render_section_divider()

    # Simple navigation row
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        next_disabled = st.session_state.get(SS_UPLOADED_FILE) is None
        if st.button("Next: Preview Data →", disabled=next_disabled, use_container_width=True):
            if st.session_state.get(SS_EXCEL_DATA):
                st.session_state[SS_STAGE] = STAGE_PREVIEW
                st.experimental_rerun()
            else:
                render_alert("Please upload and validate a file first.", "warning")
    # center column reserved for future controls
    with nav_col2:
        st.write("")  # placeholder (could be step controls)
    with nav_col3:
        st.write("")  # placeholder

# ---------------------------
# Main
# ---------------------------
def main():
    render_upload_stage()

if __name__ == "__main__":
    main()
