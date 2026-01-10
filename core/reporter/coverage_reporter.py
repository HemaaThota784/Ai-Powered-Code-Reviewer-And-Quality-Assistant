"""
Compute docstring coverage and write report to JSON.

Coverage is now based on successfully parsed functions, not just documented ones.
"""

import json
from typing import List, Dict, Any


def compute_coverage(per_file_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute parsing coverage statistics from parsed file results.
    Coverage = (total parsed functions / total functions) × 100
    
    Args:
        per_file_results (List[Dict[str, Any]]): List of file parsing results
        
    Returns:
        Dict[str, Any]: Coverage statistics including totals and per-file breakdown
    """
    total_functions = 0
    successfully_parsed_functions = 0
    total_parsing_errors = 0
    
    file_stats = []
    
    for file_result in per_file_results:
        file_path = file_result.get("file_path", "unknown")
        functions = file_result.get("functions", [])
        classes = file_result.get("classes", [])
        parsing_errors = file_result.get("parsing_errors", [])
        
        # Count functions (including methods in classes)
        file_funcs = len(functions)
        file_methods = 0
        
        for cls in classes:
            methods = cls.get("methods", [])
            file_methods += len(methods)
        
        file_total = file_funcs + file_methods
        
        # If there are parsing errors, consider none successfully parsed
        if parsing_errors:
            file_parsed = 0
            total_parsing_errors += len(parsing_errors)
        else:
            file_parsed = file_total
        
        total_functions += file_total
        successfully_parsed_functions += file_parsed
        
        file_coverage = 0.0
        if file_total > 0:
            file_coverage = (file_parsed / file_total) * 100
        
        file_stats.append({
            "file_path": file_path,
            "total_functions": file_total,
            "parsed_functions": file_parsed,
            "parsing_errors": len(parsing_errors),
            "coverage_percentage": round(file_coverage, 2)
        })
    
    overall_coverage = 0.0
    if total_functions > 0:
        overall_coverage = (successfully_parsed_functions / total_functions) * 100
    
    return {
        "total_functions": total_functions,
        "successfully_parsed": successfully_parsed_functions,
        "total_parsing_errors": total_parsing_errors,
        "overall_coverage_percentage": round(overall_coverage, 2),
        "files": file_stats
    }


def write_report(report: Dict[str, Any], path: str) -> None:
    """
    Write coverage report to JSON file.
    
    Args:
        report (Dict[str, Any]): Coverage report dictionary
        path (str): Output file path
        
    Returns:
        None
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)