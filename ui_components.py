"""
UI Components Module
====================

Reusable Streamlit components matching test(1).py UI style.
"""

import streamlit as st
from typing import Tuple

import constants


def inject_custom_css() -> None:
    """Inject modern Material Design CSS - matches test(1).py."""
    st.markdown("""
    <style>
        /* Hide sidebar completely */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        .main .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }
        
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Material Design App Bar */
        .app-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 2rem 3rem;
            margin: -3rem -3rem 3rem -3rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 16px;
        }
        
        .app-bar h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        .app-bar p {
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            opacity: 0.95;
            font-weight: 400;
        }
        
        /* Material Cards */
        .material-card {
            background: #F0F2FF;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            padding: 2rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(0, 0, 0, 0.06);
        }
        
        .material-card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }
        
        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            text-align: center;
            color: #212121;
            margin: 0 0 1rem 0;
        }
        
        /* Metrics */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            border-left: 4px solid;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }
        
        .metric-card.primary {
            border-left-color: #667eea;
            background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
        }
        
        .metric-card.success {
            border-left-color: #4caf50;
            background: linear-gradient(135deg, #f1f8f4 0%, #ffffff 100%);
        }
        
        .metric-card.warning {
            border-left-color: #ff9800;
            background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%
