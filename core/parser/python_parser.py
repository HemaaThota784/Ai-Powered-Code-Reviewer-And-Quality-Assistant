"""
AST-based per-file Python parser for Milestone 1.

Extracts:
- functions (name, args, annotations, defaults, returns, start/end lines)
- classes (and their methods)
- imports
- simple complexity estimate (heuristic)
- nesting depth
- presence of docstring
- **ACTUAL DOCSTRING TEXT** (fixed!)
- parsing errors
"""

import ast
import os
import inspect
from typing import Any, Dict, List, Optional


def get_annotation_str(node: Optional[ast.AST]) -> Optional[str]:
    """Convert annotation AST node to string representation."""
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return str(node)


def _get_default_str(node: Optional[ast.AST]) -> Optional[str]:
    """Convert default value AST node to string representation."""
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return str(node)


def _simple_complexity(node: ast.FunctionDef) -> int:
    """
    Calculate simple complexity estimate (heuristic).
    Counts control flow statements: if, for, while, except, with, and, or.
    """
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
            complexity += 1
        elif isinstance(child, (ast.BoolOp,)):
            if isinstance(child.op, (ast.And, ast.Or)):
                complexity += len(child.values) - 1
    return complexity


def _max_nesting_depth(node: ast.FunctionDef) -> int:
    """
    Calculate maximum nesting depth of control structures.
    """
    def depth(n, current=0):
        if isinstance(n, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            max_child = current
            for child in ast.iter_child_nodes(n):
                max_child = max(max_child, depth(child, current + 1))
            return max_child
        else:
            max_child = current
            for child in ast.iter_child_nodes(n):
                max_child = max(max_child, depth(child, current))
            return max_child
    
    return depth(node, 0)


def _has_docstring(node: ast.FunctionDef) -> bool:
    """Check if a function/method has a docstring."""
    return (
        len(node.body) > 0 and
        isinstance(node.body[0], ast.Expr) and
        isinstance(node.body[0].value, ast.Constant) and
        isinstance(node.body[0].value.value, str)
    )


def _get_docstring(node: ast.FunctionDef) -> Optional[str]:
    """
    Extract the actual docstring text from a function/method/class.
    Returns the docstring with triple quotes, or None if no docstring exists.
    Removes indentation from the extracted docstring.
    """
    if (len(node.body) > 0 and
        isinstance(node.body[0], ast.Expr) and
        isinstance(node.body[0].value, ast.Constant) and
        isinstance(node.body[0].value.value, str)):
        
        docstring_text = node.body[0].value.value
        
        # Use inspect.cleandoc to remove indentation and clean up the docstring
        import inspect
        cleaned_docstring = inspect.cleandoc(docstring_text)
        
        # Return with triple quotes
        return f'"""\n{cleaned_docstring}\n"""'
    return None

def parse_functions(node: ast.AST) -> List[Dict[str, Any]]:
    """
    Parse all top-level functions from AST node (not methods inside classes).
    Returns list of dictionaries with function metadata.
    """
    functions = []
    
    # Only get top-level functions, not methods inside classes
    if hasattr(node, 'body'):
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Extract arguments with types
                args = []
                for arg in item.args.args:
                    arg_info = {
                        "name": arg.arg,
                        "annotation": get_annotation_str(arg.annotation)
                    }
                    args.append(arg_info)
                
                # Extract defaults
                defaults = []
                num_defaults = len(item.args.defaults)
                num_args = len(item.args.args)
                
                # Map defaults to their corresponding arguments
                for i, default in enumerate(item.args.defaults):
                    defaults.append({
                        "arg_index": num_args - num_defaults + i,
                        "value": _get_default_str(default)
                    })
                
                func_info = {
                    "name": item.name,
                    "args": args,
                    "defaults": defaults,
                    "returns": get_annotation_str(item.returns),
                    "start_line": item.lineno,
                    "end_line": item.end_lineno,
                    "complexity": _simple_complexity(item),
                    "nesting_depth": _max_nesting_depth(item),
                    "has_docstring": _has_docstring(item),
                    "docstring": _get_docstring(item),
                    "raises": _extract_raises(item)  # NEW: Extract actual docstring
                }
                functions.append(func_info)
    
    return functions


def parse_classes(node: ast.AST) -> List[Dict[str, Any]]:
    """
    Parse all classes and their methods from AST node.
    Returns list of dictionaries with class metadata.
    """
    classes = []

    if hasattr(node, 'body'):
        for item in node.body:
            if isinstance(item, ast.ClassDef):
                methods = []

                for method in item.body:
                    if isinstance(method, ast.FunctionDef):
                        args = []
                        for arg in method.args.args:
                            args.append({
                                "name": arg.arg,
                                "annotation": get_annotation_str(arg.annotation)
                            })

                        method_info = {
                            "name": method.name,
                            "args": args,
                            "returns": get_annotation_str(method.returns),
                            "start_line": method.lineno,
                            "end_line": method.end_lineno,
                            "complexity": _simple_complexity(method),
                            "has_docstring": _has_docstring(method),
                            "docstring": _get_docstring(method),
                            # ✅ FIX: pass method, not class
                            "raises": _extract_raises(method)
                        }
                        methods.append(method_info)

                class_info = {
                    "name": item.name,
                    "methods": methods,
                    "start_line": item.lineno,
                    "end_line": item.end_lineno or item.lineno,
                    "has_docstring": _has_docstring(item),
                    "docstring": _get_docstring(item)
                }

                classes.append(class_info)

    return classes



def parse_imports(node: ast.AST) -> List[str]:
    """
    Parse all import statements from AST node.
    Returns list of import strings.
    """
    imports = []
    for item in ast.walk(node):
        if isinstance(item, ast.Import):
            for name in item.names:
                if name.asname:
                    imports.append(f"import {name.name} as {name.asname}")
                else:
                    imports.append(f"import {name.name}")
        elif isinstance(item, ast.ImportFrom):
            module = item.module or ""
            for name in item.names:
                if name.asname:
                    imports.append(f"from {module} import {name.name} as {name.asname}")
                else:
                    imports.append(f"from {module} import {name.name}")
    
    return imports


def parse_file(path: str) -> Dict[str, Any]:
    """
    Parse a Python file and extract metadata.
    
    Args:
        path: Path to Python file
        
    Returns:
        Dictionary containing file metadata including functions, classes, imports, and errors
    """
    parsing_errors = []
    functions = []
    classes = []
    imports = []
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=path)
        functions = parse_functions(tree)
        classes = parse_classes(tree)
        imports = parse_imports(tree)
        
    except SyntaxError as e:
        parsing_errors.append(f"SyntaxError at line {e.lineno}: {e.msg}")
    except Exception as e:
        parsing_errors.append(f"Error: {str(e)}")
    
    return {
        "file_path": path,
        "imports": imports,
        "parsing_errors": parsing_errors,
        "functions": functions,
        "classes": classes
    }


def parse_path(path: str, recursive: bool = True, skip_dirs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Parse Python files in a directory path.
    
    Args:
        path: Directory path to scan
        recursive: Whether to scan recursively
        skip_dirs: List of directory names to skip
        
    Returns:
        List of dictionaries containing metadata for each Python file
    """
    if skip_dirs is None:
        skip_dirs = []
    
    results = []
    
    if os.path.isfile(path):
        if path.endswith('.py'):
            results.append(parse_file(path))
    else:
        for root, dirs, files in os.walk(path):
            # Skip specified directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    results.append(parse_file(file_path))
            
            if not recursive:
                break
    
    return results

def _extract_raises(node: ast.FunctionDef) -> List[str]:
    """
    Extract exception types that are explicitly raised in a function.
    
    Returns:
        List of exception class names that are raised
    """
    raises = set()
    
    for child in ast.walk(node):
        if isinstance(child, ast.Raise):
            if child.exc:
                # Handle different raise patterns
                if isinstance(child.exc, ast.Call):
                    # raise ValueError("message")
                    if isinstance(child.exc.func, ast.Name):
                        raises.add(child.exc.func.id)
                    elif isinstance(child.exc.func, ast.Attribute):
                        raises.add(child.exc.func.attr)
                elif isinstance(child.exc, ast.Name):
                    # raise exc (where exc is a variable)
                    raises.add(child.exc.id)
    
    return sorted(list(raises))