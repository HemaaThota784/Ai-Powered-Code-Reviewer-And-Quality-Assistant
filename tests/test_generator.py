# tests/test_generator.py
"""Tests for docstring generator."""

import os
import pytest
from core.docstring_engine.generator import (
    generate_google_docstring, 
    generate_all_styles,
    _generate_fallback_docstring
)
from core.parser.python_parser import parse_path


def test_generate_google_docstring_with_groq():
    """Test Google-style docstring generation with Groq."""
    fn = {
        "name": "add",
        "args": [{"name": "a", "annotation": "int"}, {"name": "b", "annotation": "int"}],
        "returns": "int",
        "raises": []
    }
    
    # Test with Groq if API key available, otherwise fallback
    doc = generate_google_docstring(fn, use_groq=True, style="google")
    
    assert '"""' in doc
    assert "add" in doc.lower() or "sum" in doc.lower()
    # Should have proper docstring structure
    assert doc.startswith('"""')
    assert doc.endswith('"""')


def test_generate_google_docstring_fallback():
    """Test Google-style docstring generation with fallback (no Groq)."""
    fn = {
        "name": "multiply",
        "args": [{"name": "x", "annotation": "int"}, {"name": "y", "annotation": "int"}],
        "returns": "int",
        "raises": []
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="google")
    
    assert "Args:" in doc
    assert "Returns:" in doc
    assert "int" in doc
    assert "x" in doc and "y" in doc


def test_generate_numpy_docstring():
    """Test NumPy-style docstring generation."""
    fn = {
        "name": "calculate",
        "args": [{"name": "x", "annotation": "float"}],
        "returns": "float",
        "raises": []
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="numpy")
    
    assert "Parameters" in doc
    assert "----------" in doc or "-------" in doc
    assert "Returns" in doc
    assert "float" in doc


def test_generate_rest_docstring():
    """Test reST-style docstring generation."""
    fn = {
        "name": "process",
        "args": [{"name": "data", "annotation": "str"}],
        "returns": "bool",
        "raises": []
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="rest")
    
    assert ":param" in doc
    assert ":returns:" in doc or ":return:" in doc
    assert "str" in doc
    assert "bool" in doc


def test_generate_all_styles():
    """Test generating docstrings in all styles at once."""
    fn = {
        "name": "test_function",
        "args": [{"name": "param1", "annotation": "int"}],
        "returns": "str",
        "raises": []
    }
    
    all_docs = generate_all_styles(fn, use_groq=False)
    
    assert "google" in all_docs
    assert "numpy" in all_docs
    assert "rest" in all_docs
    
    # Each should be a valid docstring
    assert '"""' in all_docs["google"]
    assert '"""' in all_docs["numpy"]
    assert '"""' in all_docs["rest"]


def test_docstring_excludes_self_parameter():
    """Test that self parameter is excluded from docstrings."""
    fn = {
        "name": "method",
        "args": [
            {"name": "self", "annotation": None},
            {"name": "value", "annotation": "int"}
        ],
        "returns": "None",
        "raises": []
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="google")
    
    # Should not document 'self'
    assert "self" not in doc or "self:" not in doc.lower()
    # Should document 'value'
    assert "value" in doc


def test_docstring_excludes_cls_parameter():
    """Test that cls parameter is excluded from docstrings."""
    fn = {
        "name": "classmethod",
        "args": [
            {"name": "cls", "annotation": None},
            {"name": "param", "annotation": "str"}
        ],
        "returns": "object",
        "raises": []
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="google")
    
    # Should not document 'cls'
    assert "cls" not in doc or "cls:" not in doc.lower()
    # Should document 'param'
    assert "param" in doc


def test_docstring_with_raises_section():
    """Test docstring generation with raises section."""
    fn = {
        "name": "validate",
        "args": [{"name": "data", "annotation": "str"}],
        "returns": "bool",
        "raises": ["ValueError", "TypeError"]
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="google")
    
    assert "Raises:" in doc
    assert "ValueError" in doc
    assert "TypeError" in doc


def test_docstring_without_raises_section():
    """Test that docstring omits Raises section when no exceptions."""
    fn = {
        "name": "simple_func",
        "args": [{"name": "x", "annotation": "int"}],
        "returns": "int",
        "raises": []
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="google")
    
    # Should NOT have Raises section
    assert "Raises:" not in doc


def test_docstring_function_without_args():
    """Test docstring generation for function with no arguments."""
    fn = {
        "name": "get_timestamp",
        "args": [],
        "returns": "str",
        "raises": []
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="google")
    
    assert '"""' in doc
    # Should not have Args section or should have empty Args
    # Returns should still be present
    assert "Returns:" in doc


def test_docstring_function_without_return():
    """Test docstring generation for function with no return value."""
    fn = {
        "name": "print_message",
        "args": [{"name": "message", "annotation": "str"}],
        "returns": None,
        "raises": []
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="google")
    
    assert '"""' in doc
    assert "Args:" in doc
    assert "message" in doc


def test_generate_from_parsed_examples():
    """Test docstring generation using actual parsed functions from examples directory."""
    # Parse examples directory
    parsed_results = parse_path("examples")
    
    # Find at least one function from parsed results
    found_function = False
    for file_result in parsed_results:
        functions = file_result.get("functions", [])
        if functions:
            # Take the first function
            func = functions[0]
            found_function = True
            
            # Generate docstring for it
            doc = generate_google_docstring(func, use_groq=False, style="google")
            
            # Verify it's a valid docstring
            assert '"""' in doc
            assert doc.startswith('"""')
            assert doc.endswith('"""')
            
            # Verify function name or description is in docstring
            assert len(doc) > 20  # Should be more than just empty quotes
            break
    
    assert found_function, "Should find at least one function in examples directory"


def test_generate_all_styles_from_parsed_examples():
    """Test generating all docstring styles for functions from examples directory."""
    # Parse examples directory
    parsed_results = parse_path("examples")
    
    # Find a function with arguments
    found_function = False
    for file_result in parsed_results:
        functions = file_result.get("functions", [])
        for func in functions:
            if func.get("args"):  # Function with arguments
                found_function = True
                
                # Generate all styles
                all_docs = generate_all_styles(func, use_groq=False)
                
                # Verify all three styles are generated
                assert len(all_docs) == 3
                assert "google" in all_docs
                assert "numpy" in all_docs
                assert "rest" in all_docs
                
                # Verify each is different and valid
                assert all_docs["google"] != all_docs["numpy"]
                assert all_docs["numpy"] != all_docs["rest"]
                
                # Google should have "Args:"
                assert "Args:" in all_docs["google"]
                
                # NumPy should have "Parameters"
                assert "Parameters" in all_docs["numpy"]
                
                # reST should have ":param"
                assert ":param" in all_docs["rest"]
                
                break
        
        if found_function:
            break
    
    assert found_function, "Should find at least one function with arguments in examples"


def test_fallback_docstring_google_style():
    """Test fallback docstring generation in Google style."""
    fn = {
        "name": "test_func",
        "args": [{"name": "x", "annotation": "int"}],
        "returns": "str",
        "raises": []
    }
    
    doc = _generate_fallback_docstring(fn, style="google")
    
    assert "Args:" in doc
    assert "Returns:" in doc
    assert "x" in doc
    assert "int" in doc
    assert "str" in doc


def test_fallback_docstring_numpy_style():
    """Test fallback docstring generation in NumPy style."""
    fn = {
        "name": "test_func",
        "args": [{"name": "x", "annotation": "float"}],
        "returns": "float",
        "raises": []
    }
    
    doc = _generate_fallback_docstring(fn, style="numpy")
    
    assert "Parameters" in doc
    assert "----------" in doc
    assert "Returns" in doc
    assert "-------" in doc
    assert "float" in doc


def test_fallback_docstring_rest_style():
    """Test fallback docstring generation in reST style."""
    fn = {
        "name": "test_func",
        "args": [{"name": "data", "annotation": "dict"}],
        "returns": "list",
        "raises": []
    }
    
    doc = _generate_fallback_docstring(fn, style="rest")
    
    assert ":param" in doc
    assert ":returns:" in doc
    assert ":rtype:" in doc
    assert "dict" in doc
    assert "list" in doc


def test_groq_api_key_detection():
    """Test that function detects GROQ_API_KEY presence."""
    fn = {
        "name": "test",
        "args": [],
        "returns": None,
        "raises": []
    }
    
    # This test just verifies the function runs without crashing
    # Whether it uses Groq or fallback depends on environment
    doc = generate_google_docstring(fn, use_groq=True, style="google")
    
    assert '"""' in doc
    assert len(doc) > 10


def test_multiple_arguments_formatting():
    """Test proper formatting of multiple arguments."""
    fn = {
        "name": "complex_func",
        "args": [
            {"name": "arg1", "annotation": "int"},
            {"name": "arg2", "annotation": "str"},
            {"name": "arg3", "annotation": "list"}
        ],
        "returns": "dict",
        "raises": []
    }
    
    doc = generate_google_docstring(fn, use_groq=False, style="google")
    
    assert "arg1" in doc
    assert "arg2" in doc
    assert "arg3" in doc
    assert "int" in doc
    assert "str" in doc
    assert "list" in doc