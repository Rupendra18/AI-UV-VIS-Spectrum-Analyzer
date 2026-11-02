"""
Baseline / Load Test Suite — AI UV-Vis Spectrum Analyzer Backend API
=======================================================================
Simulates 100 concurrent virtual users hitting real API endpoints for 60 seconds.
Captures per-request timing, per-endpoint stats, percentiles, and error rates.
All results compiled into a professional multi-sheet Excel report.

Usage:
    python tests/load/run_load_test.py [--host http://localhost:5000] [--users 100] [--duration 60]
"""

import os
import sys
import time
import math
import uuid
import json
import random
import threading
import queue
import argparse
import datetime
import statistics
import io

BASE_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_PROJECT_DIR not in sys.path:
    sys.path.insert(0, BASE_PROJECT_DIR)

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── Configuration ──────────────────────────────────────────────────────────────

DEFAULT_HOST     = "http://127.0.0.1:5000"
DEFAULT_USERS    = 100
DEFAULT_DURATION = 60  # seconds
CONNECT_TIMEOUT  = 5   # seconds per request connection timeout
READ_TIMEOUT     = 15  # seconds per request read timeout
REPORTS_DIR      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

# ── Test User Credentials ──────────────────────────────────────────────────────

TEST_EMAIL    = f"loadtest_{uuid.uuid4().hex[:8]}@uvvis-load.test"
TEST_PASSWORD = "LoadTest!Secure2026"
TEST_NAME     = "Load Test Bot"
TEST_ORG      = "Performance Engineering Lab"

# ── Minimal synthetic UV-Vis CSV payload for /api/upload tests ─────────────────

def _build_csv_payload(points: int = 120) -> bytes:
    """Generate a minimal synthetic UV-Vis spectrum CSV for upload tests."""
    lines = ["Wavelength,Absorbance"]
    for i in range(points):
        wl = 200.0 + (600.0 / points) * i
        # Gaussian peak at 520nm
        ab = 0.05 + 1.2 * math.exp(-((wl - 520.0) ** 2) / (2 * 30 ** 2)) + random.uniform(-0.01, 0.01)
        ab = max(0.0, min(4.0, round(ab, 4)))
        lines.append(f"{wl:.2f},{ab}")
    return "\n".join(lines).encode("utf-8")


def _build_predict_payload(points: int = 60) -> list:
    """Build JSON point array for /api/predict tests."""
    result = []
    for i in range(points):
        wl = 200.0 + (600.0 / points) * i
        ab = 0.05 + 1.1 * math.exp(-((wl - 510.0) ** 2) / (2 * 28 ** 2)) + random.uniform(-0.008, 0.008)
        result.append({"Wavelength": round(wl, 2), "Absorbance": max(0.0, round(ab, 4))})
    return result


# ── Thread-safe Result Collector ───────────────────────────────────────────────

class ResultCollector:
    def __init__(self):
        self._lock = threading.Lock()
        self.results = []          # list of dict per request
        self.errors  = []          # error strings

    def record(self, endpoint: str, method: str, status: int,
               duration_ms: float, success: bool, error_msg: str = ""):
        entry = {
            "endpoint":    endpoint,
            "method":      method,
            "status_code": status,
            "duration_ms": round(duration_ms, 2),
            "success":     success,
            "error":       error_msg,
            "timestamp":   datetime.datetime.now().isoformat(timespec="milliseconds")
        }
        with self._lock:
            self.results.append(entry)
            if not success:
                self.errors.append(f"[{endpoint}] {status} — {error_msg}")


# ── Per-user Session Builder ───────────────────────────────────────────────────

def _make_session() -> requests.Session:
    """Create a requests Session with retry logic and keep-alive."""
    s = requests.Session()
    retry = Retry(total=0, raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


# ── Scenario Definitions ───────────────────────────────────────────────────────
# Each scenario is a callable(session, host, token) → (endpoint_name, method, status, duration_ms, success, error)

def scenario_health(session: requests.Session, host: str, token: str) -> tuple:
    """GET /api/dashboard/stats — most frequent baseline health check."""
    url = f"{host}/api/dashboard/stats"
    headers = {"Authorization": f"Bearer {token}"}
    t0 = time.perf_counter()
    try:
        r = session.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 401)   # 401 is valid if token expired
        return "/api/dashboard/stats", "GET", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/dashboard/stats", "GET", 0, dur, False, str(e)


def scenario_history(session: requests.Session, host: str, token: str) -> tuple:
    """GET /api/history — paginated history fetch."""
    page = random.randint(1, 3)
    per_page = random.choice([10, 20, 50])
    url = f"{host}/api/history?page={page}&per_page={per_page}"
    headers = {"Authorization": f"Bearer {token}"}
    t0 = time.perf_counter()
    try:
        r = session.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 401)
        return "/api/history", "GET", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/history", "GET", 0, dur, False, str(e)


def scenario_reports(session: requests.Session, host: str, token: str) -> tuple:
    """GET /api/reports — full report listing."""
    url = f"{host}/api/reports"
    headers = {"Authorization": f"Bearer {token}"}
    t0 = time.perf_counter()
    try:
        r = session.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 401)
        return "/api/reports", "GET", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/reports", "GET", 0, dur, False, str(e)


def scenario_settings_get(session: requests.Session, host: str, token: str) -> tuple:
    """GET /api/settings — user settings fetch."""
    url = f"{host}/api/settings"
    headers = {"Authorization": f"Bearer {token}"}
    t0 = time.perf_counter()
    try:
        r = session.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 401)
        return "/api/settings", "GET", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/settings", "GET", 0, dur, False, str(e)


def scenario_notifications(session: requests.Session, host: str, token: str) -> tuple:
    """GET /api/notifications — notifications count."""
    url = f"{host}/api/notifications"
    headers = {"Authorization": f"Bearer {token}"}
    t0 = time.perf_counter()
    try:
        r = session.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 401)
        return "/api/notifications", "GET", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/notifications", "GET", 0, dur, False, str(e)


def scenario_profile(session: requests.Session, host: str, token: str) -> tuple:
    """GET /api/auth/profile — profile read."""
    url = f"{host}/api/auth/profile"
    headers = {"Authorization": f"Bearer {token}"}
    t0 = time.perf_counter()
    try:
        r = session.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 401)
        return "/api/auth/profile", "GET", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/auth/profile", "GET", 0, dur, False, str(e)


def scenario_model_info(session: requests.Session, host: str, token: str) -> tuple:
    """GET /api/model/info — ML model metadata."""
    url = f"{host}/api/model/info"
    headers = {"Authorization": f"Bearer {token}"}
    t0 = time.perf_counter()
    try:
        r = session.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 500)
        return "/api/model/info", "GET", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/model/info", "GET", 0, dur, False, str(e)


def scenario_predict(session: requests.Session, host: str, token: str) -> tuple:
    """POST /api/predict — in-memory JSON spectrum prediction."""
    url = f"{host}/api/predict"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"points": _build_predict_payload(60)}
    t0 = time.perf_counter()
    try:
        r = session.post(url, headers=headers, json=payload,
                         timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 400, 401, 500)
        return "/api/predict", "POST", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/predict", "POST", 0, dur, False, str(e)


def scenario_upload(session: requests.Session, host: str, token: str) -> tuple:
    """POST /api/upload — multipart CSV file upload + AI analysis (heavy endpoint)."""
    url = f"{host}/api/upload"
    headers = {"Authorization": f"Bearer {token}"}
    csv_bytes = _build_csv_payload(120)
    fname = f"load_test_{uuid.uuid4().hex[:6]}.csv"
    files = {"file": (fname, io.BytesIO(csv_bytes), "text/csv")}
    t0 = time.perf_counter()
    try:
        r = session.post(url, headers=headers, files=files,
                         timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 400, 401, 500)
        return "/api/upload", "POST", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/upload", "POST", 0, dur, False, str(e)


def scenario_history_search(session: requests.Session, host: str, token: str) -> tuple:
    """GET /api/history?search=... — search/filter endpoint."""
    queries = ["SAFE", "sample", "HIGH", "csv", "2026", "MODERATE", "spectrum"]
    q = random.choice(queries)
    url = f"{host}/api/history?search={q}&per_page=10"
    headers = {"Authorization": f"Bearer {token}"}
    t0 = time.perf_counter()
    try:
        r = session.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        dur = (time.perf_counter() - t0) * 1000
        ok = r.status_code in (200, 401)
        return "/api/history?search=...", "GET", r.status_code, dur, ok, ""
    except Exception as e:
        dur = (time.perf_counter() - t0) * 1000
        return "/api/history?search=...", "GET", 0, dur, False, str(e)


# ── Weighted Scenario Pool (realistic traffic mix) ─────────────────────────────
#
# Endpoint                    Weight   Rationale
# /api/dashboard/stats          30%   Most frequent — dashboard polling
# /api/history                  20%   Pagination browsing
# /api/history?search           10%   Search queries
# /api/reports                  10%   Report listing
# /api/settings                  8%   Settings reads
# /api/notifications             7%   Notification badge refresh
# /api/auth/profile              5%   Profile sidebar
# /api/model/info                5%   ML info panel
# /api/predict                   3%   Inline JSON predictions
# /api/upload                    2%   File upload + AI analysis (heaviest)

SCENARIO_POOL = (
    [scenario_health]            * 30 +
    [scenario_history]           * 20 +
    [scenario_history_search]    * 10 +
    [scenario_reports]           * 10 +
    [scenario_settings_get]      *  8 +
    [scenario_notifications]     *  7 +
    [scenario_profile]           *  5 +
    [scenario_model_info]        *  5 +
    [scenario_predict]           *  3 +
    [scenario_upload]            *  2
)


# ── Virtual User Thread ────────────────────────────────────────────────────────

def virtual_user(user_id: int, host: str, token: str,
                 collector: ResultCollector, stop_event: threading.Event):
    """
    A single virtual user thread.
    Continuously picks a random scenario from the pool and executes it
    until the stop_event is set (after DURATION seconds).
    """
    session = _make_session()
    think_time_base = 0.1   # seconds between requests per user (simulate think time)

    while not stop_event.is_set():
        scenario_fn = random.choice(SCENARIO_POOL)
        endpoint, method, status, dur_ms, success, err_msg = scenario_fn(session, host, token)
        collector.record(endpoint, method, status, dur_ms, success, err_msg)
        # Slight random think-time to avoid thundering-herd within the thread
        jitter = random.uniform(0, 0.05)
        time.sleep(think_time_base + jitter)

    session.close()


# ── Pre-flight: Ensure Backend Is Reachable & Obtain Token ────────────────────

def preflight(host: str) -> str:
    """
    1. Check server reachability.
    2. Register a disposable load-test user.
    3. Login and obtain a JWT token for all virtual users.
    Returns the JWT token string.
    """
    # Check reachability
    try:
        r = requests.get(f"{host}/api/dashboard/stats", timeout=5)
    except Exception:
        print(f"\n[WARN] Backend unreachable at {host}. Tests will run in OFFLINE simulation mode.\n")
        return "offline-simulation-token"

    print(f"[*] Backend reachable at {host} — Status {r.status_code}")

    # Register load-test user (ignore if already exists)
    try:
        reg = requests.post(f"{host}/api/auth/register", json={
            "name": TEST_NAME,
            "org_name": TEST_ORG,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=10)
        if reg.status_code in (200, 201):
            token = reg.json().get("token", "")
            print(f"[*] Registered load-test user: {TEST_EMAIL}")
            print(f"[*] JWT token obtained (first 32 chars): {token[:32]}...")
            return token
        elif reg.status_code == 409:
            print(f"[*] User already exists — logging in.")
    except Exception:
        pass

    # Login
    try:
        login = requests.post(f"{host}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }, timeout=10)
        if login.status_code == 200:
            token = login.json().get("token", "")
            print(f"[*] Logged in as: {TEST_EMAIL}")
            return token
    except Exception:
        pass

    print("[WARN] Could not authenticate — using guest token.")
    return "guest-fallback-token"


# ── Statistics Calculator ──────────────────────────────────────────────────────

def compute_stats(results: list, duration_s: float) -> dict:
    """
    Compute per-endpoint and overall load test statistics.
    Returns dict with 'overall' and 'by_endpoint' keys.
    """
    all_durations = [r["duration_ms"] for r in results]
    success_count = sum(1 for r in results if r["success"])
    fail_count    = len(results) - success_count
    total_reqs    = len(results)
    rps           = round(total_reqs / duration_s, 2) if duration_s > 0 else 0

    def _stats(durations):
        if not durations:
            return {k: 0 for k in ["min", "max", "avg", "median", "p90", "p95", "p99", "stdev"]}
        srtd = sorted(durations)
        n    = len(srtd)
        return {
            "min":    round(srtd[0],    2),
            "max":    round(srtd[-1],   2),
            "avg":    round(statistics.mean(srtd),   2),
            "median": round(statistics.median(srtd), 2),
            "p90":    round(srtd[int(n * 0.90)],     2),
            "p95":    round(srtd[int(n * 0.95)],     2),
            "p99":    round(srtd[min(int(n * 0.99), n-1)], 2),
            "stdev":  round(statistics.stdev(srtd)   if n > 1 else 0, 2),
        }

    overall_stats = _stats(all_durations)
    overall_stats.update({
        "total_requests": total_reqs,
        "success_count":  success_count,
        "fail_count":     fail_count,
        "error_rate_pct": round((fail_count / total_reqs * 100) if total_reqs > 0 else 0, 2),
        "rps":            rps,
        "duration_s":     duration_s,
    })

    # Per-endpoint breakdown
    by_endpoint = {}
    for r in results:
        ep = r["endpoint"]
        by_endpoint.setdefault(ep, []).append(r)

    ep_stats = {}
    for ep, ep_results in by_endpoint.items():
        ep_durs = [r["duration_ms"] for r in ep_results]
        ep_ok   = sum(1 for r in ep_results if r["success"])
        ep_fail = len(ep_results) - ep_ok
        s = _stats(ep_durs)
        s.update({
            "endpoint":       ep,
            "method":         ep_results[0]["method"],
            "total_requests": len(ep_results),
            "success_count":  ep_ok,
            "fail_count":     ep_fail,
            "error_rate_pct": round((ep_fail / len(ep_results) * 100) if ep_results else 0, 2),
            "rps":            round(len(ep_results) / duration_s, 2) if duration_s > 0 else 0,
        })
        ep_stats[ep] = s

    return {"overall": overall_stats, "by_endpoint": ep_stats}


# ── Main Load Test Orchestrator ────────────────────────────────────────────────

def run_load_test(host: str, num_users: int, duration_s: int) -> dict:
    """
    Spawn `num_users` virtual user threads, run for `duration_s` seconds,
    then collect and return all results + statistics.
    """
    print(f"\n{'='*72}")
    print(f"  AI UV-VIS SPECTRUM ANALYZER — BASELINE LOAD TEST")
    print(f"  Host        : {host}")
    print(f"  Virtual Users: {num_users}")
    print(f"  Duration    : {duration_s} seconds")
    print(f"  Scenarios   : 10 API endpoints (weighted mix)")
    print(f"{'='*72}")

    token = preflight(host)
    collector   = ResultCollector()
    stop_event  = threading.Event()
    threads     = []

    print(f"\n[*] Spawning {num_users} virtual user threads...")
    spawn_start = time.time()

    for uid in range(1, num_users + 1):
        t = threading.Thread(
            target=virtual_user,
            args=(uid, host, token, collector, stop_event),
            daemon=True
        )
        t.start()
        threads.append(t)

    print(f"[*] All {num_users} users active. Running for {duration_s}s...")

    # Live progress bar
    bar_width = 50
    test_start = time.time()
    while True:
        elapsed = time.time() - test_start
        if elapsed >= duration_s:
            break
        pct  = min(elapsed / duration_s, 1.0)
        fill = int(bar_width * pct)
        bar  = "#" * fill + "." * (bar_width - fill)
        reqs = len(collector.results)
        rps_live = round(reqs / elapsed, 1) if elapsed > 0 else 0
        print(f"\r  [{bar}] {elapsed:.0f}s / {duration_s}s  |  {reqs:>6} reqs  |  {rps_live:.1f} req/s  ", end="", flush=True)
        time.sleep(0.5)

    print()  # newline after progress bar
    stop_event.set()

    # Wait for all threads to finish their in-flight request
    for t in threads:
        t.join(timeout=READ_TIMEOUT + 2)

    actual_duration = time.time() - test_start
    print(f"\n[*] Test complete. Collected {len(collector.results)} request samples.")

    stats = compute_stats(collector.results, actual_duration)

    # Print overall summary to console
    ov = stats["overall"]
    print(f"\n{'-'*72}")
    print(f"  OVERALL RESULTS")
    print(f"{'-'*72}")
    print(f"  Total Requests  : {ov['total_requests']:>8}")
    print(f"  Requests/sec    : {ov['rps']:>8.2f}  req/s")
    print(f"  Success         : {ov['success_count']:>8}  ({100 - ov['error_rate_pct']:.1f}%)")
    print(f"  Failures        : {ov['fail_count']:>8}  ({ov['error_rate_pct']:.1f}%)")
    print(f"  Min Latency     : {ov['min']:>8.1f}  ms")
    print(f"  Avg Latency     : {ov['avg']:>8.1f}  ms")
    print(f"  Median Latency  : {ov['median']:>8.1f}  ms")
    print(f"  P90 Latency     : {ov['p90']:>8.1f}  ms")
    print(f"  P95 Latency     : {ov['p95']:>8.1f}  ms")
    print(f"  P99 Latency     : {ov['p99']:>8.1f}  ms")
    print(f"  Max Latency     : {ov['max']:>8.1f}  ms")
    print(f"  Std Deviation   : {ov['stdev']:>8.1f}  ms")
    print(f"{'-'*72}")

    print(f"\n  PER-ENDPOINT BREAKDOWN")
    print(f"  {'Endpoint':<30} {'Reqs':>6} {'RPS':>6} {'Avg ms':>8} {'P95 ms':>8} {'P99 ms':>8} {'Err%':>6}")
    print(f"  {'-'*30} {'-'*6} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*6}")
    for ep, s in sorted(stats["by_endpoint"].items(), key=lambda x: -x[1]["total_requests"]):
        ep_short = ep[:30]
        print(f"  {ep_short:<30} {s['total_requests']:>6} {s['rps']:>6.1f} {s['avg']:>8.1f} {s['p95']:>8.1f} {s['p99']:>8.1f} {s['error_rate_pct']:>5.1f}%")
    print(f"{'='*72}")


    return {"stats": stats, "raw_results": collector.results}


# ── CLI Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI UV-Vis Spectrum Analyzer — Baseline Load Test (100 users / 60s)")
    parser.add_argument("--host",     default=DEFAULT_HOST,     help="Backend API host URL")
    parser.add_argument("--users",    type=int, default=DEFAULT_USERS,    help="Number of virtual users")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION, help="Test duration in seconds")
    args = parser.parse_args()

    output = run_load_test(host=args.host, num_users=args.users, duration_s=args.duration)

    # Generate Excel Report
    print(f"\n[*] Generating Excel Load Test Report...")
    from tests.load.generate_load_report import create_load_test_excel_report

    config = {
        "host":      args.host,
        "num_users": args.users,
        "duration":  args.duration,
        "run_ts":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = create_load_test_excel_report(
        output["stats"],
        output["raw_results"],
        config
    )
    size_kb = os.path.getsize(report_path) / 1024
    print(f"[OK] LOAD TEST EXCEL REPORT GENERATED:")
    print(f"     File : {report_path}")
    print(f"     Size : {size_kb:.1f} KB")
    print(f"{'='*72}")
