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
UPLOAD PAGE - STREAMLINED LAYOUT
============================= */
/* Main container */
.upload-page-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Page header */
.upload-page-header {
    text-align: center;
    margin-bottom: 2.5rem;
}

.upload-main-title {
    font-size: 2rem;
    font-weight: 600;
    color: var(--md-sys-color-on-surface);
    margin-bottom: 0.5rem;
}

.upload-subtitle {
    color: var(--md-sys-color-on-surface-variant);
    font-size: 1.125rem;
    line-height: 1.5;
}

/* Main content columns */
.upload-main-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2.5rem;
    margin-bottom: 2.5rem;
}

/* Left column - Upload section */
.upload-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* Upload zone - Clean and simple */
.upload-zone-clean {
    border: 2px dashed var(--md-sys-color-outline);
    border-radius: var(--md-shape-corner-medium);
    padding: 2.5rem 2rem;
    text-align: center;
    background: var(--md-sys-color-surface);
    transition: all 0.2s ease;
    cursor: pointer;
}

.upload-zone-clean:hover {
    border-color: var(--md-sys-color-primary);
    background: var(--md-sys-color-primary-container);
}

.upload-zone-clean.dragover {
    border-color: var(--md-sys-color-success);
    background: var(--md-sys-color-success-container);
}

.upload-icon-large {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: var(--md-sys-color-primary);
}

.upload-zone-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--md-sys-color-on-surface);
    margin-bottom: 0.5rem;
}

.upload-zone-subtitle {
    color: var(--md-sys-color-on-surface-variant);
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
}

.upload-file-types {
    background: var(--md-sys-color-surface-variant);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.875rem;
    color: var(--md-sys-color-on-surface-variant);
    display: inline-block;
}

/* Download section - Simple and clean */
.download-section-clean {
    background: var(--md-sys-color-surface);
    border-radius: var(--md-shape-corner-medium);
    padding: 2rem;
    border: 1px solid var(--md-sys-color-outline-variant);
}

.download-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.download-icon {
    font-size: 1.5rem;
    color: var(--md-sys-color-primary);
}

.download-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--md-sys-color-on-surface);
    margin: 0;
}

.download-description {
    color: var(--md-sys-color-on-surface-variant);
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

/* Right column - Quick Start Guide */
.quick-start-guide {
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    border-radius: var(--md-shape-corner-medium);
    padding: 2rem;
    border: 1px solid var(--md-sys-color-outline-variant);
    height: 100%;
}

.guide-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.guide-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--md-sys-color-on-surface);
    margin: 0;
}

.guide-icon {
    font-size: 1.5rem;
    color: var(--md-sys-color-success);
}

/* Clean step design */
.guide-steps-clean {
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
}

.step-item-clean {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    position: relative;
}

.step-number-clean {
    width: 32px;
    height: 32px;
    min-width: 32px;
    border-radius: 50%;
    background: var(--md-sys-color-surface);
    border: 2px solid var(--md-sys-color-primary);
    color: var(--md-sys-color-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.875rem;
    transition: all 0.2s ease;
}

.step-item-clean:hover .step-number-clean {
    background: var(--md-sys-color-primary);
    color: var(--md-sys-color-on-primary);
    transform: scale(1.1);
}

.step-content-clean {
    flex: 1;
    padding-top: 0.25rem;
}

.step-title-clean {
    font-size: 1rem;
    font-weight: 600;
    color: var(--md-sys-color-on-surface);
    display: block;
    margin-bottom: 0.25rem;
}

.step-description-clean {
    font-size: 0.875rem;
    color: var(--md-sys-color-on-surface-variant);
    line-height: 1.5;
}

/* Connector lines */
.step-item-clean:not(:last-child)::after {
    content: '';
    position: absolute;
    left: 15px;
    top: 34px;
    bottom: -1.75rem;
    width: 2px;
    background: var(--md-sys-color-outline-variant);
}

/* Details expander - Enhanced */
.details-expander {
    margin-top: 2.5rem;
}

.details-table-container {
    overflow-x: auto;
    margin: 1rem 0;
}

.details-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
}

.details-table th {
    background: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
    padding: 0.875rem 1rem;
    text-align: left;
    font-weight: 600;
    border-bottom: 1px solid var(--md-sys-color-outline);
    white-space: nowrap;
}

.details-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--md-sys-color-outline-variant);
    vertical-align: top;
}

.details-table tr:last-child td {
    border-bottom: none;
}

.details-table tr:hover td {
    background: var(--md-sys-color-surface-variant);
}

/* Constraint badges */
.constraint-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1;
}

.badge-hard {
    background: #FEE2E2;
    color: #991B1B;
}

.badge-soft {
    background: #FEF3C7;
    color: #92400E;
}

.badge-none {
    background: #E5E7EB;
    color: #374151;
}

/* Sheet examples */
.sheet-example {
    background: var(--md-sys-color-surface-variant);
    border-radius: var(--md-shape-corner-small);
    padding: 1rem;
    margin-top: 1rem;
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: 0.875rem;
    color: var(--md-sys-color-on-surface-variant);
}

/* File uploader styling */
.stFileUploader > div {
    border: 2px dashed var(--md-sys-color-outline) !important;
    background: var(--md-sys-color-surface) !important;
    border-radius: var(--md-shape-corner-medium) !important;
    padding: 2rem !important;
    transition: all 0.2s ease !important;
}

.stFileUploader > div:hover {
    border-color: var(--md-sys-color-primary) !important;
    background: var(--md-sys-color-primary-container) !important;
}

.stFileUploader > div[data-testid="stFileUploaderDropzone"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 1rem !important;
}

.stFileUploader > div[data-testid="stFileUploaderDropzone"] svg {
    width: 48px !important;
    height: 48px !important;
    color: var(--md-sys-color-primary) !important;
}

.stFileUploader > div[data-testid="stFileUploaderDropzone"]::before {
    content: "📁" !important;
    font-size: 3rem !important;
    margin-bottom: 0.5rem !important;
}

.stFileUploader > div[data-testid="stFileUploaderDropzone"]::after {
    content: "Drag & drop your Excel file here" !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    color: var(--md-sys-color-on-surface) !important;
}

.stFileUploader > div[data-testid="stFileUploaderDropzone"] small {
    color: var(--md-sys-color-on-surface-variant) !important;
    font-size: 0.875rem !important;
    margin-top: 0.5rem !important;
}

/* Status indicators */
.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-radius: var(--md-shape-corner-small);
    font-size: 0.875rem;
    font-weight: 500;
    margin: 0.5rem 0;
}

.status-success {
    background: #D1FAE5;
    color: #065F46;
    border: 1px solid #A7F3D0;
}

.status-warning {
    background: #FEF3C7;
    color: #92400E;
    border: 1px solid #FDE68A;
}

.status-error {
    background: #FEE2E2;
    color: #991B1B;
    border: 1px solid #FECACA;
}

/* File info display */
.file-info-display {
    background: var(--md-sys-color-surface);
    border-radius: var(--md-shape-corner-medium);
    padding: 1.5rem;
    border: 1px solid var(--md-sys-color-outline-variant);
    margin-top: 1rem;
}

.file-info-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.file-info-icon {
    font-size: 1.5rem;
    color: var(--md-sys-color-success);
}

.file-info-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--md-sys-color-on-surface);
    margin: 0;
}

.file-info-details {
    display: flex;
    gap: 1.5rem;
    color: var(--md-sys-color-on-surface-variant);
    font-size: 0.875rem;
}

.file-info-detail span {
    font-weight: 600;
    color: var(--md-sys-color-on-surface);
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
# UPLOAD PAGE COMPONENTS - STREAMLINED
# -------------------------------

def render_upload_header():
    """Render clean upload page header."""
    st.markdown("""
    <div class="upload-page-header">
        <h1 class="upload-main-title">📤 Upload Your File</h1>
        <p class="upload-subtitle">Upload your Excel data file to begin production optimization</p>
    </div>
    """, unsafe_allow_html=True)


def render_upload_zone():
    """Render clean upload zone without unnecessary cards."""
    st.markdown("""
    <div class="upload-zone-clean" id="uploadZone">
        <div class="upload-icon-large">📁</div>
        <div class="upload-zone-title">Drag & drop your Excel file here</div>
        <div class="upload-zone-subtitle">or click to browse your files</div>
        <div class="upload-file-types">XLSX, XLS • Max 200MB</div>
    </div>
    """, unsafe_allow_html=True)
    
    # The actual file uploader (hidden behind the visual zone)
    uploaded_file = st.file_uploader(
        "Upload Excel file",
        type=["xlsx", "xls"],
        help="Upload an Excel file with Plant, Inventory, Demand, and Transition sheets",
        label_visibility="collapsed"
    )
    
    return uploaded_file


def render_download_template_section():
    """Render clean download template section."""
    try:
        template_path = Path(__file__).parent / "polymer_production_template.xlsx"
        if template_path.exists():
            with open(template_path, "rb") as f:
                template_data = f.read()
            
            st.markdown("""
            <div class="download-section-clean">
                <div class="download-header">
                    <span class="download-icon">📋</span>
                    <h3 class="download-title">Get Started with Template</h3>
                </div>
                <p class="download-description">
                    Download our pre-formatted Excel template with all required sheets 
                    and example data to get started quickly.
                </p>
            """, unsafe_allow_html=True)
            
            # Download button
            st.download_button(
                label="📥 Download Template",
                data=template_data,
                file_name="polymer_production_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="streamlined_download"
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Template file not found")
    except Exception as e:
        st.error(f"Template file not found: {e}")


def render_quick_start_guide_clean():
    """Render clean quick start guide."""
    st.markdown("""
    <div class="quick-start-guide">
        <div class="guide-header">
            <span class="guide-icon">🚀</span>
            <h2 class="guide-title">Quick Start Guide</h2>
        </div>
        <div class="guide-steps-clean">
            <div class="step-item-clean">
                <div class="step-number-clean">1</div>
                <div class="step-content-clean">
                    <span class="step-title-clean">Download Template</span>
                    <span class="step-description-clean">Get the pre-formatted Excel structure with all required sheets</span>
                </div>
            </div>
            <div class="step-item-clean">
                <div class="step-number-clean">2</div>
                <div class="step-content-clean">
                    <span class="step-title-clean">Fill Data</span>
                    <span class="step-description-clean">Complete Plant, Inventory, Demand, and Transition sheets with your data</span>
                </div>
            </div>
            <div class="step-item-clean">
                <div class="step-number-clean">3</div>
                <div class="step-content-clean">
                    <span class="step-title-clean">Upload File</span>
                    <span class="step-description-clean">Drag & drop or browse to upload your completed Excel file</span>
                </div>
            </div>
            <div class="step-item-clean">
                <div class="step-number-clean">4</div>
                <div class="step-content-clean">
                    <span class="step-title-clean">Configure & Run</span>
                    <span class="step-description-clean">Set optimization parameters and generate your production schedule</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_variable_details_complete():
    """Render complete variable and constraint details with all data."""
    with st.expander("📋 Variable and Constraint Details", expanded=False):
        detail_tabs = st.tabs(["🏭 Plant Sheet", "📦 Inventory Sheet", "📈 Demand Sheet", "🔄 Transition Sheets"])
        
        # Plant Sheet Tab
        with detail_tabs[0]:
            st.markdown("### Plant Sheet Configuration")
            st.markdown("*Required for all plants*")
            
            st.markdown("""
            <div class="details-table-container">
                <table class="details-table">
                    <thead>
                        <tr>
                            <th>Column</th>
                            <th>Description</th>
                            <th>Example</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Plant</strong></td>
                            <td>Plant identifier</td>
                            <td>Line_A</td>
                        </tr>
                        <tr>
                            <td><strong>Capacity per day</strong></td>
                            <td>Maximum daily output (MT)</td>
                            <td>500</td>
                        </tr>
                        <tr>
                            <td><strong>Material Running</strong></td>
                            <td>Currently producing grade</td>
                            <td>Grade_X</td>
                        </tr>
                        <tr>
                            <td><strong>Expected Run Days</strong></td>
                            <td>Days before changeover</td>
                            <td>3</td>
                        </tr>
                        <tr>
                            <td><strong>Shutdown Start Date</strong></td>
                            <td>Start of planned downtime</td>
                            <td>15-Jan-25</td>
                        </tr>
                        <tr>
                            <td><strong>Shutdown End Date</strong></td>
                            <td>End of planned downtime</td>
                            <td>17-Jan-25</td>
                        </tr>
                        <tr>
                            <td><strong>Pre-Shutdown Grade</strong></td>
                            <td>Grade before shutdown</td>
                            <td>Grade_A</td>
                        </tr>
                        <tr>
                            <td><strong>Restart Grade</strong></td>
                            <td>Grade after shutdown</td>
                            <td>Grade_B</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        # Inventory Sheet Tab
        with detail_tabs[1]:
            st.markdown("### Inventory Sheet Configuration")
            st.markdown("*Grade-level constraints*")
            
            st.markdown("""
            <div class="details-table-container">
                <table class="details-table">
                    <thead>
                        <tr>
                            <th>Column</th>
                            <th>Description</th>
                            <th>Constraint Type</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Grade Name</strong></td>
                            <td>Product identifier</td>
                            <td><span class="constraint-badge badge-none">-</span></td>
                        </tr>
                        <tr>
                            <td><strong>Opening Inventory</strong></td>
                            <td>Starting stock (MT)</td>
                            <td><span class="constraint-badge badge-hard">Hard</span></td>
                        </tr>
                        <tr>
                            <td><strong>Min. Inventory</strong></td>
                            <td>Safety stock level</td>
                            <td><span class="constraint-badge badge-soft">Soft (penalty)</span></td>
                        </tr>
                        <tr>
                            <td><strong>Max. Inventory</strong></td>
                            <td>Maximum storage capacity</td>
                            <td><span class="constraint-badge badge-hard">Hard</span></td>
                        </tr>
                        <tr>
                            <td><strong>Min. Closing Inventory</strong></td>
                            <td>End-period target</td>
                            <td><span class="constraint-badge badge-soft">Soft (3x penalty)</span></td>
                        </tr>
                        <tr>
                            <td><strong>Min. Run Days</strong></td>
                            <td>Minimum consecutive days</td>
                            <td><span class="constraint-badge badge-hard">Hard</span></td>
                        </tr>
                        <tr>
                            <td><strong>Max. Run Days</strong></td>
                            <td>Maximum consecutive days</td>
                            <td><span class="constraint-badge badge-hard">Hard</span></td>
                        </tr>
                        <tr>
                            <td><strong>Force Start Date</strong></td>
                            <td>Mandatory start date</td>
                            <td><span class="constraint-badge badge-hard">Hard</span></td>
                        </tr>
                        <tr>
                            <td><strong>Lines</strong></td>
                            <td>Plants where grade can run</td>
                            <td><span class="constraint-badge badge-hard">Hard</span></td>
                        </tr>
                        <tr>
                            <td><strong>Rerun Allowed</strong></td>
                            <td>Can repeat grade (Yes/No)</td>
                            <td><span class="constraint-badge badge-hard">Hard</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        # Demand Sheet Tab
        with detail_tabs[2]:
            st.markdown("### Demand Sheet Configuration")
            st.markdown("*Daily planning horizon*")
            
            st.markdown("""
            <div class="details-table-container">
                <table class="details-table">
                    <thead>
                        <tr>
                            <th>Column</th>
                            <th>Description</th>
                            <th>Example</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Date</strong></td>
                            <td>Planning horizon (daily)</td>
                            <td>01-Jan-25</td>
                        </tr>
                        <tr>
                            <td><strong>[Grade Name] columns</strong></td>
                            <td>Daily demand quantity (MT) for each grade</td>
                            <td>Grade_A, Grade_B, etc.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="sheet-example">
                <strong>Example Structure:</strong><br>
                Date, Grade_A, Grade_B, Grade_C<br>
                2025-01-01, 100, 150, 200<br>
                2025-01-02, 120, 130, 180<br>
                2025-01-03, 110, 140, 190
            </div>
            
            <p><strong>Note:</strong> Each grade should have its own column with daily demand values. Dates should be in chronological order.</p>
            """, unsafe_allow_html=True)
        
        # Transition Sheets Tab
        with detail_tabs[3]:
            st.markdown("### Transition Sheets Configuration")
            st.markdown("*Plant-specific transition rules*")
            
            st.markdown("""
            <div class="details-table-container">
                <table class="details-table">
                    <thead>
                        <tr>
                            <th>Element</th>
                            <th>Description</th>
                            <th>Example</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Sheet Naming</strong></td>
                            <td>Transition_[PlantName]</td>
                            <td>Transition_Line_A</td>
                        </tr>
                        <tr>
                            <td><strong>Rows</strong></td>
                            <td>Previous grade (running on day D)</td>
                            <td>Grade_A, Grade_B, Grade_C</td>
                        </tr>
                        <tr>
                            <td><strong>Columns</strong></td>
                            <td>Next grade (to run on day D+1)</td>
                            <td>Grade_A, Grade_B, Grade_C</td>
                        </tr>
                        <tr>
                            <td><strong>Values</strong></td>
                            <td>Yes (allowed) or No (forbidden)</td>
                            <td>Yes, No</td>
                        </tr>
                        <tr>
                            <td><strong>Constraint Type</strong></td>
                            <td>Transition rules</td>
                            <td><span class="constraint-badge badge-hard">Hard</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="sheet-example">
                <strong>Example Matrix:</strong><br>
                From → To, Grade_A, Grade_B, Grade_C<br>
                Grade_A, Yes, Yes, No<br>
                Grade_B, No, Yes, Yes<br>
                Grade_C, Yes, No, Yes
            </div>
            
            <p><strong>Note:</strong> Create one sheet per plant following the naming convention. Forbidden transitions (No) are blocked in optimization.</p>
            """, unsafe_allow_html=True)


# -------------------------------
# STATUS INDICATORS
# -------------------------------

def render_status_indicator(status: str, message: str):
    """Render enhanced status indicator."""
    status_classes = {
        "success": "status-success",
        "warning": "status-warning",
        "error": "status-error"
    }
    
    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    st.markdown(f"""
    <div class="status-indicator {status_classes.get(status, '')}">
        <span>{status_icons.get(status, 'ℹ️')}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)


def render_file_info(file_name: str, file_size: int):
    """Render file information after upload."""
    st.markdown(f"""
    <div class="file-info-display">
        <div class="file-info-header">
            <span class="file-info-icon">📊</span>
            <h3 class="file-info-title">File Uploaded Successfully</h3>
        </div>
        <div class="file-info-details">
            <div class="file-info-detail">
                <span>File:</span> {file_name}
            </div>
            <div class="file-info-detail">
                <span>Size:</span> {file_size / 1024:.1f} KB
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
