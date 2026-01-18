"""
CLI Tool for scanning Python projects and generating JSON reports.

Usage:
    python cli/commands.py scan examples --out storage/review_logs.json

Purpose:
    - Automated scanning for CI/CD pipelines
    - Quick project analysis
    - Generate structured JSON reports

Note: For full documentation coverage analysis and docstring generation, 
      use the Streamlit web app (main_app.py) instead.
"""

import argparse
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
 
from core.parser.python_parser import parse_path
from core.reporter.coverage_reporter import compute_coverage, write_report


def cmd_scan(args):
    """Scan Python files and save report to JSON."""
    results = parse_path(args.path, recursive=True)

    if not results:
        print("[WARNING] No Python files found!")
        return

    out_path = args.out
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    write_report({"parsed_results": results}, out_path)

    print(f"[INFO] Report saved at: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="AI Code Reviewer CLI Tool")
    sub = parser.add_subparsers(dest="command")
    
    scan_cmd = sub.add_parser("scan", help="Scan a folder or file")
    scan_cmd.add_argument("path", help="Path to file or directory")
    scan_cmd.add_argument(
        "--out",
        default="storage/review_logs.json",
        help="Output JSON file path"
    )

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
