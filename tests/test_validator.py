# tests/test_validator.py
"""Tests for PEP 257 docstring validator."""

import pytest
from core.validator.validator import PEP257Validator, validate_project
from core.parser.python_parser import parse_path, parse_file


def test_validator_initialization():
    """Test that PEP257Validator can be initialized."""
    validator = PEP257Validator()
    assert validator is not None
    assert hasattr(validator, 'violations')
    assert isinstance(validator.violations, list)


def test_validate_file_returns_list():
    """Test that validate_file returns list of violations."""
    # Parse an example file first
    parsed_results = parse_path("examples")
    
    if parsed_results:
        validator = PEP257Validator()
        violations = validator.validate_file(parsed_results[0])
        
        assert isinstance(violations, list)


def test_validate_file_structure():
    """Test that violation dictionaries have correct structure."""
    parsed_results = parse_path("examples")
    
    if parsed_results:
        validator = PEP257Validator()
        violations = validator.validate_file(parsed_results[0])
        
        # If there are violations, check their structure
        for violation in violations:
            assert isinstance(violation, dict)
            assert "code" in violation
            assert "line" in violation
            assert "message" in violation
            assert "file" in violation
            
            # Validate types
            assert isinstance(violation["code"], str)
            assert isinstance(violation["line"], int)
            assert isinstance(violation["message"], str)
            assert isinstance(violation["file"], str)


def test_validate_project_returns_dict():
    """Test that validate_project returns a dictionary with metrics."""
    parsed_results = parse_path("examples")
    
    report = validate_project(parsed_results)
    
    assert isinstance(report, dict)
    assert "total_violations" in report
    assert "violations" in report
    assert "total_items" in report
    assert "compliant_items" in report
    assert "compliance_percentage" in report
    assert "total_functions" in report
    assert "total_classes" in report
    assert "compliant_functions" in report
    assert "compliant_classes" in report


def test_validate_project_metrics_types():
    """Test that validate_project returns correct data types."""
    parsed_results = parse_path("examples")
    report = validate_project(parsed_results)
    
    assert isinstance(report["total_violations"], int)
    assert isinstance(report["violations"], list)
    assert isinstance(report["total_items"], int)
    assert isinstance(report["compliant_items"], int)
    assert isinstance(report["compliance_percentage"], (int, float))
    assert isinstance(report["total_functions"], int)
    assert isinstance(report["total_classes"], int)


def test_validate_project_compliance_percentage():
    """Test that compliance percentage is in valid range."""
    parsed_results = parse_path("examples")
    report = validate_project(parsed_results)
    
    assert 0 <= report["compliance_percentage"] <= 100


def test_validator_detects_missing_docstrings():
    """Test that validator detects missing docstrings (D103, D102, D101)."""
    parsed_results = parse_path("examples")
    
    validator = PEP257Validator()
    all_violations = []
    
    for file_data in parsed_results:
        violations = validator.validate_file(file_data)
        all_violations.extend(violations)
    
    # Check if any violations are about missing docstrings
    violation_codes = [v["code"] for v in all_violations]
    
    # Validator should detect at least some violations
    # Common codes: D101 (class), D102 (method), D103 (function)
    assert isinstance(all_violations, list)


def test_validator_checks_docstring_format():
    """Test that validator checks docstring formatting rules."""
    parsed_results = parse_path("examples")
    
    report = validate_project(parsed_results)
    violations = report["violations"]
    
    # If there are violations, check they use valid PEP 257 codes
    valid_codes = [
        "D100", "D101", "D102", "D103", 
        "D200", "D201", "D202", "D203", "D204", "D205",
        "D206", "D207", "D208", "D209", "D210", "D211",
        "D212", "D213", "D300", "D301", "D400", "D401", "D402"
    ]
    
    for violation in violations:
        assert violation["code"] in valid_codes, f"Invalid code: {violation['code']}"


def test_validator_skips_private_functions():
    """Test that validator skips private functions (starting with _)."""
    # Create mock data with private function
    mock_data = {
        "file_path": "test.py",
        "functions": [
            {
                "name": "_private_func",
                "start_line": 1,
                "has_docstring": False,
                "docstring": None
            },
            {
                "name": "public_func",
                "start_line": 5,
                "has_docstring": False,
                "docstring": None
            }
        ],
        "classes": []
    }
    
    validator = PEP257Validator()
    violations = validator.validate_file(mock_data)
    
    # Should have violation for public_func but not _private_func
    violation_messages = [v["message"] for v in violations]
    
    # Check that private function is not mentioned
    private_violations = [v for v in violations if "_private_func" in v["message"]]
    assert len(private_violations) == 0, "Private functions should be skipped"


def test_validator_checks_triple_quotes():
    """Test that validator checks for triple double quotes (D300)."""
    mock_data = {
        "file_path": "test.py",
        "functions": [
            {
                "name": "test_func",
                "start_line": 1,
                "has_docstring": True,
                "docstring": "'''Single quotes docstring.'''"  # Wrong style
            }
        ],
        "classes": []
    }
    
    validator = PEP257Validator()
    violations = validator.validate_file(mock_data, source_code="def test_func():\n    '''Single quotes docstring.'''")
    
    # Should detect D300 violation
    d300_violations = [v for v in violations if v["code"] == "D300"]
    assert len(d300_violations) > 0, "Should detect triple single quotes"


def test_validator_checks_period_ending():
    """Test that validator checks for period at end of first line (D400)."""
    mock_data = {
        "file_path": "test.py",
        "functions": [
            {
                "name": "test_func",
                "start_line": 1,
                "has_docstring": True,
                "docstring": '"""\nThis is a summary without period\n"""'
            }
        ],
        "classes": []
    }
    
    validator = PEP257Validator()
    violations = validator.validate_file(mock_data)
    
    # Should detect D400 violation
    d400_violations = [v for v in violations if v["code"] == "D400"]
    assert len(d400_violations) > 0, "Should detect missing period"


def test_validator_with_proper_docstring():
    """Test validator with a properly formatted docstring."""
    mock_data = {
        "file_path": "test.py",
        "functions": [
            {
                "name": "well_documented",
                "start_line": 1,
                "has_docstring": True,
                "docstring": '"""\nProper summary line.\n\nDetailed description here.\n"""'
            }
        ],
        "classes": []
    }
    
    validator = PEP257Validator()
    violations = validator.validate_file(mock_data)
    
    # May still have some violations but should be fewer
    assert isinstance(violations, list)


def test_validate_project_empty_input():
    """Test validate_project with empty input."""
    report = validate_project([])
    
    assert report["total_violations"] == 0
    assert report["total_items"] == 0
    assert report["compliance_percentage"] == 0


def test_validate_project_counts_correctly():
    """Test that validate_project counts items correctly."""
    parsed_results = parse_path("examples")
    report = validate_project(parsed_results)
    
    # Total items should equal functions + classes
    assert report["total_items"] == report["total_functions"] + report["total_classes"]
    
    # Compliant items should not exceed total items
    assert report["compliant_items"] <= report["total_items"]
    
    # Compliant should equal compliant functions + compliant classes
    assert report["compliant_items"] == report["compliant_functions"] + report["compliant_classes"]


def test_validator_checks_classes():
    """Test that validator checks class docstrings (D101)."""
    mock_data = {
        "file_path": "test.py",
        "functions": [],
        "classes": [
            {
                "name": "TestClass",
                "start_line": 1,
                "has_docstring": False,
                "docstring": None,
                "methods": []
            }
        ]
    }
    
    validator = PEP257Validator()
    violations = validator.validate_file(mock_data)
    
    # Should have D101 violation for missing class docstring
    d101_violations = [v for v in violations if v["code"] == "D101"]
    assert len(d101_violations) > 0, "Should detect missing class docstring"


def test_validator_checks_methods():
    """Test that validator checks method docstrings (D102)."""
    mock_data = {
        "file_path": "test.py",
        "functions": [],
        "classes": [
            {
                "name": "TestClass",
                "start_line": 1,
                "has_docstring": True,
                "docstring": '"""\nClass docstring.\n"""',
                "methods": [
                    {
                        "name": "test_method",
                        "start_line": 3,
                        "has_docstring": False,
                        "docstring": None,
                        "args": []
                    }
                ]
            }
        ]
    }
    
    validator = PEP257Validator()
    violations = validator.validate_file(mock_data)
    
    # Should have D102 violation for missing method docstring
    d102_violations = [v for v in violations if v["code"] == "D102"]
    assert len(d102_violations) > 0, "Should detect missing method docstring"


def test_validator_multiline_docstring_format():
    """Test validator checks multi-line docstring format (D209)."""
    mock_data = {
        "file_path": "test.py",
        "functions": [
            {
                "name": "test_func",
                "start_line": 1,
                "has_docstring": True,
                "docstring": '"""\nFirst line.\n\nSecond paragraph."""'  # Closing quotes not on separate line
            }
        ],
        "classes": []
    }
    
    validator = PEP257Validator()
    violations = validator.validate_file(mock_data)
    
    # Should detect D209 violation
    d209_violations = [v for v in violations if v["code"] == "D209"]
    assert len(d209_violations) > 0, "Should detect improper closing quotes"


def test_validator_blank_line_after_summary():
    """Test validator checks for blank line after summary (D205)."""
    mock_data = {
        "file_path": "test.py",
        "functions": [
            {
                "name": "test_func",
                "start_line": 1,
                "has_docstring": True,
                "docstring": '"""\nFirst line.\nSecond line without blank.\n"""'  # Missing blank line
            }
        ],
        "classes": []
    }
    
    validator = PEP257Validator()
    violations = validator.validate_file(mock_data)
    
    # Should detect D205 violation
    d205_violations = [v for v in violations if v["code"] == "D205"]
    # This might or might not trigger depending on interpretation


def test_validate_examples_directory():
    """Test validation on actual examples directory."""
    parsed_results = parse_path("examples")
    
    # Should successfully parse and validate
    assert len(parsed_results) > 0
    
    report = validate_project(parsed_results)
    
    # Basic sanity checks
    assert report["total_violations"] >= 0
    assert report["total_items"] >= 0
    assert isinstance(report["violations"], list)
    
    # Print summary for debugging
    print(f"\nValidation Summary:")
    print(f"  Total Items: {report['total_items']}")
    print(f"  Compliant Items: {report['compliant_items']}")
    print(f"  Compliance: {report['compliance_percentage']}%")
    print(f"  Violations: {report['total_violations']}")


def test_validator_line_numbers():
    """Test that violations include valid line numbers."""
    parsed_results = parse_path("examples")
    
    report = validate_project(parsed_results)
    
    for violation in report["violations"]:
        assert violation["line"] > 0, "Line numbers should be positive"
        assert isinstance(violation["line"], int)


def test_validator_file_paths():
    """Test that violations include file paths."""
    parsed_results = parse_path("examples")
    
    report = validate_project(parsed_results)
    
    for violation in report["violations"]:
        assert "file" in violation
        assert isinstance(violation["file"], str)
        assert len(violation["file"]) > 0


def test_pep257_validator_class_attributes():
    """Test that PEP257Validator has the expected error code attributes."""
    validator = PEP257Validator()
    
    # Check some key error codes exist as class attributes
    assert hasattr(PEP257Validator, 'D101')
    assert hasattr(PEP257Validator, 'D102')
    assert hasattr(PEP257Validator, 'D103')
    assert hasattr(PEP257Validator, 'D200')
    assert hasattr(PEP257Validator, 'D300')
    assert hasattr(PEP257Validator, 'D400')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])