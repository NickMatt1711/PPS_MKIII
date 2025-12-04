"""
ui_components.py
Material 3 Light Theme - Enhanced Desktop UX with Upload Page Improvements
"""

import streamlit as st
from pathlib import Path

# -------------------------------
# CSS - Material 3 Light Theme (Enhanced for Desktop)
# -------------------------------
CUSTOM_CSS = """
/* =============================
CORPORATE LIGHT THEME CSS - ENHANCED DESKTOP
============================= */
:root {
  --md-sys-color-primary: #0A74DA;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #E6F0FA;
  --md-sys-color-on-primary-container: #0A2E5C;

  --md-sys-color-secondary: #5A6F8E;
  --md-sys-color-on-secondary: #FFFFFF;
  --md-sys-color-secondary-container: #F0F4F8;
  --md-sys-color-on-secondary-container: #1D2939;

  --md-sys-color-surface: #FFFFFF;
  --md-sys-color-on-surface: #212529;
  --md-sys-color-surface-variant: #F1F3F5;
  --md-sys-color-on-surface-variant: #495057;

  --md-sys-color-background: #F9FAFB;
  --md-sys-color-on-background: #212529;

  --md-sys-color-outline: #CED4DA;
  --md-sys-color-outline-variant: #DEE2E6;

  --md-sys-color-success: #28A745;
  --md-sys-color-on-success: #FFFFFF;
  --md-sys-color-success-container: #DFF6E3;

  --md-sys-color-warning: #FFC107;
  --md-sys-color-on-warning: #212529;
  --md-sys-color-warning-container: #FFF3CD;

  --md-sys-color-error: #DC3545;
  --md-sys-color-on-error: #FFFFFF;
  --md-sys-color-error-container: #F8D7DA;

  --md-shape-corner-small: 8px;
  --md-shape-corner-medium: 12px;
  --md-shape-corner-large: 16px;
}

/* Global Styles */
.stApp, html, body {
  background: var(--md-sys-color-background) !important;
  font-family: 'Roboto', 'Segoe UI', system-ui, sans-serif;
  color: var(--md-sys-color-on-background);
}

/* =============================
BUTTONS - Enhanced Hierarchy
============================= */
.stButton>button[kind="primary"],
.stButton>button:not([kind]),
button[data-testid="stDownloadButton"] {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4) !important;
  color: var(--md-sys-color-on-primary) !important;
  border-radius: var(--md-shape-corner-large) !important;
  padding: 0.75rem 1.5rem !important;
  font-weight: 500 !important;
  font-size: 0.875rem !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
  text-transform: none !important;
  transition: all 0.2s ease !important;
  border: none !important;
}

.stButton>button[kind="primary"]:hover,
.stButton>button:not([kind]):hover,
button[data-testid="stDownloadButton"]:hover {
  background: linear-gradient(135deg, #085BB5, #3D8CD9) !important;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
  transform: translateY(-1px);
}

.stButton>button[kind="secondary"] {
  background: var(--md-sys-color-surface) !important;
  color: var(--md-sys-color-primary) !important;
  border: 2px solid var(--md-sys-color-primary) !important;
  border-radius: var(--md-shape-corner-large) !important;
  padding: 0.75rem 1.5rem !important;
  font-weight: 500 !important;
  font-size: 0.875rem !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
  transition: all 0.2s ease !important;
}

.stButton>button[kind="secondary"]:hover {
  background: var(--md-sys-color-primary-container) !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
}

.stButton>button:focus-visible,
button[data-testid="stDownloadButton"]:focus-visible {
  outline: 3px solid #4BA3F4 !important;
  outline-offset: 2px !important;
}

.stButton>button:disabled {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
}

/* =============================
Header - Enhanced
============================= */
.app-header {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4);
  color: var(--md-sys-color-on-primary) !important;
  padding: 1.5rem 2rem;
  border-radius: var(--md-shape-corner-large);
  text-align: center;
  box-shadow: 0 4px 12px rgba(10, 116, 218, 0.25);
  margin-bottom: 2rem;
}

.app-header h1 {
  margin: 0;
  font-size: 1.875rem;
  font-weight: 500;
  letter-spacing: -0.5px;
}

.app-header p {
  opacity: 0.95;
  font-size: 1rem;
  margin-top: 0.5rem;
}

/* =============================
Cards - Enhanced
============================= */
.card, .metric-card, .stTabs {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

.card-header {
  font-size: 1.25rem;
  font-weight: 500;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

/* =============================
UPLOAD PAGE - Enhanced Visual Design
============================= */
.upload-section-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #212529;
}

/* Enhanced upload zone */
.upload-zone-enhanced {
    border: 3px dashed #0A74DA;
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
    transition: all 0.3s ease;
    cursor: pointer;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}

.upload-zone-enhanced::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(10, 116, 218, 0.1) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.upload-zone-enhanced:hover {
    background: linear-gradient(135deg, #E0F2FE 0%, #BFDBFE 100%);
    border-color: #085BB5;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(10, 116, 218, 0.15);
}

.upload-zone-enhanced:hover::before {
    opacity: 1;
}

.upload-icon-large {
    font-size: 4rem;
    margin-bottom: 1rem;
    animation: float 3s ease-in-out infinite;
    display: inline-block;
}

.upload-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #0A74DA;
    margin-bottom: 0.5rem;
}

.upload-subtitle {
    font-size: 0.95rem;
    color: #606266;
    margin-bottom: 1.25rem;
}

.upload-or-divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 1.5rem 0;
}

.upload-or-divider::before,
.upload-or-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, #CED4DA, transparent);
}

.upload-or-text {
    color: #909399;
    font-size: 0.875rem;
    font-weight: 500;
}

.upload-specs {
    font-size: 0.75rem;
    color: #909399;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(10, 116, 218, 0.1);
}

.browse-button-custom {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #0A74DA, #4BA3F4);
    color: white;
    border-radius: 12px;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    box-shadow: 0 2px 8px rgba(10, 116, 218, 0.3);
}

.browse-button-custom:hover {
    background: linear-gradient(135deg, #085BB5, #3D8CD9);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(10, 116, 218, 0.4);
}

/* Hide default Streamlit uploader styling */
[data-testid="stFileUploader"] {
    display: none;
}

.custom-file-uploader-wrapper [data-testid="stFileUploader"] {
    display: block;
}

/* Download section */
.download-section {
    margin-top: 2rem;
    padding: 1.5rem;
    background: var(--md-sys-color-surface);
    border-radius: var(--md-shape-corner-medium);
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border: 1px solid var(--md-sys-color-outline-variant);
}

.download-section h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #212529;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Quick Start - Connected Steps */
.quick-start-steps-connected {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-top: 1.5rem;
    position: relative;
}

/* Vertical connecting line */
.quick-start-steps-connected::before {
    content: '';
    position: absolute;
    left: 17px;
    top: 40px;
    bottom: 40px;
    width: 3px;
    background: linear-gradient(180deg, 
        #28A745 0%, 
        #28A745 25%, 
        #5DDC7A 50%, 
        #28A745 75%, 
        #28A745 100%);
    border-radius: 2px;
    z-index: 0;
}

.step-item-connected {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 0.75rem 0;
    position: relative;
    z-index: 1;
    transition: all 0.2s ease;
}

.step-item-connected:hover {
    transform: translateX(4px);
}

.step-item-connected:hover .step-number-connected {
    transform: scale(1.15);
    box-shadow: 0 4px 16px rgba(40, 167, 69, 0.5);
}

.step-number-connected {
    width: 36px;
    height: 36px;
    min-width: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #28A745, #5DDC7A);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1rem;
    box-shadow: 0 3px 8px rgba(40, 167, 69, 0.35);
    transition: all 0.3s ease;
    position: relative;
    z-index: 2;
    border: 3px solid #F0FDF4;
}

.step-content-connected {
    flex: 1;
    padding-top: 0.25rem;
}

.step-content-connected strong {
    font-size: 1rem;
    color: #212529;
    display: block;
    margin-bottom: 0.35rem;
    font-weight: 600;
}

.step-content-connected span {
    font-size: 0.875rem;
    color: #606266;
    line-height: 1.5;
    display: block;
}

/* =============================
Alerts - Enhanced
============================= */
div[data-testid="stAlert"] {
  border-radius: var(--md-sys-color-medium);
  padding: 1rem 1.5rem;
  margin: 1rem 0;
  border-left: 4px solid;
}

.alert-success { 
  background: var(--md-sys-color-success-container); 
  color: var(--md-sys-color-on-success);
  border-left-color: var(--md-sys-color-success);
}

.alert-info { 
  background: var(--md-sys-color-primary-container); 
  color: var(--md-sys-color-on-primary-container);
  border-left-color: var(--md-sys-color-primary);
}

.alert-warning { 
  background: var(--md-sys-color-warning-container); 
  color: var(--md-sys-color-on-warning);
  border-left-color: var(--md-sys-color-warning);
}

.alert-error { 
  background: var(--md-sys-color-error-container); 
  color: var(--md-sys-color-on-error);
  border-left-color: var(--md-sys-color-error);
}

/* =============================
Stage Progress - Enhanced with Animation
============================= */
.stage-container {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-sys-color-medium);
  padding: 2rem 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stage-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 1rem;
}

.stage-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  min-width: 80px;
  position: relative;
  z-index: 2;
}

.stage-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  border: 3px solid var(--md-sys-color-outline-variant);
  background: var(--md-sys-color-surface);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stage-circle:not(.active):not(.completed) {
  opacity: 0.4;
  border-color: var(--md-sys-color-outline);
}

.stage-circle.active {
  transform: scale(1.15);
  background: var(--md-sys-color-primary);
  border-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  box-shadow: 0 4px 12px rgba(10, 116, 218, 0.4), 0 0 0 4px rgba(10, 116, 218, 0.1);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { 
    transform: scale(1.15);
    box-shadow: 0 4px 12px rgba(10, 116, 218, 0.4), 0 0 0 4px rgba(10, 116, 218, 0.1);
  }
  50% { 
    transform: scale(1.2);
    box-shadow: 0 6px 16px rgba(10, 116, 218, 0.5), 0 0 0 6px rgba(10, 116, 218, 0.15);
  }
}

.stage-circle.completed {
  background: var(--md-sys-color-success);
  border-color: var(--md-sys-color-success);
  color: var(--md-sys-color-on-success);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.stage-label {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  text-align: center;
}

.stage-label.active {
  color: var(--md-sys-color-on-surface);
  font-weight: 600;
}

.stage-connector {
  flex: 1;
  height: 4px;
  background: var(--md-sys-color-outline-variant);
  margin: 0 0.5rem;
  transition: background-color 0.3s ease;
  border-radius: 2px;
}

.stage-connector.completed {
  background: var(--md-sys-color-success);
}

/* =============================
Tabs - Enhanced
============================= */
.stTabs {
  background: var(--md-sys-color-surface);
  border-radius: var(--md-shape-corner-medium) !important;
  overflow: hidden;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--md-sys-color-surface-variant);
  border-radius: var(--md-shape-corner-medium) !important;
}

.stTabs [role="tab"] {
  flex: 1;
  text-align: center;
  font-weight: 600;
  padding: 0.875rem 1rem;
  border-radius: var(--md-shape-corner-small) !important;
  transition: all 0.2s ease;
  border: none !important;
}

.stTabs [role="tab"]:nth-child(1)[aria-selected="true"] {
  background: linear-gradient(135deg, #0A74DA, #4BA3F4) !important;
  color: #FFFFFF !important;
  box-shadow: 0 2px 8px rgba(10, 116, 218, 0.3);
}

.stTabs [role="tab"]:nth-child(2)[aria-selected="true"] {
  background: linear-gradient(135deg, #28A745, #5DDC7A) !important;
  color: #FFFFFF !important;
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.stTabs [role="tab"]:nth-child(3)[aria-selected="true"] {
  background: linear-gradient(135deg, #FFC107, #FFD76A) !important;
  color: #212529 !important;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
}

.stTabs [role="tab"]:nth-child(4)[aria-selected="true"] {
  background: linear-gradient(135deg, #DC3545, #F08080) !important;
  color: #FFFFFF !important;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.stTabs [role="tab"]:not([aria-selected="true"]) {
  background: var(--md-sys-color-surface) !important;
  color: var(--md-sys-color-on-surface-variant) !important;
}

.stTabs [role="tab"]:not([aria-selected="true"]):hover {
  background: var(--md-sys-color-surface-variant) !important;
}

/* =============================
Metric Cards - Enhanced
============================= */
.metric-card {
  border-radius: var(--md-shape-corner-medium) !important;
  padding: 1.75rem 1.5rem !important;
  text-align: center !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
  margin-bottom: 1rem !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  min-height: 140px !important;
  transition: all 0.2s ease !important;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15) !important;
}

.metric-card-blue {
  background: linear-gradient(135deg, #E6F0FA, #BBD7F5) !important;
}

.metric-card-green {
  background: linear-gradient(135deg, #DFF6E3, #AEE8C1) !important;
}

.metric-card-yellow {
  background: linear-gradient(135deg, #FFF3CD, #FFE29A) !important;
}

.metric-card-red {
  background: linear-gradient(135deg, #F8D7DA, #F1A2A9) !important;
}

.metric-label {
  font-size: 0.875rem !important;
  color: #495057 !important;
  font-weight: 600 !important;
  margin-bottom: 0.75rem !important;
  text-align: center !important;
  width: 100% !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 2.25rem !important;
  font-weight: 700 !important;
  color: #212529 !important;
  line-height: 1 !important;
  text-align: center !important;
  width: 100% !important;
}

/* =============================
Loading States - Enhanced
============================= */
.spinner {
  width: 48px;
  height: 48px;
  border: 5px solid #E0E0E0;
  border-top: 5px solid #0A74DA;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 1.5rem auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.optimization-container {
  text-align: center;
  margin: 2rem auto;
  padding: 2rem;
}

.optimization-text {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1rem;
  color: var(--md-sys-color-on-surface);
}

.optimization-subtext {
  font-size: 1rem;
  color: var(--md-sys-color-on-surface-variant);
  margin-top: 0.5rem;
}

/* =============================
Error States - Enhanced
============================= */
.error-container {
  text-align: center;
  padding: 3rem 2rem;
  background: var(--md-sys-color-error-container);
  border-radius: var(--md-shape-corner-medium);
  margin: 2rem 0;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-container h3 {
  color: var(--md-sys-color-error);
  margin-bottom: 0.5rem;
}

.error-container p {
  color: var(--md-sys-color-on-surface-variant);
  font-size: 1rem;
}

/* =============================
Section Divider
============================= */
.section-divider {
  height: 1px;
  background: var(--md-sys-color-outline-variant);
  margin: 2rem 0;
}

/* =============================
Data Tables Enhancement
============================= */
.dataframe-container {
  border-radius: var(--md-shape-corner-medium);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* =============================
Constraint Details Table
============================= */
.constraint-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.constraint-table th {
  background: var(--md-sys-color-primary-container);
  color: var(--md-sys-color-on-primary-container);
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
}

.constraint-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  font-size: 0.875rem;
}

.constraint-table tr:hover {
  background: var(--md-sys-color-surface-variant);
}

.constraint-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.constraint-badge.hard {
  background: #F8D7DA;
  color: #721C24;
}

.constraint-badge.soft {
  background: #FFF3CD;
  color: #856404;
}

/* =============================
FILE UPLOADER - Enhanced Native Styling
============================= */

/* Style the dropzone to look like our design */
[data-testid="stFileUploaderDropzone"] {
    border: 3px dashed #0A74DA !important;
    background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%) !important;
    border-radius: 16px !important;
    padding: 3rem 2rem !important;
    transition: all 0.3s ease !important;
    min-height: 240px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    background: linear-gradient(135deg, #E0F2FE 0%, #BFDBFE 100%) !important;
    border-color: #085BB5 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(10, 116, 218, 0.15) !important;
}

/* Style the icon */
[data-testid="stFileUploaderDropzone"] svg {
    width: 4rem !important;
    height: 4rem !important;
    color: #0A74DA !important;
    animation: float 3s ease-in-out infinite !important;
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

/* Hide/restyle the default text */
[data-testid="stFileUploaderDropzoneInstructions"] > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 0.5rem !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: #0A74DA !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] > div > span:last-child {
    font-size: 0.95rem !important;
    color: #606266 !important;
}

/* Style the browse button */
[data-testid="stFileUploaderDropzone"] button {
    margin-top: 1rem !important;
    background: linear-gradient(135deg, #0A74DA, #4BA3F4) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    box-shadow: 0 2px 8px rgba(10, 116, 218, 0.3) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    background: linear-gradient(135deg, #085BB5, #3D8CD9) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(10, 116, 218, 0.4) !important;
}

/* Add file specs below uploader */
[data-testid="stFileUploader"]::after {
    content: "📌 Supported Format: .XLSX • Maximum Size: 200MB per file";
    display: block;
    text-align: center;
    font-size: 0.75rem;
    color: #909399;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(10, 116, 218, 0.1);
}

"""

# -------------------------------
# APPLY CSS
# -------------------------------
def apply_custom_css():
    """Inject Material 3 corporate theme with enhanced UX."""
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


# -------------------------------
# HEADER
# -------------------------------
def render_header(title: str, subtitle: str = ""):
    """Render corporate app header with enhanced styling."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="app-header"><h1>{title}</h1>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


# -------------------------------
# STAGE PROGRESS (4 stages)
# -------------------------------
def render_stage_progress(current_stage: int):
    """Render 4-stage progress indicator with proper numbering."""
    stages = [
        ("📤", "Upload"),
        ("🛠️", "Configure"),
        ("⚡", "Optimizing"),
        ("📊", "Results")
    ]
    
    total = len(stages)
    current_stage = max(0, min(current_stage, total - 1))
    
    html = '<div class="stage-row">'

    for idx, (icon, label) in enumerate(stages):
        status = "inactive"
        display_icon = icon
        
        if idx < current_stage:
            status = "completed"
            display_icon = "✓"
        elif idx == current_stage:
            status = "active"

        html += f'<div class="stage-step">'
        html += f'<div class="stage-circle {status}">{display_icon}</div>'
        html += f'<div class="stage-label {"active" if idx == current_stage else ""}">{label}</div>'
        html += '</div>'

        if idx < total - 1:
            connector_class = "completed" if idx < current_stage else ""
            html += f'<div class="stage-connector {connector_class}"></div>'

    html += '</div>'
    st.markdown(f'<div class="stage-container">{html}</div>', unsafe_allow_html=True)


# -------------------------------
# CARD
# -------------------------------
def render_card(title: str, icon: str = ""):
    """Render card container with optional icon."""
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        f'<div class="card"><div class="card-header">{icon_html}{title}</div>',
        unsafe_allow_html=True
    )

def close_card():
    """Close card container."""
    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------
# METRIC CARD (Enhanced with hover)
# -------------------------------
def render_metric_card(label: str, value: str, col, card_index: int = 0):
    """Render a metric card with gradient background and hover effect."""
    gradient_classes = [
        'metric-card-blue',
        'metric-card-green', 
        'metric-card-yellow',
        'metric-card-red'
    ]
    card_class = gradient_classes[card_index % 4]
    
    with col:
        st.markdown(
            f'''<div class="metric-card {card_class}">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>''',
            unsafe_allow_html=True
        )


# -------------------------------
# ALERT
# -------------------------------
def render_alert(message: str, alert_type: str = "info"):
    """Render styled alert with icon."""
    icons = {
        "success": "✓",
        "info": "ℹ",
        "warning": "⚠",
        "error": "✖"
    }
    st.markdown(
        f'<div class="alert alert-{alert_type}">'
        f'<strong>{icons.get(alert_type, "ℹ")}</strong> '
        f'<span>{message}</span></div>',
        unsafe_allow_html=True
    )


# -------------------------------
# ERROR STATE
# -------------------------------
def render_error_state(error_type: str, message: str):
    """Render enhanced error state with icon."""
    st.markdown(f"""
        <div class="error-container">
            <div class="error-icon">❌</div>
            <h3>{error_type}</h3>
            <p>{message}</p>
        </div>
    """, unsafe_allow_html=True)


# -------------------------------
# SECTION DIVIDER
# -------------------------------
def render_section_divider():
    """Render section divider line."""
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# -------------------------------
# DOWNLOAD TEMPLATE
# -------------------------------
def render_download_template_button():
    """Render download template button."""
    try:
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        if template_path.exists():
            with open(template_path, "rb") as f:
                template_data = f.read()
            st.download_button(
                label="📥 Download Template",
                data=template_data,
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error("Template file not found")
    except Exception as e:
        st.error(f"Template file not found: {e}")
