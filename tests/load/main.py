"""
Unified entry point — runs the baseline load test and immediately
generates the Excel report.

Usage:
    python tests/load/main.py                    # defaults: 100 users, 60s, localhost:5000
    python tests/load/main.py --host http://localhost:5000 --users 100 --duration 60
"""

import os
import sys
import argparse
import datetime

# Ensure project root is on path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from tests.load.run_load_test   import run_load_test
from tests.load.generate_load_report import create_load_test_excel_report

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")


def main():
    parser = argparse.ArgumentParser(
        description="AI UV-Vis Spectrum Analyzer — Baseline Load Test (100 VUs / 60s)"
    )
    parser.add_argument("--host",     default="http://127.0.0.1:5000",
                        help="Target API host  (default: http://127.0.0.1:5000)")
    parser.add_argument("--users",    type=int, default=100,
                        help="Number of concurrent virtual users  (default: 100)")
    parser.add_argument("--duration", type=int, default=60,
                        help="Test duration in seconds  (default: 60)")
    args = parser.parse_args()

    # 1. Execute load test
    result = run_load_test(
        host=args.host,
        num_users=args.users,
        duration_s=args.duration
    )

    # 2. Generate Excel report
    print("\n[*] Generating Excel Load Test Report ...")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    config = {
        "host":      args.host,
        "num_users": args.users,
        "duration":  args.duration,
        "run_ts":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    report_path = create_load_test_excel_report(
        result["stats"],
        result["raw_results"],
        config
    )
    size_kb = os.path.getsize(report_path) / 1024
    print(f"[OK] EXCEL REPORT GENERATED:")
    print(f"     {report_path}  ({size_kb:.1f} KB)")
    print(f"{'='*72}")


if __name__ == "__main__":
    main()
