"""
core.validator.validator

Enhanced PEP 257 docstring convention validator.
Checks Python code for docstring compliance and style violations.
"""

import re
from typing import Dict, List, Tuple, Any


class PEP257Validator:
    """Validator for PEP 257 docstring conventions."""
    
    # PEP 257 error codes
    #D100 = "Missing docstring in public module"
    D101 = "Missing docstring in public class"
    D102 = "Missing docstring in public method"
    D103 = "Missing docstring in public function"
    D200 = "One-line docstring should fit on one line with quotes"
    D201 = "No blank lines allowed before function docstring"
    D202 = "No blank lines allowed after function docstring"
    D203 = "1 blank line required before class docstring"
    D204 = "1 blank line required after class docstring"
    D205 = "1 blank line required between summary line and description"
    D206 = "Docstring should be indented with spaces, not tabs"
    D207 = "Docstring is under-indented"
    D208 = "Docstring is over-indented"
    D209 = "Multi-line docstring closing quotes should be on a separate line"
    D210 = "No whitespaces allowed surrounding docstring text"
    D211 = "No blank lines allowed before class docstring"
    D212 = "Multi-line docstring summary should start at the first line"
    D213 = "Multi-line docstring summary should start at the second line"
    D300 = "Use triple double quotes for docstrings"
    D301 = "Use r\"\"\" if any backslashes in a docstring"
    D400 = "First line should end with a period"
    D401 = "First line should be in imperative mood"
    D402 = "First line should not be the function's signature"
    
    def __init__(self):
        """Initialize the PEP 257 validator."""
        self.violations = []
    
    def validate_file(self, file_data: Dict[str, Any], source_code: str = None) -> List[Dict[str, Any]]:
        """
        Validate a parsed file for PEP 257 compliance.
        
        Args:
            file_data: Parsed file data from python_parser
            source_code: Optional source code string for line-by-line checks
            
        Returns:
            List of violation dictionaries with code, line, message
        """
        self.violations = []
        file_path = file_data.get("file_path", "")
        
        # Load source code if available
        if source_code is None and file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
            except Exception:
                source_code = None
        
        source_lines = source_code.split('\n') if source_code else []
        
        # Check module-level docstring (D100)
        #module_has_docstring = self._check_module_docstring(file_data, source_lines)
        
        # Check functions (D103, D2xx, D3xx, D4xx)
        for func in file_data.get("functions", []):
            self._validate_function(func, file_path, source_lines, is_method=False)
        
        # Check classes and methods (D101, D102, D2xx, D3xx, D4xx)
        for cls in file_data.get("classes", []):
            self._validate_class(cls, file_path, source_lines)
        
        return self.violations
    
    def _check_module_docstring(self, file_data: Dict, source_lines: List[str]) -> bool:
        """Check if module has a docstring at the top."""
        if not source_lines:
            return False
        
        # Skip shebang and encoding declarations
        start_line = 0
        for i, line in enumerate(source_lines[:10]):
            stripped = line.strip()
            if stripped.startswith('#') or stripped == '':
                start_line = i + 1
            else:
                break
        
        # Check if first non-comment line is a docstring
        if start_line < len(source_lines):
            line = source_lines[start_line].strip()
            if not (line.startswith('"""') or line.startswith("'''")):
                self.violations.append({
                    "code": "D100",
                    "line": 1,
                    "message": self.D100,
                    "file": file_data.get("file_path", "")
                })
                return False
        
        return True
    
    def _validate_function(self, func: Dict, file_path: str, source_lines: List[str], 
                          is_method: bool = False, class_name: str = None):
        """Validate a function or method for PEP 257 compliance."""
        func_name = func.get("name", "")
        start_line = func.get("start_line", 0)
        has_docstring = func.get("has_docstring", False)
        docstring = func.get("docstring", "")
        
        # Skip private functions/methods (starting with _)
        if func_name.startswith("_") and not func_name.startswith("__"):
            return
        
        # D102 or D103: Missing docstring
        if not has_docstring:
            code = "D102" if is_method else "D103"
            location = f"{class_name}.{func_name}" if class_name else func_name
            message = f"{code}: Missing docstring in public {'method' if is_method else 'function'} {location}"
            self.violations.append({
                "code": code,
                "line": start_line,
                "message": message,
                "file": file_path
            })
            return
        
        # Check blank lines before docstring (D201)
        if source_lines and start_line > 0 and start_line < len(source_lines):
            # Find the line with the function definition
            func_def_line = start_line - 1  # 0-indexed
            
            # Check if there's a blank line between function def and docstring
            if func_def_line + 1 < len(source_lines):
                next_line = source_lines[func_def_line + 1].strip()
                # If next line after def is blank (not the docstring start)
                if next_line == '' and func_def_line + 2 < len(source_lines):
                    following_line = source_lines[func_def_line + 2].strip()
                    if following_line.startswith('"""') or following_line.startswith("'''"):
                        location = f"{class_name}.{func_name}" if class_name else func_name
                        self.violations.append({
                            "code": "D201",
                            "line": func_def_line + 2,
                            "message": f"D201: No blank lines allowed before function docstring in {location}",
                            "file": file_path
                        })
        
        # Validate docstring content and check for blank lines after (D202)
        if docstring:
            self._validate_docstring_format(docstring, start_line, file_path, source_lines, 
                                           func_name, is_function=True, class_name=class_name,
                                           func_obj=func)
    
    def _validate_class(self, cls: Dict, file_path: str, source_lines: List[str]):
        """Validate a class for PEP 257 compliance."""
        class_name = cls.get("name", "")
        start_line = cls.get("start_line", 0)
        has_docstring = cls.get("has_docstring", False)
        docstring = cls.get("docstring", "")
        
        # Skip private classes
        if class_name.startswith("_"):
            return
        
        # D101: Missing class docstring
        if not has_docstring:
            self.violations.append({
                "code": "D101",
                "line": start_line,
                "message": f"D101: Missing docstring in public class {class_name}",
                "file": file_path
            })
        else:
            # Validate class docstring format
            if docstring:
                self._validate_docstring_format(docstring, start_line, file_path, source_lines,
                                               class_name, is_function=False)
        
        # Validate methods
        for method in cls.get("methods", []):
            self._validate_function(method, file_path, source_lines, 
                                   is_method=True, class_name=class_name)
    
    def _validate_docstring_format(self, docstring: str, start_line: int, file_path: str,
                                   source_lines: List[str], name: str, is_function: bool = True,
                                   class_name: str = None, func_obj: Dict = None):
        """Validate docstring format against PEP 257 rules."""
        if not docstring:
            return
        
        # Remove triple quotes for analysis
        doc_content = docstring.strip('"""').strip("'''").strip()
        lines = doc_content.split('\n')
        
        # D300: Check for triple double quotes
        if not docstring.strip().startswith('"""'):
            location = f"{class_name}.{name}" if class_name else name
            self.violations.append({
                "code": "D300",
                "line": start_line,
                "message": f"D300: Use triple double quotes for docstrings in {location}",
                "file": file_path
            })
        
        # Check if it's a one-line or multi-line docstring
        is_one_liner = len([l for l in lines if l.strip()]) == 1
        
        if is_one_liner:
            # D200: One-line docstring should fit on one line
            if '\n' in doc_content.strip():
                location = f"{class_name}.{name}" if class_name else name
                self.violations.append({
                    "code": "D200",
                    "line": start_line,
                    "message": f"D200: One-line docstring should fit on one line in {location}",
                    "file": file_path
                })
        else:
            # D209: Multi-line closing quotes on separate line
            if not docstring.rstrip().endswith('\n"""') and not docstring.rstrip().endswith("\n'''"):
                location = f"{class_name}.{name}" if class_name else name
                self.violations.append({
                    "code": "D209",
                    "line": start_line,
                    "message": f"D209: Multi-line docstring closing quotes should be on separate line in {location}",
                    "file": file_path
                })
            
            # D205: Blank line between summary and description
            if len(lines) > 2:
                if lines[1].strip() != '':
                    location = f"{class_name}.{name}" if class_name else name
                    self.violations.append({
                        "code": "D205",
                        "line": start_line + 1,
                        "message": f"D205: 1 blank line required between summary and description in {location}",
                        "file": file_path
                    })
        
        # D400: First line should end with period
        first_line = lines[0].strip() if lines else ""
        if first_line and not first_line.endswith(('.', '!', '?')):
            location = f"{class_name}.{name}" if class_name else name
            self.violations.append({
                "code": "D400",
                "line": start_line,
                "message": f"D400: First line should end with a period in {location}",
                "file": file_path
            })
        
        # D402: First line should not be function signature
        if is_function and first_line and '(' in first_line and ')' in first_line:
            location = f"{class_name}.{name}" if class_name else name
            self.violations.append({
                "code": "D402",
                "line": start_line,
                "message": f"D402: First line should not be the function's signature in {location}",
                "file": file_path
            })
        
        # D202: Check for blank lines AFTER docstring in source
        if source_lines and func_obj and is_function:
            self._check_blank_lines_after_docstring(
                source_lines, start_line, docstring, name, class_name, file_path
            )
    
    def _check_blank_lines_after_docstring(self, source_lines: List[str], start_line: int,
                                           docstring: str, func_name: str, class_name: str,
                                           file_path: str):
        """Check for blank lines after function docstring (D202)."""
        if not source_lines or start_line < 1:
            return
        
        # Calculate where the docstring ends
        # start_line is 1-indexed, convert to 0-indexed
        func_def_idx = start_line - 1
        
        # Find where docstring starts (usually next line after def)
        docstring_start_idx = func_def_idx + 1
        
        # Count how many lines the docstring spans
        docstring_lines = docstring.split('\n')
        docstring_line_count = len(docstring_lines)
        
        # Docstring ends at this index
        docstring_end_idx = docstring_start_idx + docstring_line_count - 1
        
        # Check the line immediately after docstring
        if docstring_end_idx + 1 < len(source_lines):
            line_after_doc = source_lines[docstring_end_idx + 1].strip()
            
            # If there's a blank line after docstring
            if line_after_doc == '':
                # Check if it's truly a blank line (not just end of function)
                if docstring_end_idx + 2 < len(source_lines):
                    next_next_line = source_lines[docstring_end_idx + 2].strip()
                    # If there's actual code after the blank line, it's a violation
                    if next_next_line != '' and not next_next_line.startswith('def ') and not next_next_line.startswith('class '):
                        location = f"{class_name}.{func_name}" if class_name else func_name
                        self.violations.append({
                            "code": "D202",
                            "line": docstring_end_idx + 2,  # Report the line number (1-indexed)
                            "message": f"D202: No blank lines allowed after function docstring in {location} (found 1)",
                            "file": file_path
                        })


def validate_project(scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate entire project for PEP 257 compliance.
    
    Args:
        scan_results: List of parsed file data from python_parser
        
    Returns:
        Dictionary with validation report including violations and metrics
    """
    validator = PEP257Validator()
    all_violations = []
    
    for file_data in scan_results:
        violations = validator.validate_file(file_data)
        all_violations.extend(violations)
    
    # Compute metrics
    total_functions = 0
    total_classes = 0
    compliant_functions = 0
    compliant_classes = 0
    
    for file_data in scan_results:
        funcs = file_data.get("functions", [])
        classes = file_data.get("classes", [])
        
        # Count public functions
        public_funcs = [f for f in funcs if not f.get("name", "").startswith("_")]
        total_functions += len(public_funcs)
        compliant_functions += len([f for f in public_funcs if f.get("has_docstring", False)])
        
        # Count public classes
        public_classes = [c for c in classes if not c.get("name", "").startswith("_")]
        total_classes += len(public_classes)
        compliant_classes += len([c for c in public_classes if c.get("has_docstring", False)])
        
        # Count public methods
        for cls in classes:
            methods = cls.get("methods", [])
            public_methods = [m for m in methods if not m.get("name", "").startswith("_")]
            total_functions += len(public_methods)
            compliant_functions += len([m for m in public_methods if m.get("has_docstring", False)])
    
    total_items = total_functions + total_classes
    compliant_items = compliant_functions + compliant_classes
    
    compliance_rate = (compliant_items / total_items * 100) if total_items > 0 else 0
    violation_count = len(all_violations)
    
    return {
        "total_violations": violation_count,
        "violations": all_violations,
        "total_items": total_items,
        "compliant_items": compliant_items,
        "compliance_percentage": round(compliance_rate, 2),
        "total_functions": total_functions,
        "total_classes": total_classes,
        "compliant_functions": compliant_functions,
        "compliant_classes": compliant_classes
    }