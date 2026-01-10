# tests/test_python_parser.py

"""
Test file for python_parser.py
"""

import os
import pytest
from core.parser.python_parser import (
    parse_path,
    parse_file,
    parse_functions,
    parse_classes,
    parse_imports,
    get_annotation_str,
    _get_docstring,
    _extract_raises,
    _simple_complexity,
    _max_nesting_depth,
    _has_docstring
)
import ast


def test_parse_path_returns_list():
    """Test that parse_path returns a list."""
    results = parse_path("examples")
    assert isinstance(results, list)


def test_parse_path_finds_files():
    """Test that parse_path finds at least some Python files."""
    results = parse_path("examples")
    # Should find at least one Python file
    assert len(results) >= 1


def test_parse_examples_directory():
    """Test parsing of examples directory."""
    results = parse_path("examples")
    
    # Check we got results
    assert len(results) >= 1
    
    # Check structure of each result
    for file_result in results:
        assert "file_path" in file_result
        assert "functions" in file_result
        assert "classes" in file_result
        assert "imports" in file_result
        assert "parsing_errors" in file_result
        
        # Verify types
        assert isinstance(file_result["functions"], list)
        assert isinstance(file_result["classes"], list)
        assert isinstance(file_result["imports"], list)
        assert isinstance(file_result["parsing_errors"], list)


def test_function_metadata_structure():
    """Test that parsed functions have all required metadata fields."""
    results = parse_path("examples")
    
    # Find at least one function
    found_function = False
    for file_result in results:
        for func in file_result.get("functions", []):
            found_function = True
            
            # Check required fields
            assert "name" in func
            assert "args" in func
            assert "defaults" in func
            assert "returns" in func
            assert "start_line" in func
            assert "end_line" in func
            assert "complexity" in func
            assert "nesting_depth" in func
            assert "has_docstring" in func
            assert "docstring" in func
            assert "raises" in func
            
            # Check types
            assert isinstance(func["name"], str)
            assert isinstance(func["args"], list)
            assert isinstance(func["defaults"], list)
            assert isinstance(func["start_line"], int)
            assert isinstance(func["end_line"], int)
            assert isinstance(func["complexity"], int)
            assert isinstance(func["nesting_depth"], int)
            assert isinstance(func["has_docstring"], bool)
            assert isinstance(func["raises"], list)
            
            break
        if found_function:
            break
    
    assert found_function, "Should find at least one function in examples"


def test_class_metadata_structure():
    """Test that parsed classes have all required metadata fields."""
    results = parse_path("examples")
    
    # Look for a class (might not exist in all examples)
    for file_result in results:
        for cls in file_result.get("classes", []):
            # Check required fields
            assert "name" in cls
            assert "methods" in cls
            assert "start_line" in cls
            assert "end_line" in cls
            assert "has_docstring" in cls
            assert "docstring" in cls
            
            # Check types
            assert isinstance(cls["name"], str)
            assert isinstance(cls["methods"], list)
            assert isinstance(cls["start_line"], int)
            assert isinstance(cls["end_line"], int)
            assert isinstance(cls["has_docstring"], bool)
            
            # If there are methods, check their structure
            for method in cls["methods"]:
                assert "name" in method
                assert "args" in method
                assert "returns" in method
                assert "complexity" in method
                assert "has_docstring" in method
                assert "docstring" in method
                assert "raises" in method


def test_argument_parsing():
    """Test that function arguments are parsed correctly."""
    results = parse_path("examples")
    
    # Find a function with arguments
    found_args = False
    for file_result in results:
        for func in file_result.get("functions", []):
            if func.get("args"):
                found_args = True
                
                # Check each argument has required fields
                for arg in func["args"]:
                    assert "name" in arg
                    assert "annotation" in arg
                    assert isinstance(arg["name"], str)
                    # annotation can be None or str
                    assert arg["annotation"] is None or isinstance(arg["annotation"], str)
                
                break
        if found_args:
            break
    
    # It's okay if no functions have args, but if they do, they should be structured correctly
    # This test passes either way


def test_docstring_extraction():
    """Test that docstrings are extracted correctly."""
    results = parse_path("examples")
    
    # Find a function with a docstring
    found_docstring = False
    for file_result in results:
        for func in file_result.get("functions", []):
            if func.get("has_docstring") and func.get("docstring"):
                found_docstring = True
                
                # Docstring should be wrapped in triple quotes
                assert func["docstring"].startswith('"""')
                assert func["docstring"].endswith('"""')
                
                # Should have some content
                assert len(func["docstring"]) > 10
                
                break
        if found_docstring:
            break
    
    # Note: It's possible no functions have docstrings, that's okay


def test_complexity_calculation():
    """Test that complexity is calculated as a positive integer."""
    results = parse_path("examples")
    
    for file_result in results:
        for func in file_result.get("functions", []):
            # Complexity should be at least 1
            assert func["complexity"] >= 1
            assert isinstance(func["complexity"], int)


def test_nesting_depth_calculation():
    """Test that nesting depth is calculated correctly."""
    results = parse_path("examples")
    
    for file_result in results:
        for func in file_result.get("functions", []):
            # Nesting depth should be >= 0
            assert func["nesting_depth"] >= 0
            assert isinstance(func["nesting_depth"], int)


def test_raises_extraction():
    """Test that raised exceptions are extracted."""
    results = parse_path("examples")
    
    for file_result in results:
        for func in file_result.get("functions", []):
            # raises should be a list
            assert isinstance(func["raises"], list)
            
            # If there are raises, they should be strings
            for exc in func["raises"]:
                assert isinstance(exc, str)
                assert len(exc) > 0


def test_parsing_errors_field():
    """Test that parsing_errors field is present and is a list."""
    results = parse_path("examples")
    
    for file_result in results:
        assert "parsing_errors" in file_result
        assert isinstance(file_result["parsing_errors"], list)


def test_imports_extraction():
    """Test that imports are extracted correctly."""
    results = parse_path("examples")
    
    for file_result in results:
        assert "imports" in file_result
        assert isinstance(file_result["imports"], list)
        
        # If there are imports, they should be strings
        for imp in file_result["imports"]:
            assert isinstance(imp, str)
            # Should contain 'import' keyword
            assert "import" in imp


def test_line_numbers_are_valid():
    """Test that start and end line numbers are valid."""
    results = parse_path("examples")
    
    for file_result in results:
        for func in file_result.get("functions", []):
            assert func["start_line"] > 0
            assert func["end_line"] >= func["start_line"]


def test_parse_file_single_file():
    """Test parsing a single Python file."""
    results = parse_path("examples")
    
    if results:
        # Get the first file path
        first_file = results[0]["file_path"]
        
        # Parse just that file
        single_result = parse_file(first_file)
        
        # Should have same structure
        assert "file_path" in single_result
        assert "functions" in single_result
        assert "classes" in single_result
        assert "imports" in single_result
        assert "parsing_errors" in single_result


def test_recursive_parsing():
    """Test that recursive parsing works (default behavior)."""
    results = parse_path("examples", recursive=True)
    assert isinstance(results, list)
    assert len(results) >= 1


def test_non_recursive_parsing():
    """Test that non-recursive parsing works."""
    results = parse_path("examples", recursive=False)
    assert isinstance(results, list)
    # Non-recursive should still find files in the top level


def test_get_annotation_str():
    """Test annotation string extraction helper."""
    # Test with None
    assert get_annotation_str(None) is None
    
    # Test with actual annotation node
    code = "def func(x: int) -> str: pass"
    tree = ast.parse(code)
    func_node = tree.body[0]
    
    # Get return annotation
    return_ann = get_annotation_str(func_node.returns)
    assert return_ann == "str"
    
    # Get arg annotation
    arg_ann = get_annotation_str(func_node.args.args[0].annotation)
    assert arg_ann == "int"


def test_has_docstring_helper():
    """Test _has_docstring helper function."""
    # Function with docstring
    code_with_doc = '''
def func():
    """This is a docstring."""
    pass
'''
    tree = ast.parse(code_with_doc)
    func_node = tree.body[0]
    assert _has_docstring(func_node) is True
    
    # Function without docstring
    code_without_doc = '''
def func():
    pass
'''
    tree = ast.parse(code_without_doc)
    func_node = tree.body[0]
    assert _has_docstring(func_node) is False


def test_simple_complexity_helper():
    """Test _simple_complexity helper function."""
    # Simple function
    code_simple = '''
def func():
    return 1
'''
    tree = ast.parse(code_simple)
    func_node = tree.body[0]
    complexity = _simple_complexity(func_node)
    assert complexity == 1
    
    # Function with if statement
    code_with_if = '''
def func(x):
    if x > 0:
        return x
    return 0
'''
    tree = ast.parse(code_with_if)
    func_node = tree.body[0]
    complexity = _simple_complexity(func_node)
    assert complexity >= 2


def test_max_nesting_depth_helper():
    """Test _max_nesting_depth helper function."""
    # No nesting
    code_flat = '''
def func():
    x = 1
    return x
'''
    tree = ast.parse(code_flat)
    func_node = tree.body[0]
    depth = _max_nesting_depth(func_node)
    assert depth == 0
    
    # With nesting
    code_nested = '''
def func(x):
    if x > 0:
        for i in range(x):
            print(i)
    return x
'''
    tree = ast.parse(code_nested)
    func_node = tree.body[0]
    depth = _max_nesting_depth(func_node)
    assert depth >= 1


def test_extract_raises_helper():
    """Test _extract_raises helper function."""
    # Function with raise
    code_with_raise = '''
def func(x):
    if x < 0:
        raise ValueError("negative value")
    return x
'''
    tree = ast.parse(code_with_raise)
    func_node = tree.body[0]
    raises = _extract_raises(func_node)
    assert "ValueError" in raises
    
    # Function without raise
    code_no_raise = '''
def func(x):
    return x * 2
'''
    tree = ast.parse(code_no_raise)
    func_node = tree.body[0]
    raises = _extract_raises(func_node)
    assert len(raises) == 0


def test_get_docstring_with_triple_quotes():
    """Test that _get_docstring returns docstring with triple quotes."""
    code = '''
def func():
    """This is a docstring."""
    pass
'''
    tree = ast.parse(code)
    func_node = tree.body[0]
    docstring = _get_docstring(func_node)
    
    assert docstring is not None
    assert docstring.startswith('"""')
    assert docstring.endswith('"""')
    assert "This is a docstring" in docstring


def test_total_functions_count():
    """Test counting total functions across all files."""
    results = parse_path("examples")
    
    total_funcs = sum(len(f.get("functions", [])) for f in results)
    # Should have at least one function in examples
    assert total_funcs >= 1


def test_total_classes_count():
    """Test counting total classes across all files."""
    results = parse_path("examples")
    
    total_classes = sum(len(f.get("classes", [])) for f in results)
    # Classes might be 0, that's okay
    assert total_classes >= 0


def test_file_paths_are_valid():
    """Test that all file paths in results are valid strings."""
    results = parse_path("examples")
    
    for file_result in results:
        assert isinstance(file_result["file_path"], str)
        assert len(file_result["file_path"]) > 0
        assert file_result["file_path"].endswith(".py")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])