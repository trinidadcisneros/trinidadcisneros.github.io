#!/usr/bin/env python3
"""
Controller script: Runs all 15 model notebooks sequentially.
Captures output and errors, then prints a summary report.

Usage:
    cd notebooks/models/
    python run_all.py
"""

import subprocess
import sys
import time
import json
from pathlib import Path

# All 15 model notebooks in execution order
NOTEBOOKS = [
    "01_logistic_regression.ipynb",
    "02_lda.ipynb",
    "03_qda.ipynb",
    "04_knn.ipynb",
    "05_naive_bayes.ipynb",
    "06_decision_tree.ipynb",
    "07_random_forest.ipynb",
    "08_bagging.ipynb",
    "09_adaboost.ipynb",
    "10_gradient_boosting.ipynb",
    "11_xgboost.ipynb",
    "12_lightgbm.ipynb",
    "13_catboost.ipynb",
    "14_svm.ipynb",
    "15_mlp.ipynb",
]

MODELS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODELS_DIR.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "outputs"


def run_notebook(nb_path):
    """
    Execute a notebook using nbconvert and return (success, duration, error_msg, output).
    """
    start = time.time()
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "jupyter", "nbconvert",
                "--to", "notebook",
                "--execute",
                "--ExecutePreprocessor.timeout=600",
                "--ExecutePreprocessor.kernel_name=python3",
                "--output", nb_path.name,
                str(nb_path),
            ],
            capture_output=True,
            text=True,
            timeout=660,
            cwd=str(MODELS_DIR),
        )
        duration = time.time() - start

        if result.returncode != 0:
            # Extract the most relevant error from stderr
            stderr = result.stderr
            # Try to find the actual Python traceback
            lines = stderr.split("\n")
            error_lines = []
            in_traceback = False
            for line in lines:
                if "Traceback" in line or "Error" in line or "Exception" in line:
                    in_traceback = True
                if in_traceback:
                    error_lines.append(line)
            error_msg = "\n".join(error_lines[-20:]) if error_lines else stderr[-2000:]
            return False, duration, error_msg, result.stdout

        return True, duration, None, result.stdout

    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return False, duration, "TIMEOUT: Notebook took longer than 600 seconds", ""
    except Exception as e:
        duration = time.time() - start
        return False, duration, f"EXCEPTION: {type(e).__name__}: {str(e)}", ""


def check_outputs(model_slug):
    """Check what chart files were generated for a model."""
    model_dir = OUTPUT_DIR / model_slug
    if not model_dir.exists():
        return []
    return sorted([f.name for f in model_dir.glob("*.html")])


def extract_slug(nb_name):
    """Extract model slug from notebook name: '01_logistic_regression.ipynb' -> 'logistic_regression'"""
    stem = nb_name.replace(".ipynb", "")
    # Remove the leading number and underscore
    parts = stem.split("_", 1)
    return parts[1] if len(parts) > 1 else parts[0]


def main():
    print("=" * 80)
    print("  MODEL NOTEBOOK CONTROLLER")
    print("  Running all 15 model notebooks")
    print("=" * 80)
    print(f"\n  Working directory: {MODELS_DIR}")
    print(f"  Output directory:  {OUTPUT_DIR}")
    print(f"  Notebooks found:   {sum(1 for nb in NOTEBOOKS if (MODELS_DIR / nb).exists())}/15")
    print()

    # Check which notebooks exist
    missing = [nb for nb in NOTEBOOKS if not (MODELS_DIR / nb).exists()]
    if missing:
        print("  WARNING: Missing notebooks:")
        for nb in missing:
            print(f"    - {nb}")
        print()

    results = []
    total_start = time.time()

    for i, nb_name in enumerate(NOTEBOOKS, 1):
        nb_path = MODELS_DIR / nb_name
        slug = extract_slug(nb_name)

        if not nb_path.exists():
            results.append({
                "notebook": nb_name,
                "slug": slug,
                "success": False,
                "duration": 0,
                "error": "FILE NOT FOUND",
                "charts": [],
            })
            continue

        print(f"[{i:2d}/15] Running {nb_name}...", end=" ", flush=True)

        success, duration, error, output = run_notebook(nb_path)
        charts = check_outputs(slug)

        results.append({
            "notebook": nb_name,
            "slug": slug,
            "success": success,
            "duration": duration,
            "error": error,
            "charts": charts,
        })

        status = "OK" if success else "FAIL"
        print(f"{status} ({duration:.1f}s, {len(charts)} charts)")

        if not success and error:
            # Print first few lines of error
            err_preview = error.strip().split("\n")
            for line in err_preview[:5]:
                print(f"         {line}")
            if len(err_preview) > 5:
                print(f"         ... ({len(err_preview) - 5} more lines)")

    total_duration = time.time() - total_start

    # ============================================================
    # SUMMARY REPORT
    # ============================================================
    print("\n" + "=" * 80)
    print("  SUMMARY REPORT")
    print("=" * 80)

    passed = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])

    print(f"\n  Total:  {len(results)} notebooks")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Time:   {total_duration:.0f}s ({total_duration/60:.1f} min)")

    # Status table
    print(f"\n  {'Notebook':<40} {'Status':<8} {'Time':>8} {'Charts':>8}")
    print(f"  {'-'*40} {'-'*8} {'-'*8} {'-'*8}")
    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        time_str = f"{r['duration']:.1f}s"
        charts_str = str(len(r["charts"]))
        print(f"  {r['notebook']:<40} {status:<8} {time_str:>8} {charts_str:>8}")

    # Detailed errors
    if failed > 0:
        print(f"\n{'='*80}")
        print("  ERRORS (details)")
        print(f"{'='*80}")
        for r in results:
            if not r["success"] and r["error"]:
                print(f"\n  --- {r['notebook']} ---")
                print(f"  {r['error']}")

    # Chart inventory
    print(f"\n{'='*80}")
    print("  CHART INVENTORY")
    print(f"{'='*80}")
    total_charts = 0
    for r in results:
        n = len(r["charts"])
        total_charts += n
        status = "OK" if n > 0 else "EMPTY"
        print(f"\n  [{status}] {r['slug']}/ ({n} charts)")
        for chart in r["charts"]:
            print(f"       - {chart}")

    print(f"\n  Total charts generated: {total_charts}")

    # Write JSON report
    report_path = MODELS_DIR / "run_all_report.json"
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_notebooks": len(results),
        "passed": passed,
        "failed": failed,
        "total_duration_seconds": round(total_duration, 1),
        "total_charts": total_charts,
        "results": [{
            "notebook": r["notebook"],
            "slug": r["slug"],
            "success": r["success"],
            "duration_seconds": round(r["duration"], 1),
            "charts_generated": len(r["charts"]),
            "chart_files": r["charts"],
            "error": r["error"],
        } for r in results],
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report saved to: {report_path.name}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
