# tests/test_coverage_reporter.py

"""Tests for coverage reporter."""

from core.reporter.coverage_reporter import compute_coverage, write_report
from core.parser.python_parser import parse_path
import json
import os
import tempfile


def test_coverage_keys_exist():
    """Test coverage report structure."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed)
    
    # Check for keys that actually exist in the implementation
    assert "total_functions" in report
    assert "successfully_parsed" in report
    assert "total_parsing_errors" in report
    assert "overall_coverage_percentage" in report
    assert "files" in report


def test_coverage_file_stats():
    """Test per-file statistics in coverage report."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed)
    
    # Check files array structure
    assert isinstance(report["files"], list)
    
    if len(report["files"]) > 0:
        file_stat = report["files"][0]
        assert "file_path" in file_stat
        assert "total_functions" in file_stat
        assert "parsed_functions" in file_stat
        assert "parsing_errors" in file_stat
        assert "coverage_percentage" in file_stat


def test_coverage_calculation():
    """Test coverage percentage calculation from examples directory."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed)
    
    # Basic sanity checks
    assert report["total_functions"] >= 0
    assert report["successfully_parsed"] >= 0
    assert report["successfully_parsed"] <= report["total_functions"]
    assert 0 <= report["overall_coverage_percentage"] <= 100


def test_coverage_values_are_numbers():
    """Test that coverage values are proper numeric types."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed)
    
    assert isinstance(report["total_functions"], int)
    assert isinstance(report["successfully_parsed"], int)
    assert isinstance(report["total_parsing_errors"], int)
    assert isinstance(report["overall_coverage_percentage"], (int, float))


def test_file_level_coverage():
    """Test per-file coverage calculations."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed)
    
    for file_stat in report["files"]:
        # Each file should have valid coverage percentage
        assert 0 <= file_stat["coverage_percentage"] <= 100
        assert isinstance(file_stat["coverage_percentage"], (int, float))
        
        # Parsed functions should not exceed total functions
        assert file_stat["parsed_functions"] <= file_stat["total_functions"]
        
        # If no parsing errors, all functions should be parsed
        if file_stat["parsing_errors"] == 0:
            assert file_stat["parsed_functions"] == file_stat["total_functions"]


def test_empty_input_handling():
    """Test coverage computation with empty input."""
    report = compute_coverage([])
    
    assert report["total_functions"] == 0
    assert report["successfully_parsed"] == 0
    assert report["total_parsing_errors"] == 0
    assert report["overall_coverage_percentage"] == 0.0
    assert report["files"] == []


def test_write_report():
    """Test writing coverage report to JSON file."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    
    try:
        # Write report
        write_report(report, temp_path)
        
        # Verify file exists
        assert os.path.exists(temp_path)
        
        # Read and verify structure
        with open(temp_path, 'r', encoding='utf-8') as f:
            loaded_report = json.load(f)
        
        assert loaded_report == report
        assert "overall_coverage_percentage" in loaded_report
        assert "files" in loaded_report
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_parsing_errors_tracked():
    """Test that parsing errors are properly tracked."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed)
    
    # Total parsing errors should equal sum of all file errors
    total_errors = sum(f["parsing_errors"] for f in report["files"])
    assert report["total_parsing_errors"] == total_errors


def test_function_count_consistency():
    """Test that function counts are consistent across the report."""
    parsed = parse_path("examples")
    report = compute_coverage(parsed)
    
    # Sum of all file function counts should equal total
    file_total = sum(f["total_functions"] for f in report["files"])
    assert report["total_functions"] == file_total
    
    # Sum of all file parsed counts should equal total parsed
    file_parsed = sum(f["parsed_functions"] for f in report["files"])
    assert report["successfully_parsed"] == file_parsed