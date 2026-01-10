import argparse
import json
import os

from core.parser.python_parser import parse_path
from core.docstring_engine.generator import generate_google_docstring
from core.reporter.coverage_reporter import compute_coverage, write_report


def _attach_generated_docstrings(results, generate_docs: bool = False):
    """
    Attach auto-generated Google-style docstrings to parsed functions/classes
    if --generate-docs flag is passed.
    """
    if not generate_docs:
        return results

    for file_info in results:
        for func in file_info.get("functions", []):
            doc = generate_google_docstring(
                name=func["name"],
                args=func["args"],
                returns=func["returns"],
                description="Auto-generated documentation."
            )
            func["generated_docstring"] = doc

        for cls in file_info.get("classes", []):
            for method in cls.get("methods", []):
                doc = generate_google_docstring(
                    name=method["name"],
                    args=method["args"],
                    returns=method["returns"],
                    description=f"Auto-generated docs for method of class {cls['name']}."
                )
                method["generated_docstring"] = doc

    return results


def cmd_scan(args):
    """
    Execute `scan` command:
    - parse files
    - generate docstrings (optional)
    - compute coverage
    - save output JSON
    """

    print(f"[INFO] Scanning path: {args.path}")
    results = parse_path(args.path, recursive=True)

    # Attach generated docstrings if enabled
    results = _attach_generated_docstrings(results, args.generate_docs)

    # Compute coverage report
    coverage = compute_coverage(results)

    output_data = {
        "parsed_results": results,
        "coverage": coverage
    }

    # Save final output JSON
    out_path = args.out
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    write_report(output_data, out_path)

    print(f"[INFO] Scan completed. Report saved at: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Run Milestone 1 scan")

    sub = parser.add_subparsers(dest="command")

    scan_cmd = sub.add_parser("scan", help="Scan a folder or file")
    scan_cmd.add_argument("path", help="Path to file or directory")
    scan_cmd.add_argument(
        "--out",
        default="storage/review_logs.json",
        help="Output JSON file path"
    )
    scan_cmd.add_argument(
        "--generate-docs",
        action="store_true",
        help="Generate Google-style docstrings"
    )

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
