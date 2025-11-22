"""
Data preview components for displaying Excel sheets
"""

import streamlit as st
import pandas as pd
from typing import Dict


def format_date_columns(df: pd.DataFrame, date_col_indices: list) -> pd.DataFrame:
    """Format datetime columns to readable date strings"""
    df_copy = df.copy()
    for idx in date_col_indices:
        if idx < len(df_copy.columns):
            col = df_copy.columns[idx]
            if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
                df_copy[col] = df_copy[col].dt.strftime('%d-%b-%y')
    return df_copy


def render_sheet_preview(sheet_name: str, df: pd.DataFrame, icon: str = "📋"):
    """Render a single sheet preview in an expander"""
    
    # Format dates based on sheet type
    if sheet_name == 'Plant':
        df_display = format_date_columns(df, [4, 5])  # Shutdown dates
    elif sheet_name == 'Inventory':
        df_display = format_date_columns(df, [7])  # Force start date
    elif sheet_name == 'Demand':
        df_display = format_date_columns(df, [0])  # Date column
    else:
        df_display = df.copy()
    
    with st.expander(f"{icon} **{sheet_name}** ({len(df)} rows × {len(df.columns)} columns)", expanded=False):
        st.dataframe(df_display, use_container_width=True, height=300)
        
        # Show basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            missing = df.isna().sum().sum()
            st.metric("Missing Values", missing)


def render_all_sheets(excel_data: Dict[str, pd.DataFrame]):
    """Render preview of all sheets"""
    
    st.markdown("### 📊 Data Preview")
    st.markdown("Review your uploaded data before running the optimization.")
    
    # Required sheets
    st.markdown("#### Required Sheets")
    
    for sheet_name in ['Plant', 'Inventory', 'Demand']:
        if sheet_name in excel_data:
            icon_map = {
                'Plant': '🏭',
                'Inventory': '📦',
                'Demand': '📈'
            }
            render_sheet_preview(sheet_name, excel_data[sheet_name], icon_map[sheet_name])
    
    # Transition sheets
    transition_sheets = [k for k in excel_data.keys() if k.startswith('Transition_')]
    if transition_sheets:
        st.markdown("#### Transition Matrices")
        for sheet_name in transition_sheets:
            render_sheet_preview(sheet_name, excel_data[sheet_name], "🔄")


def render_data_summary(excel_data: Dict[str, pd.DataFrame]):
    """Render summary statistics of the data"""
    
    st.markdown("### 📋 Data Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Count plants
    if 'Plant' in excel_data:
        num_plants = len(excel_data['Plant'])
        with col1:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #E8EEFF 0%, #D4DFFF 100%); 
                            padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 0.875rem; color: #606266;">Plants</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: #5E7CE2;">{num_plants}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Count grades
    if 'Inventory' in excel_data:
        num_grades = excel_data['Inventory']['Grade Name'].nunique()
        with col2:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #F0F9EB 0%, #E1F3D8 100%); 
                            padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 0.875rem; color: #606266;">Grades</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: #67C23A;">{num_grades}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Count demand days
    if 'Demand' in excel_data:
        num_days = len(excel_data['Demand'])
        with col3:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #FDF6EC 0%, #F9ECD8 100%); 
                            padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 0.875rem; color: #606266;">Demand Days</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: #E6A23C;">{num_days}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Count transition matrices
    transition_count = len([k for k in excel_data.keys() if k.startswith('Transition_')])
    with col4:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FEF0F0 0%, #FAE1E1 100%); 
                        padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.875rem; color: #606266;">Transition Rules</div>
                <div style="font-size: 1.75rem; font-weight: 700; color: #F56C6C;">{transition_count}</div>
            </div>
        """, unsafe_allow_html=True)


def render_validation_messages(errors: list, warnings: list):
    """Render validation errors and warnings"""
    
    if errors:
        st.markdown("### ❌ Validation Errors")
        for error in errors:
            st.markdown(f"""
                <div class="alert alert-error">
                    <span style="font-size: 1.25rem; font-weight: bold;">✕</span>
                    <span>{error}</span>
                </div>
            """, unsafe_allow_html=True)
    
    if warnings:
        st.markdown("### ⚠️ Warnings")
        for warning in warnings:
            st.markdown(f"""
                <div class="alert alert-warning">
                    <span style="font-size: 1.25rem; font-weight: bold;">⚠</span>
                    <span>{warning}</span>
                </div>
            """, unsafe_allow_html=True)
