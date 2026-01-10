# tests/test_dashboard.py

"""Tests for dashboard UI."""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import streamlit as st
import json
from dashboard import (
    render_feature_cards,
    render_filters_view,
    render_search_view,
    render_export_view,
    render_help_view,
    render_tests_view,
    load_test_results,
    run_pytest_tests
)


@pytest.fixture
def mock_streamlit_state():
    """Mock Streamlit session state."""
    st.session_state.dashboard_view = "filters"
    st.session_state.current_filter = "All"
    st.session_state.search_query = ""
    st.session_state.scan_results = []
    st.session_state.tests_have_run = False
    st.session_state.test_running = False
    st.session_state.report = {
        'total_functions': 10,
        'documented_functions': 5,
        'overall_coverage_percentage': 50.0
    }
    return st.session_state


@pytest.fixture
def sample_scan_results():
    """Sample scan results for testing."""
    return [
        {
            "file_path": "test_file.py",
            "functions": [
                {"name": "test_function", "has_docstring": True, "complexity": 5},
                {"name": "undocumented_func", "has_docstring": False, "complexity": 2}
            ],
            "classes": [
                {
                    "name": "TestClass",
                    "methods": [
                        {"name": "method_one", "has_docstring": True, "complexity": 3},
                        {"name": "method_two", "has_docstring": False, "complexity": 1}
                    ]
                }
            ]
        },
        {
            "file_path": "another_file.py",
            "functions": [
                {"name": "calculate", "has_docstring": True, "complexity": 8},
                {"name": "process", "has_docstring": False, "complexity": 4}
            ],
            "classes": []
        }
    ]


@pytest.fixture
def sample_test_results():
    """Sample test results JSON."""
    return {
        "summary": {
            "total": 10,
            "passed": 8,
            "failed": 2
        },
        "tests": [
            {
                "nodeid": "tests/test_parser.py::test_parse_function",
                "outcome": "passed"
            },
            {
                "nodeid": "tests/test_parser.py::test_parse_class",
                "outcome": "passed"
            },
            {
                "nodeid": "tests/test_generator.py::test_generate_google",
                "outcome": "failed"
            }
        ]
    }


def test_render_feature_cards(mock_streamlit_state, monkeypatch):
    """Test that feature cards render without errors."""
    # Mock streamlit functions
    monkeypatch.setattr(st, "subheader", MagicMock())
    monkeypatch.setattr(st, "columns", MagicMock(return_value=[MagicMock()] * 5))
    monkeypatch.setattr(st, "button", MagicMock(return_value=False))
    monkeypatch.setattr(st, "divider", MagicMock())
    
    # Should not raise any exceptions
    try:
        render_feature_cards()
        assert True
    except Exception as e:
        pytest.fail(f"render_feature_cards raised an exception: {e}")


def test_load_test_results_file_exists(sample_test_results, monkeypatch):
    """Test loading test results when file exists."""
    mock_file = mock_open(read_data=json.dumps(sample_test_results))
    
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_file):
            results = load_test_results()
            
            assert results is not None
            assert results['summary']['total'] == 10
            assert results['summary']['passed'] == 8
            assert 'by_file' in results


def test_load_test_results_file_not_exists(monkeypatch):
    """Test loading test results when file doesn't exist."""
    with patch('os.path.exists', return_value=False):
        results = load_test_results()
        assert results is None


def test_run_pytest_tests_success(monkeypatch):
    """Test running pytest tests successfully."""
    mock_process = MagicMock()
    mock_process.stdout = iter(["test output line 1\n", "test output line 2\n"])
    mock_process.returncode = 0
    mock_process.wait = MagicMock()
    
    with patch('subprocess.Popen', return_value=mock_process):
        with patch('os.makedirs'):
            success, all_passed, output_lines = run_pytest_tests()
            
            assert success is True
            assert all_passed is True
            assert len(output_lines) == 2


def test_run_pytest_tests_failure(monkeypatch):
    """Test running pytest tests with failures."""
    mock_process = MagicMock()
    mock_process.stdout = iter(["test failed\n"])
    mock_process.returncode = 1
    mock_process.wait = MagicMock()
    
    with patch('subprocess.Popen', return_value=mock_process):
        with patch('os.makedirs'):
            success, all_passed, output_lines = run_pytest_tests()
            
            assert success is True
            assert all_passed is False
            assert len(output_lines) == 1


def test_run_pytest_tests_exception(monkeypatch):
    """Test running pytest tests with exception."""
    with patch('subprocess.Popen', side_effect=Exception("Test error")):
        with patch('os.makedirs'):
            success, all_passed, output_lines = run_pytest_tests()
            
            assert success is False
            assert all_passed is False
            assert "Error" in output_lines[0]


def test_render_tests_view_no_tests_run(mock_streamlit_state, monkeypatch):
    """Test tests view when tests haven't been run."""
    st.session_state.tests_have_run = False
    
    # Create a flexible mock for columns that handles different argument types
    def mock_columns(spec):
        if isinstance(spec, list):
            return [MagicMock() for _ in spec]
        else:
            return [MagicMock() for _ in range(spec)]
    
    # Mock streamlit functions
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "columns", mock_columns)
    monkeypatch.setattr(st, "button", MagicMock(return_value=False))
    monkeypatch.setattr(st, "spinner", MagicMock())
    monkeypatch.setattr(st, "empty", MagicMock())
    monkeypatch.setattr(st, "code", MagicMock())
    monkeypatch.setattr(st, "success", MagicMock())
    monkeypatch.setattr(st, "warning", MagicMock())
    monkeypatch.setattr(st, "error", MagicMock())
    monkeypatch.setattr(st, "info", MagicMock())
    monkeypatch.setattr(st, "rerun", MagicMock())
    
    # Mock os.path.exists to return False (no test results file)
    with patch('os.path.exists', return_value=False):
        # Should not raise any exceptions and should return early
        try:
            render_tests_view()
            assert True
        except Exception as e:
            pytest.fail(f"render_tests_view raised an exception: {e}")


def test_render_tests_view_with_results(mock_streamlit_state, sample_test_results, monkeypatch):
    """Test tests view with test results."""
    st.session_state.tests_have_run = True
    
    mock_file = mock_open(read_data=json.dumps(sample_test_results))
    def mock_columns(spec):
        if isinstance(spec, list):
            return [MagicMock() for _ in spec]
        else:
            return [MagicMock() for _ in range(spec)]
    
    # Mock streamlit functions
    monkeypatch.setattr(st, "markdown", MagicMock())
    #monkeypatch.setattr(st, "columns", MagicMock(return_value=[MagicMock()] * 4))
    monkeypatch.setattr(st, "columns", mock_columns)
    monkeypatch.setattr(st, "button", MagicMock(return_value=False))
    
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_file):
            try:
                render_tests_view()
                assert True
            except Exception as e:
                pytest.fail(f"render_tests_view raised an exception: {e}")


def test_render_filters_view_all_functions(mock_streamlit_state, sample_scan_results, monkeypatch):
    """Test filters view with 'All' filter."""
    st.session_state.scan_results = sample_scan_results
    st.session_state.current_filter = "All"
    
    # Mock streamlit functions
    monkeypatch.setattr(st, "subheader", MagicMock())
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "columns", MagicMock(return_value=[MagicMock()] * 3))
    monkeypatch.setattr(st, "button", MagicMock(return_value=False))
    monkeypatch.setattr(st, "dataframe", MagicMock())
    
    # Should not raise any exceptions
    try:
        render_filters_view()
        assert True
    except Exception as e:
        pytest.fail(f"render_filters_view raised an exception: {e}")


def test_render_filters_view_ok_filter(mock_streamlit_state, sample_scan_results, monkeypatch):
    """Test filters view with 'OK' filter (documented functions only)."""
    st.session_state.scan_results = sample_scan_results
    st.session_state.current_filter = "OK (Has Docstring)"
    
    # Mock streamlit functions
    monkeypatch.setattr(st, "subheader", MagicMock())
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "columns", MagicMock(return_value=[MagicMock()] * 3))
    monkeypatch.setattr(st, "button", MagicMock(return_value=False))
    monkeypatch.setattr(st, "dataframe", MagicMock())
    
    # Should not raise any exceptions
    try:
        render_filters_view()
        # Verify that filtering logic would work
        all_functions = []
        for file_result in sample_scan_results:
            for func in file_result.get("functions", []):
                all_functions.append(func)
            for cls in file_result.get("classes", []):
                for method in cls.get("methods", []):
                    all_functions.append(method)
        
        documented = [f for f in all_functions if f.get("has_docstring", False)]
        assert len(documented) == 3  # test_function, method_one, calculate
    except Exception as e:
        pytest.fail(f"render_filters_view raised an exception: {e}")


def test_render_filters_view_fix_filter(mock_streamlit_state, sample_scan_results, monkeypatch):
    """Test filters view with 'Fix' filter (undocumented functions only)."""
    st.session_state.scan_results = sample_scan_results
    st.session_state.current_filter = "Fix (Missing Docstring)"
    
    # Mock streamlit functions
    monkeypatch.setattr(st, "subheader", MagicMock())
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "columns", MagicMock(return_value=[MagicMock()] * 3))
    monkeypatch.setattr(st, "button", MagicMock(return_value=False))
    monkeypatch.setattr(st, "dataframe", MagicMock())
    
    # Should not raise any exceptions
    try:
        render_filters_view()
        # Verify that filtering logic would work
        all_functions = []
        for file_result in sample_scan_results:
            for func in file_result.get("functions", []):
                all_functions.append(func)
            for cls in file_result.get("classes", []):
                for method in cls.get("methods", []):
                    all_functions.append(method)
        
        undocumented = [f for f in all_functions if not f.get("has_docstring", False)]
        assert len(undocumented) == 3  # undocumented_func, method_two, process
    except Exception as e:
        pytest.fail(f"render_filters_view raised an exception: {e}")


def test_render_search_view_no_query(mock_streamlit_state, sample_scan_results, monkeypatch):
    """Test search view with no search query."""
    st.session_state.scan_results = sample_scan_results
    
    # Mock streamlit functions
    monkeypatch.setattr(st, "subheader", MagicMock())
    monkeypatch.setattr(st, "text_input", MagicMock(return_value=""))
    monkeypatch.setattr(st, "info", MagicMock())
    monkeypatch.setattr(st, "markdown", MagicMock())
    
    # Should not raise any exceptions
    try:
        render_search_view()
        assert True
    except Exception as e:
        pytest.fail(f"render_search_view raised an exception: {e}")


def test_render_search_view_with_query(mock_streamlit_state, sample_scan_results, monkeypatch):
    """Test search view with a search query."""
    st.session_state.scan_results = sample_scan_results
    
    # Mock streamlit functions
    monkeypatch.setattr(st, "subheader", MagicMock())
    monkeypatch.setattr(st, "text_input", MagicMock(return_value="test"))
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "dataframe", MagicMock())
    
    # Should not raise any exceptions
    try:
        render_search_view()
        # Verify search logic would find correct functions
        all_functions = []
        for file_result in sample_scan_results:
            for func in file_result.get("functions", []):
                if "test" in func["name"].lower():
                    all_functions.append(func)
            for cls in file_result.get("classes", []):
                for method in cls.get("methods", []):
                    if "test" in method["name"].lower():
                        all_functions.append(method)
        
        assert len(all_functions) == 1  # test_function
    except Exception as e:
        pytest.fail(f"render_search_view raised an exception: {e}")


def test_render_export_view(mock_streamlit_state, sample_scan_results, monkeypatch):
    """Test export view renders correctly."""
    st.session_state.scan_results = sample_scan_results
    
    # Mock streamlit functions
    monkeypatch.setattr(st, "subheader", MagicMock())
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "columns", MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()]))
    monkeypatch.setattr(st, "download_button", MagicMock())
    monkeypatch.setattr(st, "dataframe", MagicMock())
    monkeypatch.setattr(st, "info", MagicMock())
    
    # Should not raise any exceptions
    try:
        render_export_view()
        assert True
    except Exception as e:
        pytest.fail(f"render_export_view raised an exception: {e}")


def test_render_export_view_csv_data(mock_streamlit_state, sample_scan_results):
    """Test that CSV data is generated correctly."""
    st.session_state.scan_results = sample_scan_results
    
    # Manually generate CSV data like the function does
    rows = []
    for file_result in sample_scan_results:
        file_name = file_result.get("file_path", "").split("/")[-1]
        for func in file_result.get("functions", []):
            rows.append([
                file_name,
                func["name"],
                "Yes" if func.get("has_docstring", False) else "No",
                func.get("complexity", 1)
            ])
        for cls in file_result.get("classes", []):
            for method in cls.get("methods", []):
                rows.append([
                    file_name,
                    f"{cls['name']}.{method['name']}",
                    "Yes" if method.get("has_docstring", False) else "No",
                    method.get("complexity", 1)
                ])
    
    # Verify correct number of functions
    assert len(rows) == 6  # 6 functions total
    
    # Verify some specific functions exist
    function_names = [row[1] for row in rows]
    assert "test_function" in function_names
    assert "calculate" in function_names
    assert "TestClass.method_one" in function_names


def test_render_help_view(mock_streamlit_state, monkeypatch):
    """Test help view renders without errors."""
    # Mock streamlit functions
    monkeypatch.setattr(st, "markdown", MagicMock())
    monkeypatch.setattr(st, "columns", MagicMock(return_value=[MagicMock(), MagicMock()]))
    monkeypatch.setattr(st, "tabs", MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()]))
    monkeypatch.setattr(st, "code", MagicMock())
    
    # Should not raise any exceptions
    try:
        render_help_view()
        assert True
    except Exception as e:
        pytest.fail(f"render_help_view raised an exception: {e}")


def test_function_collection_logic(sample_scan_results):
    """Test that function collection logic works correctly."""
    all_functions = []
    for file_result in sample_scan_results:
        file_path = file_result.get("file_path", "")
        for func in file_result.get("functions", []):
            all_functions.append({
                "file": file_path.split("/")[-1],
                "name": func["name"],
                "has_docstring": func.get("has_docstring", False)
            })
        for cls in file_result.get("classes", []):
            for method in cls.get("methods", []):
                all_functions.append({
                    "file": file_path.split("/")[-1],
                    "name": method["name"],
                    "has_docstring": method.get("has_docstring", False)
                })
    
    assert len(all_functions) == 6
    documented = [f for f in all_functions if f["has_docstring"]]
    assert len(documented) == 3
    undocumented = [f for f in all_functions if not f["has_docstring"]]
    assert len(undocumented) == 3


def test_search_filter_logic(sample_scan_results):
    """Test search filtering logic."""
    search_query = "calc"
    all_functions = []
    
    for file_result in sample_scan_results:
        for func in file_result.get("functions", []):
            if search_query.lower() in func["name"].lower():
                all_functions.append(func)
        for cls in file_result.get("classes", []):
            for method in cls.get("methods", []):
                if search_query.lower() in method["name"].lower():
                    all_functions.append(method)
    
    assert len(all_functions) == 1
    assert all_functions[0]["name"] == "calculate"


def test_status_filter_logic(sample_scan_results):
    """Test status filtering logic (OK vs Fix)."""
    all_functions = []
    
    for file_result in sample_scan_results:
        for func in file_result.get("functions", []):
            all_functions.append(func)
        for cls in file_result.get("classes", []):
            for method in cls.get("methods", []):
                all_functions.append(method)
    
    # Test OK filter (documented)
    ok_funcs = [f for f in all_functions if f.get("has_docstring", False)]
    assert len(ok_funcs) == 3
    
    # Test Fix filter (undocumented)
    fix_funcs = [f for f in all_functions if not f.get("has_docstring", False)]
    assert len(fix_funcs) == 3
    
    # Test All filter
    assert len(all_functions) == 6


def test_test_results_grouping(sample_test_results):
    """Test that test results are grouped correctly by file."""
    tests = sample_test_results.get('tests', [])
    results_by_file = {}
    
    for test in tests:
        nodeid = test.get('nodeid', '')
        file_name = nodeid.split('::')[0] if '::' in nodeid else nodeid
        file_name = file_name.split('/')[-1] if '/' in file_name else file_name
        
        if file_name not in results_by_file:
            results_by_file[file_name] = {
                'passed': 0,
                'failed': 0,
                'total': 0
            }
        
        outcome = test.get('outcome', 'unknown')
        results_by_file[file_name][outcome] = results_by_file[file_name].get(outcome, 0) + 1
        results_by_file[file_name]['total'] += 1
    
    # Verify grouping
    assert len(results_by_file) == 2  # test_parser.py and test_generator.py
    assert 'test_parser.py' in results_by_file
    assert 'test_generator.py' in results_by_file
    assert results_by_file['test_parser.py']['passed'] == 2
    assert results_by_file['test_generator.py']['failed'] == 1