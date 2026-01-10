"""
Main Streamlit app for AI Code Reviewer - Enhanced Version.

Features:
- Dark theme throughout
- Multiple docstring styles (Google, NumPy, reST)
- Side-by-side docstring comparison
- Accept/Reject workflow with style tracking
- Direct file modification
- Enhanced metrics view
- Improved diff visualization
- PEP 257 Validation
"""
from dotenv import load_dotenv
load_dotenv()

import json
import os
import difflib
import streamlit as st
from core.parser.python_parser import parse_path
from core.docstring_engine.generator import generate_google_docstring, generate_class_docstring
from core.reporter.coverage_reporter import compute_coverage, write_report
from core.validator.validator import validate_project

# Import dashboard module
import dashboard

# Page config
st.set_page_config(page_title="AI Code Reviewer", layout="wide", initial_sidebar_state="expanded")


# Dark Theme CSS
st.markdown("""
<style>
    /* ==================== PROFESSIONAL COLOR PALETTE ==================== */
    /* Primary: #6366f1 (Indigo) */
    /* Secondary: #8b5cf6 (Purple) */
    /* Accent: #06b6d4 (Cyan) */
    /* Success: #10b981 (Emerald) */
    /* Warning: #f59e0b (Amber) */
    /* Error: #ef4444 (Red) */
    /* Background: #0f172a → #1e293b (Slate gradient) */
    
    /* ==================== GLOBAL THEME ==================== */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ==================== MAIN HEADER ==================== */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 3rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        color: white;
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        border-radius: 50%;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.75rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.75rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* ==================== SIDEBAR STYLING ==================== */
    /* Reduce sidebar width by ~14% */
    [data-testid="stSidebar"] {
        width: 18rem !important;
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.15);
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 18rem !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] h1 {
        color: #a5b4fc;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.2);
    }
    [data-testid="stSidebar"] h3 {
        color: #94a3b8;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 2rem 0 1rem 0;
    }
    
    /* ==================== NAVIGATION BUTTONS ==================== */
    [data-testid="stSidebar"] .stButton>button {
        width: 100%;
        text-align: left;
        padding: 0.875rem 1.25rem;
        margin: 0.375rem 0;
        font-size: 0.95rem;
        font-weight: 500;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
    }
    
    /* Active/Primary button - strong highlight */
    [data-testid="stSidebar"] .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
        color: white;
        font-weight: 600;
    }
    
    /* Inactive/Secondary buttons - dimmer */
    [data-testid="stSidebar"] .stButton>button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.3) !important;
        border: 1px solid rgba(148, 163, 184, 0.12) !important;
        color: #94a3b8 !important;
        opacity: 0.65;
    }
    
    /* Hover state for inactive buttons */
    [data-testid="stSidebar"] .stButton>button[kind="secondary"]:hover {
        opacity: 1;
        background: rgba(99, 102, 241, 0.1) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
        color: #e2e8f0 !important;
        transform: translateX(4px);
    }
    
    /* ==================== CARD CONTAINERS ==================== */
    .card-container {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    .card-container h3 {
        color: #a5b4fc;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 0;
    }
    
    /* ==================== FILE CARDS ==================== */
    .file-card {
        background: rgba(30, 41, 59, 0.4);
        border: 2px solid rgba(148, 163, 184, 0.2);
        border-radius: 14px;
        padding: 1.125rem 1.5rem;
        margin: 0.625rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .file-card:hover {
        border-color: #6366f1;
        background: rgba(99, 102, 241, 0.08);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
        transform: translateX(6px);
    }
    .file-card-selected {
        border: 2px solid #6366f1;
        background: rgba(99, 102, 241, 0.12);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
    }
    .file-name {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* ==================== STATUS BADGES ==================== */
    .status-fix {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.5rem 1.125rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
    }
    .status-ok {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1.125rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    }
    .status-partial {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.5rem 1.125rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
    }
    
    /* ==================== COMPARISON PANELS ==================== */
    .comparison-panel {
        background: rgba(30, 41, 59, 0.5);
        border: 2px solid rgba(148, 163, 184, 0.2);
        border-radius: 16px;
        padding: 1.75rem;
        height: 450px;
        overflow-y: auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
    }
    .panel-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #a5b4fc;
        margin-bottom: 1.25rem;
        padding-bottom: 0.875rem;
        border-bottom: 2px solid rgba(148, 163, 184, 0.2);
        display: flex;
        align-items: center;
        gap: 0.625rem;
    }
    
    /* ==================== DIFF VIEW ==================== */
    .diff-container {
        background: rgba(30, 41, 59, 0.5);
        border: 2px solid rgba(148, 163, 184, 0.2);
        border-radius: 16px;
        padding: 1.75rem;
        margin-top: 1.75rem;
        max-height: 400px;
        overflow-y: auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
    }
    .diff-header {
        font-weight: 700;
        color: #a5b4fc;
        margin-bottom: 1.25rem;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 0.625rem;
    }
    .diff-line {
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 0.875rem;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        white-space: pre-wrap;
        word-break: break-word;
        border-radius: 8px;
        line-height: 1.6;
    }
    .diff-add {
        background: rgba(16, 185, 129, 0.12);
        color: #6ee7b7;
        border-left: 3px solid #10b981;
    }
    .diff-remove {
        background: rgba(239, 68, 68, 0.12);
        color: #fca5a5;
        border-left: 3px solid #ef4444;
    }
    .diff-context {
        color: #94a3b8;
        background: rgba(148, 163, 184, 0.05);
    }
    .no-diff {
        color: #a5b4fc;
        font-style: italic;
        text-align: center;
        padding: 2.5rem;
        background: rgba(99, 102, 241, 0.08);
        border-radius: 12px;
        border: 2px dashed rgba(99, 102, 241, 0.3);
    }
    
    /* ==================== METRICS CARDS ==================== */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 20px;
        padding: 2.25rem;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        text-align: center;
        border: 2px solid rgba(148, 163, 184, 0.15);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s;
    }
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(99, 102, 241, 0.3);
        border-color: #6366f1;
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-value {
        font-size: 3.25rem;
        font-weight: 900;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        z-index: 1;
    }
    .metric-label {
        font-size: 1rem;
        color: #94a3b8;
        margin-top: 0.875rem;
        font-weight: 600;
        position: relative;
        z-index: 1;
    }
    .metric-icon {
        font-size: 2.75rem;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    
    /* ==================== INFO BOX ==================== */
    .info-box {
        background: rgba(99, 102, 241, 0.08);
        border-left: 4px solid #6366f1;
        padding: 1.75rem;
        border-radius: 12px;
        margin: 1.75rem 0;
        color: #e2e8f0;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.12);
    }
    .info-box h3 {
        margin-top: 0;
        color: #a5b4fc;
    }
    
    /* ==================== BUTTONS ==================== */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 2px solid transparent;
        padding: 0.625rem 1.25rem;
        font-size: 0.95rem;
    }
    .stButton>button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.6);
        color: #e2e8f0;
        border: 2px solid rgba(148, 163, 184, 0.2);
    }
    .stButton>button[kind="secondary"]:hover {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.3);
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    }
    
    /* ==================== CUSTOM SCROLLBAR ==================== */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
    }
    
    /* ==================== CODE BLOCKS ==================== */
    .stCodeBlock {
        background: rgba(15, 23, 41, 0.8) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
    }
    
    /* ==================== INPUTS ==================== */
    .stTextInput>div>div>input,
    .stSelectbox>div>div {
        background-color: rgba(30, 41, 59, 0.6);
        color: #e2e8f0;
        border: 2px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 0.625rem 1rem;
        transition: all 0.3s;
    }
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div:focus-within {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    }
    
    /* ==================== HIDE STREAMLIT BRANDING ==================== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ==================== RESPONSIVE DESIGN ==================== */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .metric-value {
            font-size: 2.5rem;
        }
        .card-container {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def load_test_results(json_path="storage/reports/pytest_results.json"):
    """Load and parse pytest JSON report."""
    try:
        if not os.path.exists(json_path):
            return None
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Parse test results
        tests = data.get('tests', [])
        summary = data.get('summary', {})
        
        # Group by test file
        results_by_file = {}
        for test in tests:
            nodeid = test.get('nodeid', '')
            # Extract file name (e.g., "tests/test_parser.py::test_function")
            file_name = nodeid.split('::')[0] if '::' in nodeid else nodeid
            file_name = file_name.split('/')[-1] if '/' in file_name else file_name
            
            if file_name not in results_by_file:
                results_by_file[file_name] = {
                    'passed': 0,
                    'failed': 0,
                    'skipped': 0,
                    'total': 0
                }
            
            outcome = test.get('outcome', 'unknown')
            results_by_file[file_name][outcome] = results_by_file[file_name].get(outcome, 0) + 1
            results_by_file[file_name]['total'] += 1
        
        return {
            'summary': summary,
            'by_file': results_by_file,
            'raw_tests': tests
        }
    except Exception as e:
        st.error(f"Error loading test results: {e}")
        return None
    


# Initialize session state
if "view" not in st.session_state:
    st.session_state.view = "Home"
if "docstring_style" not in st.session_state:
    st.session_state.docstring_style = "google"
if "selected_function" not in st.session_state:
    st.session_state.selected_function = None
if "selected_file" not in st.session_state:
    st.session_state.selected_file = None
if "scan_results" not in st.session_state:
    st.session_state.scan_results = []
if "accepted_styles" not in st.session_state:
    st.session_state.accepted_styles = {}
if "dashboard_view" not in st.session_state:
    st.session_state.dashboard_view = "overview"
if "doc_filter" not in st.session_state:
    st.session_state.doc_filter = "All"
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "sidebar_visible" not in st.session_state:
    st.session_state.sidebar_visible = True

# Helper function to get unique function ID
def get_function_id(func_data, file_path, class_name=None):
    """Create unique identifier for a function."""
    if class_name:
        return f"{file_path}::{class_name}.{func_data['name']}"
    return f"{file_path}::{func_data['name']}"

# Helper function to apply docstring to file
# ==============================================================================
# COMPLETE REPLACEMENT for apply_docstring_to_file function
# Find this function around line 160-220 in main.py and REPLACE ENTIRELY
# ==============================================================================

def apply_docstring_to_file(file_path, func_name, docstring, is_method=False, class_name=None, is_class=False):
    """Apply a docstring to a function, method, or class in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # ✅ NEW: Handle CLASS docstrings
        if is_class:
            # Find class definition line
            class_line_idx = None
            for i, line in enumerate(lines):
                if f"class {func_name}" in line and ":" in line:
                    class_line_idx = i
                    break
            
            if class_line_idx is None:
                return False
            
            # Get indentation for class body
            class_line = lines[class_line_idx]
            indent = len(class_line) - len(class_line.lstrip())
            body_indent = indent + 4
            
            # Check if there's already a docstring after class definition
            next_line_idx = class_line_idx + 1
            has_docstring = False
            docstring_end_idx = None
            
            if next_line_idx < len(lines):
                next_line = lines[next_line_idx].strip()
                if next_line.startswith('"""') or next_line.startswith("'''"):
                    has_docstring = True
                    # Check if it's a one-liner docstring
                    if next_line.count('"""') >= 2 or next_line.count("'''") >= 2:
                        docstring_end_idx = next_line_idx
                    else:
                        # Multi-line docstring - find the end
                        for j in range(next_line_idx + 1, len(lines)):
                            if '"""' in lines[j] or "'''" in lines[j]:
                                docstring_end_idx = j
                                break
            
            # Prepare new docstring with proper indentation
            docstring_lines = docstring.split('\n')
            indented_docstring = []
            for line in docstring_lines:
                if line.strip():
                    indented_docstring.append(' ' * body_indent + line + '\n')
                else:
                    indented_docstring.append('\n')
            
            # Replace or insert docstring
            if has_docstring and docstring_end_idx is not None:
                # Remove old docstring
                del lines[next_line_idx:docstring_end_idx + 1]
                # Insert new docstring
                for idx, line in enumerate(indented_docstring):
                    lines.insert(next_line_idx + idx, line)
            else:
                # Insert new docstring (no existing docstring)
                for idx, line in enumerate(indented_docstring):
                    lines.insert(next_line_idx + idx, line)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
        
        # ✅ EXISTING: Handle FUNCTION/METHOD docstrings
        # Find the function definition line
        func_line_idx = None
        in_target_class = not is_method
        
        for i, line in enumerate(lines):
            if is_method and class_name:
                if f"class {class_name}" in line:
                    in_target_class = True
                    continue
            
            if in_target_class and f"def {func_name}(" in line:
                func_line_idx = i
                break
        
        if func_line_idx is None:
            return False
        
        # Get indentation
        func_line = lines[func_line_idx]
        indent = len(func_line) - len(func_line.lstrip())
        body_indent = indent + 4
        
        # Check if there's already a docstring
        next_line_idx = func_line_idx + 1
        has_docstring = False
        docstring_end_idx = None
        
        if next_line_idx < len(lines):
            next_line = lines[next_line_idx].strip()
            if next_line.startswith('"""') or next_line.startswith("'''"):
                has_docstring = True
                # Find the end of the docstring
                if next_line.count('"""') >= 2 or next_line.count("'''") >= 2:
                    docstring_end_idx = next_line_idx
                else:
                    for j in range(next_line_idx + 1, len(lines)):
                        if '"""' in lines[j] or "'''" in lines[j]:
                            docstring_end_idx = j
                            break
        
        # Prepare new docstring
        docstring_lines = docstring.split('\n')
        indented_docstring = []
        for line in docstring_lines:
            if line.strip():
                indented_docstring.append(' ' * body_indent + line + '\n')
            else:
                indented_docstring.append('\n')
        
        # Replace or insert docstring
        if has_docstring and docstring_end_idx is not None:
            # Remove old docstring
            del lines[next_line_idx:docstring_end_idx + 1]
            # Insert new docstring
            for idx, line in enumerate(indented_docstring):
                lines.insert(next_line_idx + idx, line)
        else:
            # Insert new docstring
            for idx, line in enumerate(indented_docstring):
                lines.insert(next_line_idx + idx, line)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True
    except Exception as e:
        st.error(f"Error applying docstring: {e}")
        return False

def docstrings_are_identical(doc1, doc2):
    """Check if two docstrings are identical (ignoring whitespace differences)."""
    clean1 = doc1.strip().strip('"""').strip("'''").strip()
    clean2 = doc2.strip().strip('"""').strip("'''").strip()
    return clean1 == clean2

# Sidebar
with st.sidebar:
    st.markdown("# 🧠 AI Code Reviewer")
    
    # Toggle button
    if st.button("✕ Close Menu", use_container_width=True, type="secondary"):
        st.session_state.sidebar_visible = False
        st.rerun()
    
    st.markdown("---")
    
    # Side Navigation Bar
    st.markdown("### Navigation")
    
    # Navigation buttons
    nav_items = [
    ("🏠", "Home", "home"),
    ("📝", "Docstrings", "docstrings"),
    ("📊", "Dashboard", "dashboard"),
    ("📈", "Metrics", "metrics"),
    ("✅", "Validation", "validation")
   ]
    
    for icon, label, view_key in nav_items:
        is_active = st.session_state.view == label
        button_type = "primary" if is_active else "secondary"
        
        if st.button(
            f"{icon} {label}", 
            key=f"nav_{view_key}",
            use_container_width=True,
            type=button_type
        ):
            st.session_state.view = label
            st.rerun()
    
    st.markdown("---")
    
    # Configuration Section
    st.markdown("### Configuration")
    scan_path = st.text_input("Path to scan", value="examples", placeholder="examples")
    
    output_path = st.text_input("Output JSON path", value="storage/review_logs.json", placeholder="storage/review_logs.json")
    
    if st.button("🔍 Scan Project", use_container_width=True, type="primary"):
        if not os.path.exists(scan_path):
            st.error(f"❌ Path does not exist: {scan_path}")
        else:
            with st.spinner("🔄 Scanning files..."):
                try:
                    skip_dirs = ["__pycache__", "venv", ".git", ".venv", "node_modules"]
                    results = parse_path(scan_path, recursive=True, skip_dirs=skip_dirs)
                    
                    if not results:
                        st.warning("⚠️ No Python files found.")
                    else:
                        st.session_state.scan_results = results
                        st.session_state.accepted_styles = {}
                        
                        # Generate docstrings for all styles for ALL functions
                        total_functions = 0
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Count total functions first
                        total_functions = 0
                        for file_result in results:
                            total_functions += len(file_result.get("functions", []))
                            for cls in file_result.get("classes", []):
                                total_functions += 1  # Count the class itself
                                total_functions += len(cls.get("methods", []))
                        
                        current = 0
                        
                        for file_result in results:
                            file_path = file_result.get("file_path", "")
                            
                            # Process standalone functions
                            for func in file_result.get("functions", []):
                                current += 1
                                progress_bar.progress(current / total_functions)
                                status_text.text(f"Generating docstrings for: {func['name']} ({current}/{total_functions})")
                                
                                func_id = get_function_id(func, file_path)
                                
                                existing_doc = func.get("docstring", "")
                                if existing_doc and existing_doc.strip():
                                    func["original_docstring"] = existing_doc
                                else:
                                    func["original_docstring"] = '"""\nNo docstring.\n"""'
                                
                                try:
                                    func["suggested_docstrings"] = {
                                        "google": generate_google_docstring(func, use_groq=True, style="google"),
                                        "numpy": generate_google_docstring(func, use_groq=True, style="numpy"),
                                        "rest": generate_google_docstring(func, use_groq=True, style="rest")
                                    }
                                except Exception as e:
                                    st.warning(f"⚠️ Error generating for {func['name']}: {str(e)}")
                                    func["suggested_docstrings"] = {
                                        "google": '"""\nError generating docstring.\n"""',
                                        "numpy": '"""\nError generating docstring.\n"""',
                                        "rest": '"""\nError generating docstring.\n"""'
                                    }
                            
                            # Process classes AND their methods
                            for cls in file_result.get("classes", []):
                                # ✅ NEW: Generate docstring for the CLASS itself
                                current += 1
                                progress_bar.progress(current / total_functions)
                                status_text.text(f"Generating docstrings for class: {cls['name']} ({current}/{total_functions})")
                                
                                existing_class_doc = cls.get("docstring", "")
                                if existing_class_doc and existing_class_doc.strip():
                                    cls["original_docstring"] = existing_class_doc
                                else:
                                    cls["original_docstring"] = '"""\nNo docstring.\n"""'
                                
                                try:
                                    cls["suggested_docstrings"] = {
                                        "google": generate_class_docstring(cls, use_groq=True, style="google"),
                                        "numpy": generate_class_docstring(cls, use_groq=True, style="numpy"),
                                        "rest": generate_class_docstring(cls, use_groq=True, style="rest")
                                    }
                                except Exception as e:
                                    st.warning(f"⚠️ Error generating class docstring for {cls['name']}: {str(e)}")
                                    cls["suggested_docstrings"] = {
                                        "google": '"""\nError generating docstring.\n"""',
                                        "numpy": '"""\nError generating docstring.\n"""',
                                        "rest": '"""\nError generating docstring.\n"""'
                                    }
                                
                                # Now process the class methods
                                for method in cls.get("methods", []):
                                    current += 1
                                    progress_bar.progress(current / total_functions)
                                    status_text.text(f"Generating docstrings for: {cls['name']}.{method['name']} ({current}/{total_functions})")
                                    
                                    func_id = get_function_id(method, file_path, cls["name"])
                                    
                                    existing_doc = method.get("docstring", "")
                                    if existing_doc and existing_doc.strip():
                                        method["original_docstring"] = existing_doc
                                    else:
                                        method["original_docstring"] = '"""\nNo docstring.\n"""'
                                    method["class_name"] = cls["name"]
                                    
                                    try:
                                        method["suggested_docstrings"] = {
                                            "google": generate_google_docstring(method, use_groq=True, style="google"),
                                            "numpy": generate_google_docstring(method, use_groq=True, style="numpy"),
                                            "rest": generate_google_docstring(method, use_groq=True, style="rest")
                                        }
                                    except Exception as e:
                                        st.warning(f"⚠️ Error generating for {cls['name']}.{method['name']}: {str(e)}")
                                        method["suggested_docstrings"] = {
                                            "google": '"""\nError generating docstring.\n"""',
                                            "numpy": '"""\nError generating docstring.\n"""',
                                            "rest": '"""\nError generating docstring.\n"""'
                                        }
                        
                        progress_bar.progress(1.0)
                        status_text.text(f"✅ Completed! Generated docstrings for {total_functions} functions")
                        
                        # Compute coverage
                        report = compute_coverage(results)
                        st.session_state.report = report
                        
                        st.success("✅ Scan completed!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    import traceback
                    st.error(traceback.format_exc())
    
            
    # Show scan status at the bottom
    if st.session_state.scan_results:
        st.markdown("---")
        st.success("✅ Project scanned")
        total_files = len(st.session_state.scan_results)
        st.info(f"📁 {total_files} files analyzed")


# Sidebar visibility control with floating button
st.markdown(f"""
<style>
    /* Hide/show sidebar smoothly with reduced width */
    [data-testid="stSidebar"] {{
        margin-left: {'-18rem' if not st.session_state.sidebar_visible else '0'};
        transition: margin-left 0.3s ease;
    }}
</style>
""", unsafe_allow_html=True)

# Floating toggle button (only show when sidebar is hidden)
if not st.session_state.sidebar_visible:
    if st.button("☰ Open Menu", key="floating-toggle", type="primary"):
        st.session_state.sidebar_visible = True
        st.rerun()

# Main content based on view
if st.session_state.view == "Home":
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI-Powered Code Reviewer</h1>
        <p>Intelligent documentation analysis and generation</p>
    </div>
    """, unsafe_allow_html=True)
    
    
    
    # Show welcome message or scan results
    if not st.session_state.scan_results:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">👋 Welcome to AI Code Reviewer</h3>
            <p>Get started by scanning your project directory to analyze Python code documentation.</p>
            <ul style="margin: 1rem 0;">
                <li>Analyze Python code documentation</li>
                <li>Generate docstrings in multiple styles</li>
                <li>Track coverage metrics</li>
                <li>Apply changes directly to your code</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Prominent scan section in Home
        st.markdown("---")
        st.markdown('<div class="section-header">🔍 Get Started</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card-container">
            <h3 style="margin-top: 0; color: #a5b4fc;">📂 Scan Your Project</h3>
            <p style="color: #cbd5e1; line-height: 1.7;">
                Enter the path to your Python project directory below. The scanner will recursively 
                analyze all Python files and generate docstring suggestions.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            home_scan_path = st.text_input(
                "Project Path", 
                value="examples", 
                placeholder="examples or /path/to/your/project",
                key="home_scan_path",
                label_visibility="collapsed"
            )
        
        with col2:
            home_scan_button = st.button(
                "🔍 Scan Project", 
                use_container_width=True, 
                type="primary",
                key="home_scan_button"
            )
        
        if home_scan_button:
            if not os.path.exists(home_scan_path):
                st.error(f"❌ Path does not exist: {home_scan_path}")
            else:
                with st.spinner("🔄 Scanning files..."):
                    try:
                        skip_dirs = ["__pycache__", "venv", ".git", ".venv", "node_modules"]
                        results = parse_path(home_scan_path, recursive=True, skip_dirs=skip_dirs)
                        
                        if not results:
                            st.warning("⚠️ No Python files found.")
                        else:
                            st.session_state.scan_results = results
                            st.session_state.accepted_styles = {}
                            
                            # Generate docstrings for all styles for ALL functions
                            total_functions = 0
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Count total functions first
                            for file_result in results:
                                total_functions += len(file_result.get("functions", []))
                                for cls in file_result.get("classes", []):
                                    total_functions += 1  # Count the class itself
                                    total_functions += len(cls.get("methods", []))
                            
                            current = 0
                            
                            for file_result in results:
                                file_path = file_result.get("file_path", "")
                                
                                # Process standalone functions
                                for func in file_result.get("functions", []):
                                    current += 1
                                    progress_bar.progress(current / total_functions)
                                    status_text.text(f"Generating docstrings for: {func['name']} ({current}/{total_functions})")
                                    
                                    func_id = get_function_id(func, file_path)
                                    
                                    existing_doc = func.get("docstring", "")
                                    if existing_doc and existing_doc.strip():
                                        func["original_docstring"] = existing_doc
                                    else:
                                        func["original_docstring"] = '"""\nNo docstring.\n"""'
                                    
                                    try:
                                        func["suggested_docstrings"] = {
                                            "google": generate_google_docstring(func, use_groq=True, style="google"),
                                            "numpy": generate_google_docstring(func, use_groq=True, style="numpy"),
                                            "rest": generate_google_docstring(func, use_groq=True, style="rest")
                                        }
                                    except Exception as e:
                                        st.warning(f"⚠️ Error generating for {func['name']}: {str(e)}")
                                        func["suggested_docstrings"] = {
                                            "google": '"""\nError generating docstring.\n"""',
                                            "numpy": '"""\nError generating docstring.\n"""',
                                            "rest": '"""\nError generating docstring.\n"""'
                                        }
                                
                                # Process classes AND their methods
                                for cls in file_result.get("classes", []):
                                    # ✅ NEW: Generate docstring for the CLASS itself
                                    current += 1
                                    progress_bar.progress(current / total_functions)
                                    status_text.text(f"Generating docstrings for class: {cls['name']} ({current}/{total_functions})")
                                    
                                    existing_class_doc = cls.get("docstring", "")
                                    if existing_class_doc and existing_class_doc.strip():
                                        cls["original_docstring"] = existing_class_doc
                                    else:
                                        cls["original_docstring"] = '"""\nNo docstring.\n"""'
                                    
                                    try:
                                        cls["suggested_docstrings"] = {
                                            "google": generate_class_docstring(cls, use_groq=True, style="google"),
                                            "numpy": generate_class_docstring(cls, use_groq=True, style="numpy"),
                                            "rest": generate_class_docstring(cls, use_groq=True, style="rest")
                                        }
                                    except Exception as e:
                                        st.warning(f"⚠️ Error generating class docstring for {cls['name']}: {str(e)}")
                                        cls["suggested_docstrings"] = {
                                            "google": '"""\nError generating docstring.\n"""',
                                            "numpy": '"""\nError generating docstring.\n"""',
                                            "rest": '"""\nError generating docstring.\n"""'
                                        }
                                    
                                    # Now process the class methods
                                    for method in cls.get("methods", []):
                                        current += 1
                                        progress_bar.progress(current / total_functions)
                                        status_text.text(f"Generating docstrings for: {cls['name']}.{method['name']} ({current}/{total_functions})")
                                        
                                        func_id = get_function_id(method, file_path, cls["name"])
                                        
                                        existing_doc = method.get("docstring", "")
                                        if existing_doc and existing_doc.strip():
                                            method["original_docstring"] = existing_doc
                                        else:
                                            method["original_docstring"] = '"""\nNo docstring.\n"""'
                                        method["class_name"] = cls["name"]
                                        
                                        try:
                                            method["suggested_docstrings"] = {
                                                "google": generate_google_docstring(method, use_groq=True, style="google"),
                                                "numpy": generate_google_docstring(method, use_groq=True, style="numpy"),
                                                "rest": generate_google_docstring(method, use_groq=True, style="rest")
                                            }
                                        except Exception as e:
                                            st.warning(f"⚠️ Error generating for {cls['name']}.{method['name']}: {str(e)}")
                                            method["suggested_docstrings"] = {
                                                "google": '"""\nError generating docstring.\n"""',
                                                "numpy": '"""\nError generating docstring.\n"""',
                                                "rest": '"""\nError generating docstring.\n"""'
                                            }
                            
                            progress_bar.progress(1.0)
                            status_text.text(f"✅ Completed! Generated docstrings for {total_functions} functions")
                            
                            # Compute coverage
                            report = compute_coverage(results)
                            st.session_state.report = report
                            
                            st.success("✅ Scan completed!")
                            st.balloons()
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        import traceback
                        st.error(traceback.format_exc())
        
        # Add helpful tip
        st.markdown("""
        <div style="background: rgba(99, 102, 241, 0.08); border-left: 4px solid #6366f1; 
                    padding: 1.25rem; border-radius: 12px; margin-top: 2rem;">
            <p style="margin: 0; color: #cbd5e1; font-size: 0.95rem;">
                💡 <strong>Tip:</strong> Make sure your <code>.env</code> file contains a valid 
                <code>GROQ_API_KEY</code> for AI-powered docstring generation.
            </p>
        </div>
        """, unsafe_allow_html=True)

        
    else:
        # Show quick overview metrics
        total_functions = 0
        documented_functions = 0
        for file in st.session_state.scan_results:
        # Count standalone functions
            for fn in file.get("functions", []):
                total_functions += 1
                if fn.get("has_docstring", False):
                    documented_functions += 1
    
    # Count class methods
            for cls in file.get("classes", []):
                for method in cls.get("methods", []):
                    total_functions += 1
                    if method.get("has_docstring", False):
                        documented_functions += 1
        coverage = (documented_functions / total_functions * 100) if total_functions > 0 else 0
        
        st.markdown('<div class="section-header">📈 Documentation Coverage</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            #coverage = report.get('overall_coverage_percentage', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📊</div>
                <div class="metric-value">{coverage:.1f}%</div>
                <div class="metric-label">Documentation Coverage</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📑</div>
                <div class="metric-value">{total_functions}</div>
                <div class="metric-label">Total Functions</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">✅</div>
                <div class="metric-value">{documented_functions}</div>
                <div class="metric-label">Documented</div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.view == "Dashboard":
    # Dashboard view with advanced features
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard</h1>
        <p>Advanced tools for code analysis and management</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.scan_results:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">⚠️ No Scan Results</h3>
            <p>Please run a project scan from the sidebar to access enhanced features.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Render feature cards and dashboard views
        dashboard.render_feature_cards()
        
        # Render appropriate sub-view
        if st.session_state.dashboard_view == "filters":
            dashboard.render_filters_view()
        elif st.session_state.dashboard_view == "search":
            dashboard.render_search_view()
        elif st.session_state.dashboard_view == "tests":
            dashboard.render_tests_view()
        elif st.session_state.dashboard_view == "export":
            dashboard.render_export_view()
        elif st.session_state.dashboard_view == "help":
            dashboard.render_help_view()
        else:
            # Show overview message
            st.markdown("""
            <div class="info-box">
                <h3 style="margin-top: 0;">🎯 Select a Feature</h3>
                <p>Click one of the feature cards above to access advanced tools:</p>
                <ul style="margin: 1rem 0;">
                    <li><strong>Advanced Filters</strong> - Filter functions by documentation status</li>
                    <li><strong>Search</strong> - Find functions by name across your project</li>
                    <li><strong>Test Results</strong> - View pytest test results and coverage</li>
                    <li><strong>Export</strong> - Download reports in JSON or CSV format</li>
                    <li><strong>Help & Tips</strong> - Complete usage guide and best practices</li>
                </ul>
                
            </div>
            """, unsafe_allow_html=True)


elif st.session_state.view == "Docstrings":
    st.markdown('<div class="section-header">📘 Docstring Review & Generation</div>', unsafe_allow_html=True)
    
    if not st.session_state.scan_results:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">⚠️ No Scan Results</h3>
            <p>Please run a project scan from the sidebar to begin reviewing docstrings.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Docstring style selector
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-top: 0; color: #a5b4fc;">📋 Select Docstring Style</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📗 Google Style", use_container_width=True, type="primary" if st.session_state.docstring_style == "google" else "secondary"):
                st.session_state.docstring_style = "google"
                st.rerun()
        
        with col2:
            if st.button("📕 NumPy Style", use_container_width=True, type="primary" if st.session_state.docstring_style == "numpy" else "secondary"):
                st.session_state.docstring_style = "numpy"
                st.rerun()
        
        with col3:
            if st.button("📙 reST Style", use_container_width=True, type="primary" if st.session_state.docstring_style == "rest" else "secondary"):
                st.session_state.docstring_style = "rest"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Files and Function sections
        col_files, col_function = st.columns([1, 2])
        
        with col_files:
            st.markdown('<div class="section-header">📁 Project Files</div>', unsafe_allow_html=True)
            
            # Count files
            total_files = len(st.session_state.scan_results)
            st.markdown(f"<p style='color: #94a3b8; margin: 1rem 0; font-size: 0.95rem;'>Total: {total_files} files | Style: <strong>{st.session_state.docstring_style.upper()}</strong></p>", unsafe_allow_html=True)
           

            # Display files
            for file_result in st.session_state.scan_results:
                file_path = file_result.get("file_path", "")
                file_name = os.path.basename(file_path)
                
                # ✅ FIXED: Collect all functions AND classes
                all_items = []  # Changed from all_funcs to all_items
                
                # Add standalone functions
                for func in file_result.get("functions", []):
                    all_items.append(("function", func, None))
                
                # Add classes AND their methods
                for cls in file_result.get("classes", []):
                    # ✅ NEW: Add the class itself as an item
                    all_items.append(("class", cls, cls["name"]))
                    
                    # Add the class's methods
                    for method in cls.get("methods", []):
                        all_items.append(("method", method, cls["name"]))
                
                # ✅ CRITICAL: Check status for THIS SPECIFIC STYLE ONLY
                current_style = st.session_state.docstring_style  # "google", "numpy", or "rest"
                
                needs_fix = 0
                all_ok = 0
                
                for item_type, item, cls_name in all_items:  # Changed from func to item
                    # Generate appropriate func_id based on item type
                    if item_type == "class":
                        # For classes, use the class name directly
                        func_id = get_function_id({"name": item["name"]}, file_path, None)
                    else:
                        # For functions and methods
                        func_id = get_function_id(item, file_path, cls_name)
                    
                    # Check 1: Has this specific style been manually accepted?
                    accepted_styles_for_item = st.session_state.accepted_styles.get(func_id, [])
                    is_style_accepted = current_style in accepted_styles_for_item
                    
                    # Check 2: Does the original match THIS SPECIFIC style's suggestion?
                    original_doc = item.get("original_docstring", "")
                    suggested_docs = item.get("suggested_docstrings", {})
                    
                    if current_style in suggested_docs:
                        current_style_suggestion = suggested_docs[current_style]
                        is_style_identical = docstrings_are_identical(original_doc, current_style_suggestion)
                    else:
                        is_style_identical = False
                    
                    # Count as OK ONLY if:
                    # - This specific style was manually accepted, OR
                    # - Original matches this specific style's suggestion
                    if is_style_accepted or is_style_identical:
                        all_ok += 1
                    else:
                        needs_fix += 1
                
                # Determine status badge
                if needs_fix == 0 and all_ok > 0:
                    status_html = '<span class="status-ok">🟢 Complete</span>'
                elif needs_fix > 0 and all_ok > 0:
                    status_html = f'<span class="status-partial">🟡 {needs_fix} pending</span>'
                else:
                    status_html = f'<span class="status-fix">🔴 {needs_fix} needed</span>'
                
                card_class = "file-card file-card-selected" if st.session_state.selected_file == file_name else "file-card"
                
                if st.button(f"📄 {file_name}", key=f"file_{file_name}", use_container_width=True):
                    st.session_state.selected_file = file_name
                    st.session_state.selected_function = None
                    st.rerun()
                
                st.markdown(f'<div class="{card_class}"><span class="file-name">{file_name}</span>{status_html}</div>', unsafe_allow_html=True)
                
        with col_function:
            if st.session_state.selected_file:
                st.markdown(f'<div class="section-header">⚙️ Function Review</div>', unsafe_allow_html=True)
                
                # Find the selected file
                selected_file_result = None
                for file_result in st.session_state.scan_results:
                    if os.path.basename(file_result.get("file_path", "")) == st.session_state.selected_file:
                        selected_file_result = file_result
                        break
                
                if selected_file_result:
                    file_path = selected_file_result.get("file_path", "")
                    
                    # Collect all functions
                    all_functions = []
                    for func in selected_file_result.get("functions", []):
                        all_functions.append(("function", func, None))
                    
                    for cls in selected_file_result.get("classes", []):
                        # ✅ NEW: Add the class itself as a reviewable item
                        all_functions.append(("class", cls, cls["name"]))
                        for method in cls.get("methods", []):
                            all_functions.append(("method", method, cls["name"]))
                    
                    if not all_functions:
                        st.markdown("""
                        <div class="info-box">
                            <h3 style="margin-top: 0;">🎉 No Functions Found</h3>
                            <p>This file doesn't contain any functions or methods.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Check if docstrings are generated
                        first_func = all_functions[0][1]
                        if "suggested_docstrings" not in first_func or not first_func["suggested_docstrings"]:
                            st.markdown("""
                            <div class="info-box">
                                <h3 style="margin-top: 0;">⚠️ Docstrings Not Generated</h3>
                                <p>Docstrings haven't been generated yet. Please run the scan again.</p>
                                <p>Make sure <strong>GROQ_API_KEY</strong> is set in your <code>.env</code> file.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Function selector
                            func_names = []
                            func_statuses = []
                            for func_type, func, cls_name in all_functions:
                                if func_type == "class":
                                    display_name = f"[CLASS] {func['name']}"
                                elif func_type == "method":
                                    display_name = f"{cls_name}.{func['name']}"
                                else:
                                    display_name = func['name']
                                func_names.append(display_name)
                                
                                # Check if accepted in current style
                                func_id = get_function_id(func, file_path, cls_name)
                                accepted = st.session_state.accepted_styles.get(func_id, [])
                                if st.session_state.docstring_style in accepted:
                                    func_statuses.append("✅")
                                else:
                                    func_statuses.append("🔴")
                            
                            # Create formatted options
                            formatted_options = [f"{status} {name}" for status, name in zip(func_statuses, func_names)]
                            
                            if not st.session_state.selected_function or st.session_state.selected_function not in func_names:
                                st.session_state.selected_function = func_names[0]
                            
                            # Find current index
                            try:
                                current_idx = func_names.index(st.session_state.selected_function)
                            except ValueError:
                                current_idx = 0
                                st.session_state.selected_function = func_names[0]
                            
                            selected_display = st.selectbox("Select Function", formatted_options, index=current_idx, key="func_selector")
                            # Extract actual function name (remove status emoji)
                            st.session_state.selected_function = selected_display.split(" ", 1)[1]
                            
                            # Find the selected function
                            selected_func_data = None
                            selected_func_type = None
                            selected_class_name = None
                            
                            for func_type, func, cls_name in all_functions:
                                if func_type == "class":
                                    display_name = f"[CLASS] {func['name']}"
                                elif func_type == "method":
                                    display_name = f"{cls_name}.{func['name']}"
                                else:
                                    display_name = func['name']
                                if display_name == st.session_state.selected_function:
                                    selected_func_data = func
                                    selected_func_type = func_type
                                    selected_class_name = cls_name
                                    break
                            
                            if selected_func_data and "suggested_docstrings" in selected_func_data:
                                func_id = get_function_id(selected_func_data, file_path, selected_class_name)
                                accepted_styles = st.session_state.accepted_styles.get(func_id, [])
                                
                                # Before and After comparison
                                st.markdown("---")
                                col_before, col_after = st.columns(2)
                                
                                with col_before:
                                    st.markdown('<div class="panel-header">📋 Current Docstring</div>', unsafe_allow_html=True)
                                    
                                    # Show original docstring
                                    before_doc = selected_func_data.get("original_docstring", '"""\nNo docstring.\n"""')
                                    st.code(before_doc, language="python")
                                
                                with col_after:
                                    st.markdown(f'<div class="panel-header">✨ Generated ({st.session_state.docstring_style.upper()})</div>', unsafe_allow_html=True)
                                    
                                    style = st.session_state.docstring_style
                                    after_doc = selected_func_data.get("suggested_docstrings", {}).get(style, '"""\nGenerated docstring.\n"""')
                                    st.code(after_doc, language="python")
                                
                                # Check if docstrings are identical
                                are_identical = docstrings_are_identical(before_doc, after_doc)
                                
                                # Status indicator
                                if style in accepted_styles:
                                    st.success(f"✅ {style.upper()} style already accepted and applied to code")
                                elif are_identical:
                                    st.info(f"✨ No changes needed - docstrings are identical")
                                else:
                                    st.info(f"⏳ {style.upper()} style pending review")
                                
                                # Only show Accept/Reject buttons if NOT identical and NOT already accepted
                                if not are_identical and style not in accepted_styles:
                                    st.markdown("---")
                                    col_accept, col_reject, col_status = st.columns([2, 2, 3])
                                    
                                    # Find the "Accept & Apply" button handler in main.py (around line 1320-1360)
                                    # Replace the entire if st.button("✅ Accept & Apply"...) block with this:

                                    with col_accept:
                                        if st.button("✅ Accept & Apply", use_container_width=True, type="primary", key="accept_btn"):
                                            func_name = selected_func_data["name"]
                                            docstring = selected_func_data["suggested_docstrings"][style]
                                            
                                            is_method = selected_func_type == "method"
                                            is_class = selected_func_type == "class"  # ✅ NEW
                                            
                                            with st.spinner("Applying docstring to file..."):
                                                success = apply_docstring_to_file(
                                                    file_path,
                                                    func_name,
                                                    docstring,
                                                    is_method=is_method,
                                                    class_name=selected_class_name,
                                                    is_class=is_class  # ✅ NEW
                                                )
                                            
                                            if success:
                                                st.session_state.accepted_styles[func_id] = [style]
                                                selected_func_data["original_docstring"] = docstring
                                                selected_func_data["has_docstring"] = True
                                                selected_func_data["docstring"] = docstring
                                                
                                                for other_style in ["google", "numpy", "rest"]:
                                                    if other_style != style:
                                                        other_suggestion = selected_func_data["suggested_docstrings"].get(other_style, "")
                                                        if docstrings_are_identical(docstring, other_suggestion):
                                                            if other_style not in st.session_state.accepted_styles[func_id]:
                                                                st.session_state.accepted_styles[func_id].append(other_style)
                                                
                                                report = compute_coverage(st.session_state.scan_results)
                                                st.session_state.report = report
                                                
                                                item_type = "class" if is_class else "function"
                                                st.success(f"✅ Applied {style.upper()} docstring to {item_type} {st.session_state.selected_function}")
                                                st.balloons()
                                                st.rerun()
                                            else:
                                                st.error("❌ Failed to apply docstring to file")
                                    
                                    with col_reject:
                                        if st.button("❌ Skip This Style", use_container_width=True, key="reject_btn"):
                                            st.warning(f"⏭️ Skipped {style.upper()} style - no changes made to code")
                                    
                                    with col_status:
                                        # Show which styles have been accepted
                                        accepted_count = len(accepted_styles)
                                        if accepted_count > 0:
                                            accepted_list = ", ".join([s.upper() for s in accepted_styles])
                                            st.info(f"📝 Applied: {accepted_list}")

                                elif style in accepted_styles:
                                    # Show status for already accepted
                                    st.markdown("---")
                                    accepted_list = ", ".join([s.upper() for s in accepted_styles])
                                    st.info(f"📝 Applied: {accepted_list}")
                                
                                # Diff view
                                st.markdown("---")
                                st.markdown('<div class="diff-container"><div class="diff-header">🔍 Detailed Diff</div>', unsafe_allow_html=True)
                                
                                before_lines = before_doc.split('\n')
                                after_lines = after_doc.split('\n')
                                
                                # Check if there's any actual difference
                                if before_doc.strip() == after_doc.strip():
                                    st.markdown('<div class="no-diff">✨ No changes needed - docstrings are identical</div>', unsafe_allow_html=True)
                                else:
                                    diff = difflib.unified_diff(
                                        before_lines,
                                        after_lines,
                                        lineterm='',
                                        fromfile='Current',
                                        tofile='Generated'
                                    )
                                    
                                    diff_html = ""
                                    has_diff = False
                                    for line in diff:
                                        if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                                            continue
                                        has_diff = True
                                        if line.startswith('-'):
                                            diff_html += f'<div class="diff-line diff-remove">- {line[1:]}</div>'
                                        elif line.startswith('+'):
                                            diff_html += f'<div class="diff-line diff-add">+ {line[1:]}</div>'
                                        else:
                                            diff_html += f'<div class="diff-line diff-context">  {line[1:] if line.startswith(" ") else line}</div>'
                                    
                                    if not has_diff:
                                        st.markdown('<div class="no-diff">✨ No changes needed - docstrings are identical</div>', unsafe_allow_html=True)
                                    else:
                                        st.markdown(diff_html, unsafe_allow_html=True)
                                
                                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="info-box">
                    <h3 style="margin-top: 0;">📂 Select a File</h3>
                    <p>Choose a file from the list on the left to review its functions.</p>
                </div>
                """, unsafe_allow_html=True)

elif st.session_state.view == "Metrics":
    st.markdown('<div class="section-header">📊 Code Metrics & Analysis</div>', unsafe_allow_html=True)
    
    if not st.session_state.scan_results:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">⚠️ No Scan Results</h3>
            <p>Please run a project scan from the sidebar to view metrics.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Build metrics data - ensure each function appears exactly once
        metrics_data = []
        seen_functions = set()  # Track unique functions
        
        for file_result in st.session_state.scan_results:
            file_path = file_result.get("file_path", "")
            file_name = os.path.basename(file_path)
            
            # Standalone functions
            for func in file_result.get("functions", []):
                func_id = f"{file_path}::{func['name']}"
                if func_id not in seen_functions:
                    seen_functions.add(func_id)
                    metrics_data.append({
                        "file": file_name,
                        "type": "function",
                        "name": func["name"],
                        "complexity": func.get("complexity", 1),
                        "start_line": func.get("start_line", 0),
                        "end_line": func.get("end_line", 0),
                        "has_docstring": func.get("has_docstring", False)
                    })
            
            # Class methods
            for cls in file_result.get("classes", []):
                for method in cls.get("methods", []):
                    func_id = f"{file_path}::{cls['name']}.{method['name']}"
                    if func_id not in seen_functions:
                        seen_functions.add(func_id)
                        metrics_data.append({
                            "file": file_name,
                            "type": "method",
                            "class": cls["name"],
                            "name": method["name"],
                            "complexity": method.get("complexity", 1),
                            "start_line": method.get("start_line", 0),
                            "end_line": method.get("end_line", 0),
                            "has_docstring": method.get("has_docstring", False)
                        })
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        
        total_funcs = len(metrics_data)
        avg_complexity = sum(m["complexity"] for m in metrics_data) / total_funcs if total_funcs > 0 else 0
        high_complexity = sum(1 for m in metrics_data if m["complexity"] > 10)
        documented = sum(1 for m in metrics_data if m["has_docstring"])
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🎯</div>
                <div class="metric-value">{total_funcs}</div>
                <div class="metric-label">Total Items</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📈</div>
                <div class="metric-value">{avg_complexity:.1f}</div>
                <div class="metric-label">Avg Complexity</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">⚠️</div>
                <div class="metric-value">{high_complexity}</div>
                <div class="metric-label">High Complexity</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📝</div>
                <div class="metric-value">{documented}</div>
                <div class="metric-label">Documented</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed metrics table
        st.markdown('<div class="section-header">📋 Detailed Function Metrics</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card-container">
            <p style="color: #94a3b8; margin-bottom: 1rem;">
                Showing metrics for all functions and methods in the scanned project. Each function appears exactly once.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display as formatted JSON with syntax highlighting
        st.json(metrics_data, expanded=False)
        
        # Download button
        if st.button("📥 Download Metrics Data", use_container_width=True):
            metrics_json = json.dumps(metrics_data, indent=2)
            st.download_button(
                label="💾 Save Metrics JSON",
                data=metrics_json,
                file_name="code_metrics.json",
                mime="application/json",
                use_container_width=True
            )

elif st.session_state.view == "Validation":
    st.markdown('<div class="section-header">✅ PEP 257 Validation</div>', unsafe_allow_html=True)
    
    if not st.session_state.scan_results:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">⚠️ No Scan Results</h3>
            <p>Please run a project scan from the sidebar to validate code.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Run validation
        with st.spinner("🔍 Validating code against PEP 257..."):
            validation_report = validate_project(st.session_state.scan_results)
        
        # Store in session state
        st.session_state.validation_report = validation_report
        
        # Metrics row
        col1, col2 = st.columns(2)
        
        with col1:
            compliance = validation_report.get('compliance_percentage', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">✅</div>
                <div class="metric-value">{compliance:.1f}%</div>
                <div class="metric-label">PEP 257 Compliant</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            violations = validation_report.get('total_violations', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">⚠️</div>
                <div class="metric-value">{violations}</div>
                <div class="metric-label">Violations Found</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Compliance chart
        st.markdown('<div class="section-header">📊 Compliance vs Violations</div>', unsafe_allow_html=True)
        
        compliant = validation_report.get('compliant_items', 0)
        total = validation_report.get('total_items', 1)
        non_compliant = total - compliant
        
        # Create chart data
        chart_col1, chart_col2 = st.columns([2, 1])
        
        with chart_col1:
            try:
                import plotly.graph_objects as go
                
                fig = go.Figure(data=[
                    go.Bar(name='Compliant', x=['Functions & Classes'], y=[compliant], 
                           marker_color='rgb(16, 185, 129)'),
                    go.Bar(name='Violations', x=['Functions & Classes'], y=[non_compliant], 
                           marker_color='rgb(239, 68, 68)')
                ])
                
                fig.update_layout(
                    barmode='group',
                    title='Code Compliance Overview',
                    yaxis_title='Count',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30, 41, 59, 0.5)',
                    font=dict(color='#e2e8f0'),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                st.warning("📊 Install plotly for chart visualization: `pip install plotly`")
                st.markdown(f"""
                <div class="card-container">
                    <h3 style="margin-top: 0; color: #a5b4fc;">📊 Compliance Overview</h3>
                    <p style="color: #059669; font-size: 1.2rem;">✓ Compliant: {compliant}</p>
                    <p style="color: #dc2626; font-size: 1.2rem;">✗ Non-Compliant: {non_compliant}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with chart_col2:
            st.markdown("""
            <div class="card-container">
                <h3 style="margin-top: 0; color: #a5b4fc;">📈 Summary</h3>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <p style="color: #94a3b8; font-size: 1rem; margin: 0.5rem 0;">
                    <strong style="color: #059669;">✓ Compliant:</strong> {compliant}
                </p>
                <p style="color: #94a3b8; font-size: 1rem; margin: 0.5rem 0;">
                    <strong style="color: #dc2626;">✗ Non-Compliant:</strong> {non_compliant}
                </p>
                <p style="color: #94a3b8; font-size: 1rem; margin: 0.5rem 0;">
                    <strong style="color: #4f46e5;">Total Items:</strong> {total}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Violations list
        st.markdown('<div class="section-header">🔍 Violation Details</div>', unsafe_allow_html=True)
        
        violations_list = validation_report.get('violations', [])
        
        
        if not violations_list:
            st.markdown("""
            <div class="info-box">
                <h3 style="margin-top: 0;">🎉 No Violations Found!</h3>
                <p>Your code is fully compliant with PEP 257 docstring conventions.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Group violations by file
            violations_by_file = {}
            for v in violations_list:
                file = v.get('file', 'unknown')
                if file not in violations_by_file:
                    violations_by_file[file] = []
                violations_by_file[file].append(v)
            
            # Display violations by file
            for file_path, file_violations in violations_by_file.items():
                file_name = file_path.split('/')[-1] if '/' in file_path else file_path
                
                st.markdown(f"""
                <style>
                    div[data-testid="stExpander"] details summary p {{
                        color: #1e293b !important;
                        font-weight: 600 !important;
                        font-size: 1rem !important;
                    }}
                </style>
                """, unsafe_allow_html=True)
                with st.expander(f"📄 {file_name} ({len(file_violations)} violations)", expanded=True):
                    for v in file_violations:
                        code = v.get('code', 'Unknown')
                        line = v.get('line', 0)
                        message = v.get('message', 'No message')
                        
                        # Color code based on severity
                        if code.startswith('D1'):  # Missing docstrings
                            color = '#dc2626'
                            icon = '🔴'
                        elif code.startswith('D2'):  # Formatting issues
                            color = '#d97706'
                            icon = '🟡'
                        elif code.startswith('D3'):  # Quote style
                            color = '#d97706'
                            icon = '🟡'
                        else:  # Content issues
                            color = '#3b82f6'
                            icon = '🔵'
                        
                        st.markdown(f"""
                        <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid {color}; 
                                    padding: 1rem; margin: 0.5rem 0; border-radius: 8px;">
                            <p style="margin: 0; color: #e2e8f0;">
                                {icon} <strong style="color: {color};">{code}</strong> (line {line}): {message.split(':', 1)[-1].strip() if ':' in message else message}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Download button
        st.markdown("---")
        if st.button("📥 Download Validation Report", use_container_width=True):
            report_json = json.dumps(validation_report, indent=2)
            st.download_button(
                label="💾 Save Validation JSON",
                data=report_json,
                file_name="pep257_validation_report.json",
                mime="application/json",
                use_container_width=True
            )