"""
Dashboard module for AI Code Reviewer.

Clean, professional Streamlit UI with test results integration.
"""

import streamlit as st
import json
import os
import pandas as pd


# -------------------------------------------------
# Feature Navigation - UPDATED with Tests option
# -------------------------------------------------
def render_feature_cards():
    st.subheader("🧭 Dashboard Navigation")

    # Ensure state exists
    if "dashboard_view" not in st.session_state:
        st.session_state.dashboard_view = "filters"

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🔍 Filters", use_container_width=True):
            st.session_state.dashboard_view = "filters"

    with col2:
        if st.button("🔎 Search", use_container_width=True):
            st.session_state.dashboard_view = "search"
    
    with col3:
        if st.button("🧪 Tests", use_container_width=True):
            st.session_state.dashboard_view = "tests"

    with col4:
        if st.button("📦 Export", use_container_width=True):
            st.session_state.dashboard_view = "export"

    with col5:
        if st.button("ℹ️ Help", use_container_width=True):
            st.session_state.dashboard_view = "help"

    st.divider()


# -------------------------------------------------
# Helper function to load test results
# -------------------------------------------------
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
            # Extract file name
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
# -------------------------------------------------
# Helper function to run pytest tests
# -------------------------------------------------
def run_pytest_tests():
    """Run pytest and generate JSON report with live output."""
    import subprocess
    
    try:
        # Ensure the reports directory exists
        os.makedirs("storage/reports", exist_ok=True)
        
        # Run pytest with JSON report
        process = subprocess.Popen(
            [
                "pytest",
                "-v",
                "--json-report",
                "--json-report-file=storage/reports/pytest_results.json",
                "tests/"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output line by line
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
        
        process.wait()
        
        return True, process.returncode == 0, output_lines
    except Exception as e:
        return False, False, [f"Error: {str(e)}"]

# -------------------------------------------------
# NEW: Test Results View
# -------------------------------------------------
# -------------------------------------------------
# NEW: Test Results View
# -------------------------------------------------
def render_tests_view():
    st.markdown('<div class="section-header">🧪 Test Results</div>', unsafe_allow_html=True)
    
    # Run Tests Button
    st.markdown("""
    <div style="background: rgba(99, 102, 241, 0.08); border-left: 4px solid #6366f1; 
                padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
        <p style="color: #e2e8f0; line-height: 1.7; margin: 0;">
            Click the button below to run all pytest tests. Test results will be displayed with detailed metrics and visualizations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        run_button = st.button("🧪 Run All Tests", use_container_width=True, type="primary", key="run_tests_dashboard")
    
    with col2:
        if "test_running" in st.session_state and st.session_state.test_running:
            st.info("🔄 Tests are running... Please wait.")
    
    # Run tests if button clicked
    if run_button:
        st.session_state.test_running = True
        
        with st.spinner("🔄 Running tests..."):
            # Create placeholder for live output
            output_placeholder = st.empty()
            
            success, all_passed, output_lines = run_pytest_tests()
            
            # Show live output
            with output_placeholder.container():
                st.markdown('<h3 style="color: #a5b4fc; margin-top: 1rem;">📋 Test Output</h3>', unsafe_allow_html=True)
                
                # Display output in a code block
                output_text = "".join(output_lines)
                st.code(output_text, language="text")
            
            if success:
                if all_passed:
                    st.success("✅ All tests passed!")
                else:
                    st.warning("⚠️ Some tests failed. Check results below.")
                st.session_state.tests_have_run = True
            else:
                st.error("❌ Failed to run tests")
        
        st.session_state.test_running = False
        st.rerun()
    
    st.markdown("---")
    
    
    # Try to load existing test results first
    if "tests_have_run" not in st.session_state:
        st.session_state.tests_have_run = False
    # Check if test results file exists
    if os.path.exists("storage/reports/pytest_results.json"):
        st.session_state.tests_have_run = True
    
    # Load test results
    test_results = load_test_results()
    
    if not test_results:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; 
                    padding: 1.5rem; border-radius: 12px; margin: 2rem 0;">
            <h3 style="margin-top: 0; color: #fca5a5;">⚠️ No Test Results Found</h3>
            <p style="color: #e2e8f0; line-height: 1.7;">
                No test results file found at <code>storage/reports/pytest_results.json</code>. 
                Click "Run All Tests" above to execute tests and generate results.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    summary = test_results['summary']
    by_file = test_results['by_file']
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_tests = summary.get('total', 0)
    passed_tests = summary.get('passed', 0)
    failed_tests = summary.get('failed', 0)
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🧪</div>
            <div class="metric-value">{total_tests}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">✅</div>
            <div class="metric-value">{passed_tests}</div>
            <div class="metric-label">Passed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">❌</div>
            <div class="metric-value">{failed_tests}</div>
            <div class="metric-label">Failed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-value">{pass_rate:.1f}%</div>
            <div class="metric-label">Pass Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Test results by file - Bar chart
    col_chart, col_list = st.columns([2, 1])
    
    with col_chart:
        st.markdown('<h3 style="color: #a5b4fc; margin-bottom: 1rem;">📊 Test Results by File</h3>', unsafe_allow_html=True)
        
        try:
            import plotly.graph_objects as go
            
            # Prepare data for chart
            file_names = list(by_file.keys())
            passed_counts = [by_file[f].get('passed', 0) for f in file_names]
            failed_counts = [by_file[f].get('failed', 0) for f in file_names]
            
            # Shorten file names for display
            display_names = [f.replace('test_', '').replace('.py', '') for f in file_names]
            
            fig = go.Figure(data=[
                go.Bar(
                    name='Failed',
                    x=display_names,
                    y=failed_counts,
                    marker_color='rgb(239, 68, 68)',
                    text=failed_counts,
                    textposition='inside'
                ),
                go.Bar(
                    name='Passed',
                    x=display_names,
                    y=passed_counts,
                    marker_color='rgb(16, 185, 129)',
                    text=passed_counts,
                    textposition='inside'
                )
            ])
            
            fig.update_layout(
                barmode='stack',
                title='',
                xaxis_title='',
                yaxis_title='Number of Tests',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30, 41, 59, 0.5)',
                font=dict(color='#e2e8f0', size=12),
                height=350,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=50, r=20, t=40, b=100)
            )
            
            fig.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.warning("📊 Install plotly for chart visualization: `pip install plotly`")
    
    with col_list:
        st.markdown('<h3 style="color: #a5b4fc; margin-bottom: 1rem;">📋 Test Suites</h3>', unsafe_allow_html=True)
        
        # Display test suites as colored bars
        for file_name, results in by_file.items():
            total = results['total']
            passed = results.get('passed', 0)
            failed = results.get('failed', 0)
            
            # Determine color based on pass/fail
            if failed == 0:
                bg_color = 'rgba(16, 185, 129, 0.15)'
                border_color = '#10b981'
                icon = '✅'
            elif failed < total:
                bg_color = 'rgba(245, 158, 11, 0.15)'
                border_color = '#f59e0b'
                icon = '⚠️'
            else:
                bg_color = 'rgba(239, 68, 68, 0.15)'
                border_color = '#ef4444'
                icon = '❌'
            
            # Clean file name for display
            display_name = file_name.replace('test_', '').replace('.py', '').replace('_', ' ').title()
            
            st.markdown(f"""
            <div style="background: {bg_color}; border-left: 4px solid {border_color}; 
                        padding: 0.875rem 1.25rem; margin: 0.5rem 0; border-radius: 8px;
                        display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #e2e8f0; font-weight: 600;">
                    {icon} {display_name}
                </span>
                <span style="color: #94a3b8; font-size: 0.875rem;">
                    {passed}/{total} passed
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")


# -------------------------------------------------
# Filters View (unchanged)
# -------------------------------------------------
def render_filters_view():
    st.subheader("🔍 Filter Functions by Docstring Status")

    if "scan_results" not in st.session_state:
        st.warning("No scan results available.")
        return

    st.markdown("""
    <style>
    div[data-testid="column"] button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 2px solid rgba(148, 163, 184, 0.3) !important;
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="column"] button[kind="secondary"]:hover {
        background: rgba(99, 102, 241, 0.15) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        color: #e2e8f0 !important;
        transform: translateY(-2px);
    }
    
    div[data-testid="column"] button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h3 style="color: #a5b4fc; margin-top: 1rem; margin-bottom: 1rem;">📋 Select Documentation Status</h3>', unsafe_allow_html=True)
    
    if "current_filter" not in st.session_state:
        st.session_state.current_filter = "All"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 All Functions", 
                     use_container_width=True, 
                     type="primary" if st.session_state.current_filter == "All" else "secondary",
                     key="filter_all"):
            st.session_state.current_filter = "All"
            st.rerun()
    
    with col2:
        if st.button("✅ Has Docstring", 
                     use_container_width=True, 
                     type="primary" if st.session_state.current_filter == "OK (Has Docstring)" else "secondary",
                     key="filter_ok"):
            st.session_state.current_filter = "OK (Has Docstring)"
            st.rerun()
    
    with col3:
        if st.button("❌ Missing Docstring", 
                     use_container_width=True, 
                     type="primary" if st.session_state.current_filter == "Fix (Missing Docstring)" else "secondary",
                     key="filter_fix"):
            st.session_state.current_filter = "Fix (Missing Docstring)"
            st.rerun()
    
    status = st.session_state.current_filter
    
    st.markdown("<br>", unsafe_allow_html=True)

    rows = []

    for file in st.session_state.scan_results:
        file_name = os.path.basename(file.get("file_path", ""))

        for fn in file.get("functions", []):
            rows.append({
                "File": file_name,
                "Function": fn["name"],
                "Docstring": fn.get("has_docstring", False)
            })

        for cls in file.get("classes", []):
            for m in cls.get("methods", []):
                rows.append({
                    "File": file_name,
                    "Function": f"{cls['name']}.{m['name']}",
                    "Docstring": m.get("has_docstring", False)
                })

    df = pd.DataFrame(rows)

    if status.startswith("OK"):
        df_filtered = df[df["Docstring"] == True]
    elif status.startswith("Fix"):
        df_filtered = df[df["Docstring"] == False]
    else:
        df_filtered = df

    st.markdown('<h3 style="color: #a5b4fc; margin-top: 1.5rem; margin-bottom: 1rem;">📊 Filter Results</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.15); padding: 1.5rem; border-radius: 12px; 
                    text-align: center; border: 2px solid rgba(99, 102, 241, 0.4);">
            <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">
                Total Functions
            </div>
            <div style="font-size: 2.5rem; font-weight: bold; color: #a5b4fc;">
                {len(df)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.15); padding: 1.5rem; border-radius: 12px; 
                    text-align: center; border: 2px solid rgba(16, 185, 129, 0.4);">
            <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">
                Showing
            </div>
            <div style="font-size: 2.5rem; font-weight: bold; color: #6ee7b7;">
                {len(df_filtered)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        percentage = (len(df_filtered) / len(df) * 100) if len(df) > 0 else 0
        st.markdown(f"""
        <div style="background: rgba(139, 92, 246, 0.15); padding: 1.5rem; border-radius: 12px; 
                    text-align: center; border: 2px solid rgba(139, 92, 246, 0.4);">
            <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">
                Percentage
            </div>
            <div style="font-size: 2.5rem; font-weight: bold; color: #c4b5fd;">
                {percentage:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if df_filtered.empty:
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.08); border-left: 4px solid #6366f1; 
                    padding: 1.5rem; border-radius: 12px; margin: 2rem 0;">
            <p style="margin: 0; color: #e2e8f0; font-size: 1rem;">
                ✨ No functions match the '<strong>{status}</strong>' filter.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        row_count = len(df_filtered)
        table_height = min(400, max(200, row_count * 35 + 38))
        
        st.markdown('<h3 style="color: #a5b4fc; margin-bottom: 1rem;">📋 Functions List</h3>', unsafe_allow_html=True)
        
        st.dataframe(
            df_filtered.replace({True: "✅ Yes", False: "❌ No"}),
            use_container_width=True,
            height=table_height
        )


# -------------------------------------------------
# Search View (unchanged)
# -------------------------------------------------
def render_search_view():
    st.subheader("🔎 Search Functions")

    if "scan_results" not in st.session_state:
        st.warning("No scan results available.")
        return

    query = st.text_input("Enter function or method name", placeholder="e.g., calculate, process, init")

    if not query:
        st.info("💡 Type a function name to start searching.")
        return

    results = []

    for file in st.session_state.scan_results:
        file_name = os.path.basename(file.get("file_path", ""))

        for fn in file.get("functions", []):
            if query.lower() in fn["name"].lower():
                results.append({
                    "File": file_name,
                    "Function": fn["name"],
                    "Docstring": fn.get("has_docstring", False)
                })

        for cls in file.get("classes", []):
            for m in cls.get("methods", []):
                if query.lower() in m["name"].lower():
                    results.append({
                        "File": file_name,
                        "Function": f"{cls['name']}.{m['name']}",
                        "Docstring": m.get("has_docstring", False)
                    })

    df = pd.DataFrame(results)

    st.markdown(f"### 📊 {len(df)} result(s) found for '{query}'")

    if df.empty:
        st.warning(f"❌ No functions matching '{query}' were found.")
    else:
        st.dataframe(
            df.replace({True: "✅ Yes", False: "❌ No"}),
            use_container_width=True,
            height=min(400, len(df) * 35 + 38)
        )

# -------------------------------------------------
# Export View (DO NOT RENAME) - FIXED VERSION
# -------------------------------------------------
def render_export_view():
    st.subheader("📦 Export Analysis Reports")

    if "scan_results" not in st.session_state or not st.session_state.scan_results:
        st.warning("⚠️ No data available for export. Please scan your project first.")
        return

    # ✅ FIX: Calculate metrics directly from scan_results in real-time
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
    
    missing_functions = total_functions - documented_functions

    # Display metrics with better styling
    st.markdown("### 📊 Project Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.1); padding: 1.5rem; border-radius: 12px; text-align: center; border: 2px solid rgba(99, 102, 241, 0.3);">
            <div style="font-size: 2.5rem; font-weight: bold; color: #6366f1;">{total_functions}</div>
            <div style="color: #94a3b8; margin-top: 0.5rem;">Total Functions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); padding: 1.5rem; border-radius: 12px; text-align: center; border: 2px solid rgba(16, 185, 129, 0.3);">
            <div style="font-size: 2.5rem; font-weight: bold; color: #10b981;">{documented_functions}</div>
            <div style="color: #94a3b8; margin-top: 0.5rem;">Documented</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.1); padding: 1.5rem; border-radius: 12px; text-align: center; border: 2px solid rgba(239, 68, 68, 0.3);">
            <div style="font-size: 2.5rem; font-weight: bold; color: #ef4444;">{missing_functions}</div>
            <div style="color: #94a3b8; margin-top: 0.5rem;">Missing</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📥 Download Reports")

    # Build report object for JSON export
    report = {
        "total_functions": total_functions,
        "documented_functions": documented_functions,
        "undocumented_functions": missing_functions,
        "coverage_percentage": (documented_functions / total_functions * 100) if total_functions > 0 else 0,
        "files": []
    }
    
    # Add file-level details
    for file in st.session_state.scan_results:
        file_info = {
            "file_path": file.get("file_path", ""),
            "functions": [],
            "classes": []
        }
        
        for fn in file.get("functions", []):
            file_info["functions"].append({
                "name": fn["name"],
                "has_docstring": fn.get("has_docstring", False),
                "complexity": fn.get("complexity", 1)
            })
        
        for cls in file.get("classes", []):
            class_info = {
                "name": cls["name"],
                "methods": []
            }
            for method in cls.get("methods", []):
                class_info["methods"].append({
                    "name": method["name"],
                    "has_docstring": method.get("has_docstring", False),
                    "complexity": method.get("complexity", 1)
                })
            file_info["classes"].append(class_info)
        
        report["files"].append(file_info)

    # JSON Export with better button styling
    json_data = json.dumps(report, indent=2)
    st.markdown("""
    <style>
    /* Fix download button visibility */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4) !important;
    }
    .stDownloadButton > button p {
        color: white !important;
        font-size: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.download_button(
        label="📄 Download JSON Report",
        data=json_data,
        file_name="docstring_report.json",
        mime="application/json",
        use_container_width=True,
        key="json_download"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # CSV Export
    rows = []
    for file in st.session_state.scan_results:
        fname = os.path.basename(file.get("file_path", ""))

        for fn in file.get("functions", []):
            rows.append([
                fname,
                fn["name"],
                "Yes" if fn.get("has_docstring", False) else "No",
                fn.get("complexity", 1)
            ])

        for cls in file.get("classes", []):
            for m in cls.get("methods", []):
                rows.append([
                    fname,
                    f"{cls['name']}.{m['name']}",
                    "Yes" if m.get("has_docstring", False) else "No",
                    m.get("complexity", 1)
                ])

    csv_df = pd.DataFrame(
        rows,
        columns=["File", "Function", "Has Docstring", "Complexity"]
    )

    csv_data = csv_df.to_csv(index=False)
    
    st.download_button(
        label="📊 Download CSV Report",
        data=csv_data,
        file_name="docstring_report.csv",
        mime="text/csv",
        use_container_width=True,
        key="csv_download"
    )

    # Show preview
    st.markdown("---")
    st.markdown("### 👀 Data Preview")
    st.dataframe(csv_df.head(10), use_container_width=True)
    if len(csv_df) > 10:
        st.info(f"Showing first 10 of {len(csv_df)} total rows")


# -------------------------------------------------
# Help View (DO NOT RENAME) - SIMPLIFIED VERSION
# -------------------------------------------------
def render_help_view():
    # Add tab styling first
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p {
        color: #6366f1 !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">📚 Complete Usage Guide</div>', unsafe_allow_html=True)
    
    # Feature Grid - Using Streamlit columns for reliability
    st.markdown("### 🎯 Core Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(99, 102, 241, 0.3); 
                    border-radius: 16px; padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem;">🔍</div>
                <h3 style="margin: 0; color: #06b6d4; font-size: 1.3rem;">Project Scanning</h3>
            </div>
            <ul style="color: #cbd5e1; line-height: 1.8; margin: 0; padding-left: 1.25rem;">
                <li>Recursively scans Python files in your project</li>
                <li>Parses functions, methods, and classes</li>
                <li>Extracts existing docstrings and signatures</li>
                <li>Calculates cyclomatic complexity metrics</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(16, 185, 129, 0.3); 
                    border-radius: 16px; padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem;">✅</div>
                <h3 style="margin: 0; color: #10b981; font-size: 1.3rem;">Review &amp; Apply Workflow</h3>
            </div>
            <ul style="color: #cbd5e1; line-height: 1.8; margin: 0; padding-left: 1.25rem;">
                <li>Side-by-side comparison view</li>
                <li>Detailed diff highlighting changes</li>
                <li>Accept: Writes docstring directly to your file</li>
                <li>Tracks accepted styles per function</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(99, 102, 241, 0.3); 
                    border-radius: 16px; padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem;">📊</div>
                <h3 style="margin: 0; color: #6366f1; font-size: 1.3rem;">Coverage Tracking</h3>
            </div>
            <ul style="color: #cbd5e1; line-height: 1.8; margin: 0; padding-left: 1.25rem;">
                <li>Real-time calculation of doc coverage %</li>
                <li>Tracks which functions have docstrings</li>
                <li>Provides overall project metrics</li>
                <li>Updates automatically after changes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(139, 92, 246, 0.3); 
                    border-radius: 16px; padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem;">🤖</div>
                <h3 style="margin: 0; color: #8b5cf6; font-size: 1.3rem;">AI Docstring Generation</h3>
            </div>
            <ul style="color: #cbd5e1; line-height: 1.8; margin: 0; padding-left: 1.25rem;">
                <li>Generates 3 styles: Google, NumPy, reST</li>
                <li>Uses Groq LLM API for intelligent suggestions</li>
                <li>Analyzes function signature and complexity</li>
                <li>Pre-generates all styles during scan</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(245, 158, 11, 0.3); 
                    border-radius: 16px; padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem;">📝</div>
                <h3 style="margin: 0; color: #f59e0b; font-size: 1.3rem;">Direct File Modification</h3>
            </div>
            <ul style="color: #cbd5e1; line-height: 1.8; margin: 0; padding-left: 1.25rem;">
                <li>Automatically finds function definition</li>
                <li>Replaces existing or inserts new docstring</li>
                <li>Preserves indentation and formatting</li>
                <li>Works with both functions and class methods</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(239, 68, 68, 0.3); 
                    border-radius: 16px; padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="font-size: 2.5rem;">🔍</div>
                <h3 style="margin: 0; color: #ef4444; font-size: 1.3rem;">PEP 257 Validation</h3>
            </div>
            <ul style="color: #cbd5e1; line-height: 1.8; margin: 0; padding-left: 1.25rem;">
                <li>Checks docstring compliance standards</li>
                <li>Identifies missing or malformed docstrings</li>
                <li>Provides detailed violation reports</li>
                <li>Groups violations by severity</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced Features Guide
    st.markdown('<div class="section-header">✨ Enhanced Features Guide</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(99, 102, 241, 0.2); 
                    border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;">
            <h3 style="margin: 0 0 1rem 0; color: #a5b4fc; display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.75rem;">🎯</span> Advanced Filters
            </h3>
            <p style="color: #cbd5e1; line-height: 1.7; margin: 0;">
                Filter functions by documentation status: <strong>All</strong>, <strong>Missing Docs</strong>, 
                or <strong>Documented</strong>. Quickly identify which parts of your codebase need attention. 
                Shows count and percentage of filtered results.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(99, 102, 241, 0.2); 
                    border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;">
            <h3 style="margin: 0 0 1rem 0; color: #a5b4fc; display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.75rem;">📥</span> Export Reports
            </h3>
            <p style="color: #cbd5e1; line-height: 1.7; margin: 0;">
                Download complete analysis reports in <strong>JSON</strong> (programmatic use) or 
                <strong>CSV</strong> (spreadsheets/Excel). Include coverage metrics, complexity scores, 
                and validation results for code reviews or CI/CD integration.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(99, 102, 241, 0.2); 
                    border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;">
            <h3 style="margin: 0 0 1rem 0; color: #a5b4fc; display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.75rem;">🔎</span> Search Functions
            </h3>
            <p style="color: #cbd5e1; line-height: 1.7; margin: 0;">
                Find specific functions by name across your entire project. Case-insensitive search helps 
                you quickly locate methods, classes, or functions. Perfect for large codebases with 
                hundreds of functions.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(99, 102, 241, 0.2); 
                    border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;">
            <h3 style="margin: 0 0 1rem 0; color: #a5b4fc; display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.75rem;">🧪</span> Testing Integration
            </h3>
            <p style="color: #cbd5e1; line-height: 1.7; margin: 0;">
                Run all pytest tests directly from the sidebar. View test results, pass rates, and 
                failures grouped by file. Ensure your documentation changes don't break existing 
                functionality.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Docstring Styles Reference
    st.markdown('<div class="section-header">📖 Docstring Styles Reference</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📗 Google Style", "📕 NumPy Style", "📙 reST Style"])
    
    with tab1:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(148, 163, 184, 0.2); 
                    border-radius: 16px; padding: 2rem; margin: 1rem 0;">
            <h3 style="margin-top: 0; color: #a5b4fc;">Google Style Docstrings</h3>
            <p style="color: #cbd5e1; line-height: 1.7;">
                Most popular and readable style. Used by Google, TensorFlow, and many open-source projects.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.code('''def example_function(param1, param2, param3=None):
    """Brief description of the function.
    
    More detailed explanation of what the function does,
    its behavior, and any important notes.
    
    Args:
        param1 (int): Description of param1.
        param2 (str): Description of param2.
        param3 (Optional[bool]): Description of optional param3.
            Defaults to None.
    
    Returns:
        dict: Description of the return value.
    
    Raises:
        ValueError: When param1 is negative.
        TypeError: When param2 is not a string.
    
    Example:
        >>> result = example_function(42, "hello")
        >>> print(result)
        {'status': 'success'}
    """
    pass
''', language='python')
    
    with tab2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(148, 163, 184, 0.2); 
                    border-radius: 16px; padding: 2rem; margin: 1rem 0;">
            <h3 style="margin-top: 0; color: #a5b4fc;">NumPy Style Docstrings</h3>
            <p style="color: #cbd5e1; line-height: 1.7;">
                Preferred by the scientific Python community. Used by NumPy, SciPy, and Pandas.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.code('''def example_function(param1, param2, param3=None):
    """Brief description of the function.
    
    More detailed explanation of what the function does,
    its behavior, and any important notes.
    
    Parameters
    ----------
    param1 : int
        Description of param1.
    param2 : str
        Description of param2.
    param3 : bool, optional
        Description of optional param3.
        The default is None.
    
    Returns
    -------
    dict
        Description of the return value.
    
    Raises
    ------
    ValueError
        When param1 is negative.
    TypeError
        When param2 is not a string.
    
    Examples
    --------
    >>> result = example_function(42, "hello")
    >>> print(result)
    {'status': 'success'}
    """
    pass
''', language='python')
    
    with tab3:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 2px solid rgba(148, 163, 184, 0.2); 
                    border-radius: 16px; padding: 2rem; margin: 1rem 0;">
            <h3 style="margin-top: 0; color: #a5b4fc;">reST Style Docstrings</h3>
            <p style="color: #cbd5e1; line-height: 1.7;">
                ReStructuredText style. Integrates well with Sphinx documentation generator.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.code('''def example_function(param1, param2, param3=None):
    """Brief description of the function.
    
    More detailed explanation of what the function does,
    its behavior, and any important notes.
    
    :param param1: Description of param1.
    :type param1: int
    :param param2: Description of param2.
    :type param2: str
    :param param3: Description of optional param3.
    :type param3: bool or None, optional
    :return: Description of the return value.
    :rtype: dict
    :raises ValueError: When param1 is negative.
    :raises TypeError: When param2 is not a string.
    
    Example::
    
        >>> result = example_function(42, "hello")
        >>> print(result)
        {'status': 'success'}
    """
    pass
''', language='python')
    
    st.markdown("---")
    
    # Final Tips
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%); 
                border: 2px solid rgba(99, 102, 241, 0.3); padding: 2rem; border-radius: 16px; 
                margin: 2rem 0; text-align: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🎓</div>
        <h3 style="margin: 0 0 1rem 0; color: #a5b4fc; font-size: 1.5rem;">Pro Tip</h3>
        <p style="color: #cbd5e1; line-height: 1.8; font-size: 1.1rem; margin: 0;">
            Use this tool as part of your development workflow! Run scans before commits to ensure 
            documentation coverage. Export reports for code reviews. Integrate validation checks 
            into your CI/CD pipeline for automated quality assurance.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid #6366f1; 
                padding: 1.5rem; border-radius: 12px; margin-top: 2rem;">
        <h3 style="margin-top: 0; color: #a5b4fc;">📚 Documentation Standards</h3>
        <p style="color: #e2e8f0; line-height: 1.7;">
            This tool follows <strong>PEP 257</strong> docstring conventions and supports 
            three popular styles: <strong>Google</strong>, <strong>NumPy</strong>, and <strong>reST</strong>.
            All generated docstrings are validated for compliance with Python's official documentation standards.
        </p>
    </div>
    """, unsafe_allow_html=True)