"""
Excel Report Generator for Load Test Results
Produces a rich 5-sheet .xlsx report with KPI cards, time-series data,
per-endpoint breakdown, raw request log, and test environment details.
"""

import os
import sys
import math
import datetime
import statistics

BASE_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_PROJECT_DIR not in sys.path:
    sys.path.insert(0, BASE_PROJECT_DIR)

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.chart.series import DataPoint

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")


# ── Style Palette ──────────────────────────────────────────────────────────────

NAVY     = "0F172A"
SLATE800 = "1E293B"
SLATE100 = "F1F5F9"
SKY      = "0284C7"
SKY_LITE = "E0F2FE"
WHITE    = "FFFFFF"
GREEN_BG = "DCFCE7"; GREEN_FG = "15803D"
RED_BG   = "FEE2E2"; RED_FG   = "B91C1C"
AMB_BG   = "FEF3C7"; AMB_FG   = "B45309"
TEAL_BG  = "CCFBF1"; TEAL_FG  = "0F766E"


def _font(size=9, bold=False, color="334155", italic=False):
    return Font(name="Segoe UI", size=size, bold=bold, color=color, italic=italic)

def _fill(color):
    return PatternFill(start_color=color, end_color=color, fill_type="solid")

def _border(color="CBD5E1", style="thin"):
    s = Side(border_style=style, color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def _align(h="left", v="center", wrap=True):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

_thin   = _border()
_thick  = Border(bottom=Side(border_style="medium", color=SLATE800))
_center = _align("center")
_left   = _align("left")
_right  = _align("right", wrap=False)

F_TITLE   = _font(18, True, WHITE)
F_SUB     = _font(10, False, "CBD5E1", italic=True)
F_SECTION = _font(13, True, NAVY)
F_HDR     = _font(10, True, WHITE)
F_BOLD    = _font(9,  True,  NAVY)
F_DATA    = _font(9,  False, "334155")
F_PASS    = _font(9,  True,  GREEN_FG)
F_FAIL    = _font(9,  True,  RED_FG)
F_WARN    = _font(9,  True,  AMB_FG)
F_TEAL    = _font(9,  True,  TEAL_FG)

FILL_NAVY   = _fill(NAVY)
FILL_SLATE  = _fill(SLATE800)
FILL_SKY    = _fill(SKY_LITE)
FILL_WHITE  = _fill(WHITE)
FILL_ZEBRA  = _fill(SLATE100)
FILL_PASS   = _fill(GREEN_BG)
FILL_FAIL   = _fill(RED_BG)
FILL_WARN   = _fill(AMB_BG)
FILL_TEAL   = _fill(TEAL_BG)


def _write_header(ws, title: str, subtitle: str, merge_cols: int = 14):
    col_end = get_column_letter(merge_cols)
    ws.merge_cells(f"A1:{col_end}1")
    ws["A1"].value = f"   {title}"
    ws["A1"].font  = F_TITLE
    ws["A1"].fill  = FILL_NAVY
    ws["A1"].alignment = _align("left")

    ws.merge_cells(f"A2:{col_end}2")
    ws["A2"].value = f"   {subtitle}"
    ws["A2"].font  = F_SUB
    ws["A2"].fill  = FILL_SLATE
    ws["A2"].alignment = _align("left")

    ws.row_dimensions[1].height = 32
    ws.row_dimensions[2].height = 20


def _table_header(ws, row: int, headers: list, fill=None, font=None):
    fill = fill or FILL_SLATE
    font = font or F_HDR
    for col, h in enumerate(headers, start=1):
        c = ws.cell(row=row, column=col, value=h)
        c.font      = font
        c.fill      = fill
        c.alignment = _center
        c.border    = _thin


# ── Latency Classification ─────────────────────────────────────────────────────

def _latency_grade(avg_ms: float) -> tuple:
    """Return (grade_str, fill, font) based on average latency."""
    if avg_ms < 200:
        return "Excellent", FILL_PASS,  F_PASS
    elif avg_ms < 500:
        return "Good",      FILL_TEAL,  F_TEAL
    elif avg_ms < 1000:
        return "Acceptable", FILL_WARN, F_WARN
    else:
        return "Poor",      FILL_FAIL,  F_FAIL


def _error_grade(err_pct: float) -> tuple:
    if err_pct < 1:
        return "Pass",  FILL_PASS, F_PASS
    elif err_pct < 5:
        return "Warn",  FILL_WARN, F_WARN
    else:
        return "Fail",  FILL_FAIL, F_FAIL


# ── Time-series Bucketing ─────────────────────────────────────────────────────

def _bucket_timeseries(raw_results: list, bucket_secs: int = 5) -> list:
    """
    Group raw requests into N-second buckets for time-series chart.
    Returns list of dicts: {second, requests, avg_ms, rps, errors}
    """
    if not raw_results:
        return []

    # Parse timestamps
    fmt = "%Y-%m-%dT%H:%M:%S.%f"
    ts_list = []
    for r in raw_results:
        try:
            ts_list.append((datetime.datetime.fromisoformat(r["timestamp"]), r))
        except Exception:
            pass

    if not ts_list:
        return []

    ts_list.sort(key=lambda x: x[0])
    start_ts = ts_list[0][0]

    buckets = {}
    for ts, r in ts_list:
        elapsed = (ts - start_ts).total_seconds()
        bucket  = int(elapsed // bucket_secs) * bucket_secs
        buckets.setdefault(bucket, []).append(r)

    result = []
    all_seconds = sorted(buckets.keys())
    for s in all_seconds:
        reqs = buckets[s]
        durs = [r["duration_ms"] for r in reqs]
        errs = sum(1 for r in reqs if not r["success"])
        result.append({
            "second":   s,
            "requests": len(reqs),
            "avg_ms":   round(statistics.mean(durs), 1) if durs else 0,
            "rps":      round(len(reqs) / bucket_secs, 2),
            "errors":   errs
        })
    return result


# ── Main Report Generator ─────────────────────────────────────────────────────

def create_load_test_excel_report(stats: dict, raw_results: list,
                                   config: dict = None, output_path: str = None) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    if not output_path:
        ts_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(REPORTS_DIR, f"Load_Test_Report_{ts_str}.xlsx")

    config = config or {}
    host      = config.get("host",     "http://localhost:5000")
    num_users = config.get("num_users", 100)
    duration  = config.get("duration",  60)
    run_ts    = config.get("run_ts",    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    ov = stats["overall"]
    ep = stats["by_endpoint"]

    wb = Workbook()

    # =========================================================================
    # SHEET 1 — Executive Summary (KPI Cards + Module Table + Charts)
    # =========================================================================
    ws1 = wb.active
    ws1.title = "Executive Summary"
    ws1.views.sheetView[0].showGridLines = True

    _write_header(ws1,
        "AI UV-VIS SPECTRUM ANALYZER — BASELINE LOAD TEST REPORT",
        f"100 Virtual Users | 60-Second Run | Target: {host} | Generated: {run_ts}",
        merge_cols=12
    )

    # ── KPI Cards Row ──────────────────────────────────────────────────────────
    kpis = [
        ("TOTAL REQUESTS",    str(ov["total_requests"]),          "A4:B5", "A4"),
        ("REQUESTS / SEC",    f"{ov['rps']:.2f}",                 "C4:D5", "C4"),
        ("PASS RATE",         f"{100 - ov['error_rate_pct']:.1f}%", "E4:F5", "E4"),
        ("AVG LATENCY",       f"{ov['avg']:.1f} ms",             "G4:H5", "G4"),
        ("P95 LATENCY",       f"{ov['p95']:.1f} ms",             "I4:J5", "I4"),
        ("MAX LATENCY",       f"{ov['max']:.1f} ms",             "K4:L5", "K4"),
    ]

    for label, val, mrg, topleft in kpis:
        ws1.merge_cells(mrg)
        c = ws1[topleft]
        c.value     = f"{label}\n{val}"
        c.font      = _font(13, True, NAVY)
        c.fill      = FILL_SKY
        c.alignment = _center
        c.border    = _thin

    # Row heights
    ws1.row_dimensions[4].height = 40
    ws1.row_dimensions[5].height = 40

    # ── Response Time Summary ──────────────────────────────────────────────────
    ws1.cell(row=7, column=1, value="Response Time Distribution").font = F_SECTION
    rt_headers = ["Metric", "Value (ms)", "Threshold", "Grade"]
    _table_header(ws1, 8, rt_headers)

    rt_rows = [
        ("Minimum Latency",   ov["min"],    "N/A",    "—"),
        ("Average Latency",   ov["avg"],    "< 500",  _latency_grade(ov["avg"])[0]),
        ("Median Latency",    ov["median"], "< 500",  _latency_grade(ov["median"])[0]),
        ("90th Percentile",   ov["p90"],    "< 800",  _latency_grade(ov["p90"])[0]),
        ("95th Percentile",   ov["p95"],    "< 1000", _latency_grade(ov["p95"])[0]),
        ("99th Percentile",   ov["p99"],    "< 1500", _latency_grade(ov["p99"])[0]),
        ("Maximum Latency",   ov["max"],    "< 3000", "Info"),
        ("Std Deviation",     ov["stdev"],  "—",      "—"),
    ]

    for row_i, (metric, val, threshold, grade) in enumerate(rt_rows, start=9):
        fll = FILL_ZEBRA if row_i % 2 == 0 else FILL_WHITE
        grade_fill, grade_font = FILL_WHITE, F_DATA
        if "Excellent" in str(grade) or "Good" in str(grade):
            grade_fill, grade_font = FILL_PASS, F_PASS
        elif "Acceptable" in str(grade):
            grade_fill, grade_font = FILL_WARN, F_WARN
        elif "Poor" in str(grade):
            grade_fill, grade_font = FILL_FAIL, F_FAIL

        for col_i, (v, f, fv) in enumerate([
            (metric,    F_BOLD, fll),
            (f"{val} ms" if isinstance(val, float) else str(val), F_DATA, fll),
            (threshold, F_DATA, fll),
            (grade,     grade_font, grade_fill),
        ], start=1):
            c = ws1.cell(row=row_i, column=col_i, value=v)
            c.font      = f
            c.fill      = fv
            c.alignment = _center if col_i > 1 else _left
            c.border    = _thin

    # ── Throughput & Error Summary ─────────────────────────────────────────────
    ws1.cell(row=18, column=1, value="Throughput & Reliability").font = F_SECTION
    tp_headers = ["Metric", "Value", "Grade"]
    _table_header(ws1, 19, tp_headers)

    err_pct = ov["error_rate_pct"]
    eg, ef_fill, ef_font = _error_grade(err_pct)
    tp_rows = [
        ("Virtual Users",          str(num_users),                 "—",       FILL_WHITE, F_DATA),
        ("Test Duration",          f"{duration} seconds",          "—",       FILL_ZEBRA, F_DATA),
        ("Total Requests",         str(ov["total_requests"]),      "—",       FILL_WHITE, F_DATA),
        ("Successful Requests",    str(ov["success_count"]),       "—",       FILL_ZEBRA, F_DATA),
        ("Failed Requests",        str(ov["fail_count"]),          "—",       FILL_WHITE, F_DATA),
        ("Requests per Second",    f"{ov['rps']:.2f}",             "> 50 rps", FILL_ZEBRA, F_DATA),
        ("Error Rate",             f"{err_pct:.2f}%",              "< 1%",    FILL_WHITE, F_DATA),
        ("Availability",           f"{100 - err_pct:.2f}%",        "> 99%",   FILL_ZEBRA, F_DATA),
    ]

    for row_i, (metric, val, thr, fll, fnt) in enumerate(tp_rows, start=20):
        for col_i, (v, f, fv) in enumerate([
            (metric, F_BOLD, fll),
            (val,    fnt,   fll),
            (thr,    fnt,   fll),
        ], start=1):
            c = ws1.cell(row=row_i, column=col_i, value=v)
            c.font      = f
            c.fill      = fv
            c.alignment = _center if col_i > 1 else _left
            c.border    = _thin

    # ── Column Widths ─────────────────────────────────────────────────────────
    ws1.column_dimensions["A"].width = 26
    ws1.column_dimensions["B"].width = 16
    ws1.column_dimensions["C"].width = 14
    ws1.column_dimensions["D"].width = 14
    for col in "EFGHIJKL":
        ws1.column_dimensions[col].width = 14

    # =========================================================================
    # SHEET 2 — Per-Endpoint Breakdown
    # =========================================================================
    ws2 = wb.create_sheet("Per-Endpoint Breakdown")
    _write_header(ws2,
        "PER-ENDPOINT PERFORMANCE BREAKDOWN",
        f"All API Endpoints | Sorted by Request Volume | Run: {run_ts}",
        merge_cols=12
    )

    ep_headers = [
        "Endpoint", "Method", "Requests", "RPS",
        "Min (ms)", "Avg (ms)", "Median (ms)", "P90 (ms)", "P95 (ms)", "P99 (ms)", "Max (ms)",
        "Errors", "Error %", "Latency Grade"
    ]
    _table_header(ws2, 4, ep_headers)

    sorted_eps = sorted(ep.items(), key=lambda x: -x[1]["total_requests"])

    for row_i, (endpoint, s) in enumerate(sorted_eps, start=5):
        fll = FILL_ZEBRA if row_i % 2 == 0 else FILL_WHITE
        grade, g_fill, g_font = _latency_grade(s["avg"])
        eg, eg_fill, eg_font  = _error_grade(s["error_rate_pct"])

        row_vals = [
            (endpoint,                   F_BOLD, fll,    _left),
            (s["method"],                F_DATA, fll,    _center),
            (s["total_requests"],        F_DATA, fll,    _center),
            (f"{s['rps']:.2f}",          F_DATA, fll,    _center),
            (f"{s['min']:.1f}",          F_DATA, fll,    _center),
            (f"{s['avg']:.1f}",          F_DATA, fll,    _center),
            (f"{s['median']:.1f}",       F_DATA, fll,    _center),
            (f"{s['p90']:.1f}",          F_DATA, fll,    _center),
            (f"{s['p95']:.1f}",          F_DATA, fll,    _center),
            (f"{s['p99']:.1f}",          F_DATA, fll,    _center),
            (f"{s['max']:.1f}",          F_DATA, fll,    _center),
            (s["fail_count"],            F_DATA, fll if s["fail_count"] == 0 else FILL_FAIL, _center),
            (f"{s['error_rate_pct']:.2f}%", eg_font, eg_fill, _center),
            (grade,                      g_font,  g_fill, _center),
        ]

        for col_i, (v, f, fv, aln) in enumerate(row_vals, start=1):
            c = ws2.cell(row=row_i, column=col_i, value=v)
            c.font      = f
            c.fill      = fv
            c.alignment = aln
            c.border    = _thin

    # Column widths
    ws2.column_dimensions["A"].width = 34
    ws2.column_dimensions["B"].width = 8
    for col in list("CDEFGHIJKLMN"):
        ws2.column_dimensions[col].width = 12

    # ── Bar Chart: Avg Latency per Endpoint ────────────────────────────────────
    # Write data table for chart
    chart_start_row = len(sorted_eps) + 7
    ws2.cell(row=chart_start_row, column=1, value="Endpoint").font = F_HDR
    ws2.cell(row=chart_start_row, column=2, value="Avg Latency (ms)").font = F_HDR
    ws2.cell(row=chart_start_row, column=3, value="P95 Latency (ms)").font = F_HDR

    for i, (endpoint, s) in enumerate(sorted_eps):
        ws2.cell(row=chart_start_row + 1 + i, column=1, value=endpoint.replace("/api/", ""))
        ws2.cell(row=chart_start_row + 1 + i, column=2, value=s["avg"])
        ws2.cell(row=chart_start_row + 1 + i, column=3, value=s["p95"])

    chart_data_end = chart_start_row + len(sorted_eps)

    bar_chart = BarChart()
    bar_chart.type  = "col"
    bar_chart.style = 10
    bar_chart.title = "Average & P95 Latency per Endpoint (ms)"
    bar_chart.y_axis.title = "Latency (ms)"
    bar_chart.width  = 22
    bar_chart.height = 14

    data_ref = Reference(ws2, min_col=2, max_col=3,
                          min_row=chart_start_row, max_row=chart_data_end)
    cats_ref = Reference(ws2, min_col=1,
                          min_row=chart_start_row + 1, max_row=chart_data_end)
    bar_chart.add_data(data_ref, titles_from_data=True)
    bar_chart.set_categories(cats_ref)
    ws2.add_chart(bar_chart, f"O4")

    # =========================================================================
    # SHEET 3 — Time-Series (Requests per 5-Second Bucket)
    # =========================================================================
    ws3 = wb.create_sheet("Time-Series Data")
    _write_header(ws3,
        "REQUEST RATE & LATENCY TIME-SERIES (5-SECOND BUCKETS)",
        f"Visualises load ramp-up, steady-state throughput, and latency trends over 60s",
        merge_cols=8
    )

    ts_headers = ["Bucket (s)", "Requests", "Req/s (RPS)", "Avg Latency (ms)", "Errors"]
    _table_header(ws3, 4, ts_headers)

    buckets = _bucket_timeseries(raw_results, bucket_secs=5)
    ts_data_start = 5

    for row_i, b in enumerate(buckets, start=ts_data_start):
        fll = FILL_ZEBRA if row_i % 2 == 0 else FILL_WHITE
        row_vals = [
            (f"t={b['second']}s", F_BOLD, fll),
            (b["requests"],        F_DATA, fll),
            (b["rps"],             F_DATA, fll),
            (b["avg_ms"],          F_DATA, fll),
            (b["errors"],          F_DATA if b["errors"] == 0 else F_FAIL, fll if b["errors"] == 0 else FILL_FAIL),
        ]
        for col_i, (v, f, fv) in enumerate(row_vals, start=1):
            c = ws3.cell(row=row_i, column=col_i, value=v)
            c.font      = f
            c.fill      = fv
            c.alignment = _center
            c.border    = _thin

    ts_data_end = ts_data_start + len(buckets) - 1

    for col in "ABCDE":
        ws3.column_dimensions[col].width = 20

    if buckets:
        # Line Chart: RPS over time
        line_rps = LineChart()
        line_rps.title  = "Requests per Second Over Time"
        line_rps.style  = 10
        line_rps.y_axis.title = "RPS"
        line_rps.x_axis.title = "Elapsed Time (s)"
        line_rps.width  = 22
        line_rps.height = 12

        rps_ref  = Reference(ws3, min_col=3, min_row=ts_data_start - 1, max_row=ts_data_end)
        cats_rps = Reference(ws3, min_col=1, min_row=ts_data_start,     max_row=ts_data_end)
        line_rps.add_data(rps_ref, titles_from_data=True)
        line_rps.set_categories(cats_rps)
        ws3.add_chart(line_rps, "G4")

        # Line Chart: Avg Latency over time
        line_lat = LineChart()
        line_lat.title  = "Average Response Time Over Time"
        line_lat.style  = 10
        line_lat.y_axis.title = "Avg Latency (ms)"
        line_lat.x_axis.title = "Elapsed Time (s)"
        line_lat.width  = 22
        line_lat.height = 12

        lat_ref  = Reference(ws3, min_col=4, min_row=ts_data_start - 1, max_row=ts_data_end)
        line_lat.add_data(lat_ref, titles_from_data=True)
        line_lat.set_categories(cats_rps)
        ws3.add_chart(line_lat, "G22")

    # =========================================================================
    # SHEET 4 — Raw Request Log (first 5000 rows for Excel feasibility)
    # =========================================================================
    ws4 = wb.create_sheet("Raw Request Log")
    _write_header(ws4,
        "RAW REQUEST LOG (SAMPLE)",
        f"First {min(5000, len(raw_results))} individual requests — full dataset: {len(raw_results)} entries",
        merge_cols=7
    )

    raw_headers = ["#", "Endpoint", "Method", "HTTP Status", "Duration (ms)", "Success", "Timestamp"]
    _table_header(ws4, 4, raw_headers)

    sample = raw_results[:5000]
    for row_i, r in enumerate(sample, start=5):
        fll = FILL_ZEBRA if row_i % 2 == 0 else FILL_WHITE
        ok  = r["success"]
        status_fill = FILL_PASS if ok else FILL_FAIL
        status_font = F_PASS    if ok else F_FAIL
        status_str  = "PASS"   if ok else "FAIL"
        dur_ms = r["duration_ms"]
        dur_fill = fll
        if dur_ms > 1000:
            dur_fill = FILL_FAIL
        elif dur_ms > 500:
            dur_fill = FILL_WARN

        row_vals = [
            (row_i - 4,        F_DATA,       fll,         _center),
            (r["endpoint"],    F_BOLD,       fll,         _left),
            (r["method"],      F_DATA,       fll,         _center),
            (r["status_code"], F_DATA,       fll,         _center),
            (dur_ms,           F_DATA,       dur_fill,    _center),
            (status_str,       status_font,  status_fill, _center),
            (r["timestamp"],   F_DATA,       fll,         _center),
        ]

        for col_i, (v, f, fv, aln) in enumerate(row_vals, start=1):
            c = ws4.cell(row=row_i, column=col_i, value=v)
            c.font      = f
            c.fill      = fv
            c.alignment = aln
            c.border    = _thin

    # Freeze pane + filter
    ws4.freeze_panes = "A5"
    ws4.auto_filter.ref = f"A4:G{len(sample) + 4}"

    ws4.column_dimensions["A"].width = 7
    ws4.column_dimensions["B"].width = 36
    ws4.column_dimensions["C"].width = 9
    ws4.column_dimensions["D"].width = 12
    ws4.column_dimensions["E"].width = 16
    ws4.column_dimensions["F"].width = 10
    ws4.column_dimensions["G"].width = 26

    # =========================================================================
    # SHEET 5 — Test Environment & Configuration
    # =========================================================================
    ws5 = wb.create_sheet("Test Environment")
    _write_header(ws5,
        "LOAD TEST CONFIGURATION & ENVIRONMENT",
        "Runtime environment, scenario weights, and SLA thresholds",
        merge_cols=4
    )

    env_rows = [
        ("Test Tool",              "Python 3.11 threading (built-in concurrent.futures pattern)"),
        ("Load Pattern",           "Baseline / Steady-State (constant load)"),
        ("Virtual Users",          str(num_users)),
        ("Test Duration",          f"{duration} seconds"),
        ("Target Host",            host),
        ("Auth Strategy",          "Bearer JWT (auto-register + login)"),
        ("Scenarios Tested",       "10 API Endpoints (weighted realistic traffic mix)"),
        ("Connect Timeout",        "5 seconds"),
        ("Read Timeout",           "15 seconds"),
        ("Think Time per User",    "100ms + random 0-50ms jitter"),
        ("CSV Upload Payload",     "120-point Gaussian synthetic spectrum (~3KB)"),
        ("JSON Predict Payload",   "60-point Gaussian synthetic spectrum (inline JSON)"),
        ("Total Requests",         str(ov["total_requests"])),
        ("Achieved RPS",           f"{ov['rps']:.2f} req/s"),
        ("Error Rate",             f"{ov['error_rate_pct']:.2f}%"),
        ("SLA: Avg Latency",       "< 500ms  →  " + ("PASS" if ov["avg"] < 500 else "FAIL")),
        ("SLA: P95 Latency",       "< 1000ms →  " + ("PASS" if ov["p95"] < 1000 else "FAIL")),
        ("SLA: P99 Latency",       "< 1500ms →  " + ("PASS" if ov["p99"] < 1500 else "FAIL")),
        ("SLA: Error Rate",        "< 1%     →  " + ("PASS" if ov["error_rate_pct"] < 1 else "FAIL")),
        ("Report Generated",       datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ]

    ws5.cell(row=4, column=1, value="Configuration Property").font = F_HDR
    ws5.cell(row=4, column=1).fill   = FILL_SLATE
    ws5.cell(row=4, column=1).border = _thin
    ws5.cell(row=4, column=2, value="Value / Specification").font  = F_HDR
    ws5.cell(row=4, column=2).fill   = FILL_SLATE
    ws5.cell(row=4, column=2).border = _thin

    for row_i, (prop, val) in enumerate(env_rows, start=5):
        fll = FILL_ZEBRA if row_i % 2 == 0 else FILL_WHITE
        f_v = F_PASS if "PASS" in str(val) else (F_FAIL if "FAIL" in str(val) else F_DATA)
        for col_i, (v, f, fv) in enumerate([
            (prop, F_BOLD, fll),
            (val,  f_v,   fll),
        ], start=1):
            c = ws5.cell(row=row_i, column=col_i, value=v)
            c.font      = f
            c.fill      = fv
            c.border    = _thin
            c.alignment = _left

    ws5.column_dimensions["A"].width = 28
    ws5.column_dimensions["B"].width = 52

    # ── Scenario Weight Table ──────────────────────────────────────────────────
    ws5.cell(row=len(env_rows) + 7, column=1, value="Traffic Scenario Weights").font = F_SECTION

    w_row = len(env_rows) + 8
    _table_header(ws5, w_row, ["Endpoint", "Method", "Weight", "Rationale"])
    w_row += 1

    weights = [
        ("/api/dashboard/stats",   "GET",  "30%", "Most frequent — dashboard polling on every login"),
        ("/api/history",           "GET",  "20%", "Pagination browsing — regular lab auditing"),
        ("/api/history?search=...", "GET", "10%", "Search queries — filtering large datasets"),
        ("/api/reports",           "GET",  "10%", "Report listing — compliance and audit views"),
        ("/api/settings",          "GET",   "8%", "Settings reads — preferences on app open"),
        ("/api/notifications",     "GET",   "7%", "Notification badge refresh — real-time alerts"),
        ("/api/auth/profile",      "GET",   "5%", "Profile reads — sidebar user display"),
        ("/api/model/info",        "GET",   "5%", "ML model info — scientist diagnostics panel"),
        ("/api/predict",           "POST",  "3%", "Inline JSON predictions — direct API calls"),
        ("/api/upload",            "POST",  "2%", "File upload + AI analysis — heaviest endpoint"),
    ]

    for row_i, (ep_name, meth, wt, rationale) in enumerate(weights, start=w_row):
        fll = FILL_ZEBRA if row_i % 2 == 0 else FILL_WHITE
        for col_i, (v, f) in enumerate([
            (ep_name,   F_BOLD),
            (meth,      F_DATA),
            (wt,        F_DATA),
            (rationale, F_DATA),
        ], start=1):
            c = ws5.cell(row=row_i, column=col_i, value=v)
            c.font      = f
            c.fill      = fll
            c.border    = _thin
            c.alignment = _left if col_i != 3 else _center

    # Save workbook (graceful fallback if file is currently open in Excel)
    try:
        wb.save(output_path)
    except PermissionError:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(REPORTS_DIR, f"Load_Test_Report_{ts}.xlsx")
        wb.save(output_path)
    return output_path


# ── Standalone regeneration ────────────────────────────────────────────────────

if __name__ == "__main__":
    # Generate a simulated offline report for preview when backend is unavailable
    import math, random, datetime, statistics

    print("[*] Generating OFFLINE SIMULATION Load Test Excel Report...")

    sim_duration  = 60
    sim_users     = 100
    sim_host      = "http://localhost:5000"
    random.seed(42)

    ENDPOINTS = [
        ("/api/dashboard/stats",    "GET",  120, 210),
        ("/api/history",            "GET",  220, 310),
        ("/api/history?search=...", "GET",  230, 320),
        ("/api/reports",            "GET",  200, 300),
        ("/api/settings",           "GET",  90,  180),
        ("/api/notifications",      "GET",  100, 200),
        ("/api/auth/profile",       "GET",  110, 220),
        ("/api/model/info",         "GET",  140, 280),
        ("/api/predict",            "POST", 380, 720),
        ("/api/upload",             "POST", 550, 1200),
    ]

    WEIGHTS = [30, 20, 10, 10, 8, 7, 5, 5, 3, 2]
    POOL    = []
    for (ep, meth, lo, hi), wt in zip(ENDPOINTS, WEIGHTS):
        POOL.extend([(ep, meth, lo, hi)] * wt)

    raw_results = []
    start_base  = datetime.datetime.now() - datetime.timedelta(seconds=sim_duration)
    total_reqs  = sim_users * 12   # ~12 requests per user over 60s

    for i in range(total_reqs):
        ep, meth, lo, hi = random.choice(POOL)
        dur   = round(random.uniform(lo * 0.5, hi * 1.5), 2)
        ok    = random.random() > 0.003
        ts_dt = start_base + datetime.timedelta(seconds=i * (sim_duration / total_reqs))
        raw_results.append({
            "endpoint":    ep,
            "method":      meth,
            "status_code": 200 if ok else random.choice([500, 503, 0]),
            "duration_ms": dur,
            "success":     ok,
            "error":       "" if ok else "Connection refused",
            "timestamp":   ts_dt.isoformat(timespec="milliseconds")
        })

    all_dur   = [r["duration_ms"] for r in raw_results]
    srtd      = sorted(all_dur)
    n         = len(srtd)
    ok_count  = sum(1 for r in raw_results if r["success"])
    fail_count = n - ok_count

    def _pct(lst, p):
        return round(lst[int(len(lst) * p)], 2)

    overall = {
        "total_requests": n,
        "success_count":  ok_count,
        "fail_count":     fail_count,
        "error_rate_pct": round(fail_count / n * 100, 2),
        "rps":            round(n / sim_duration, 2),
        "duration_s":     float(sim_duration),
        "min":    round(srtd[0], 2),
        "max":    round(srtd[-1], 2),
        "avg":    round(statistics.mean(srtd), 2),
        "median": round(statistics.median(srtd), 2),
        "p90":    _pct(srtd, 0.90),
        "p95":    _pct(srtd, 0.95),
        "p99":    _pct(srtd, 0.99),
        "stdev":  round(statistics.stdev(srtd), 2),
    }

    by_endpoint = {}
    for r in raw_results:
        ep_key = r["endpoint"]
        by_endpoint.setdefault(ep_key, []).append(r)

    ep_stats = {}
    for ep_key, ep_reqs in by_endpoint.items():
        d = sorted(r["duration_ms"] for r in ep_reqs)
        nep = len(d)
        ep_ok  = sum(1 for r in ep_reqs if r["success"])
        ep_stats[ep_key] = {
            "endpoint":       ep_key,
            "method":         ep_reqs[0]["method"],
            "total_requests": nep,
            "success_count":  ep_ok,
            "fail_count":     nep - ep_ok,
            "error_rate_pct": round((nep - ep_ok) / nep * 100, 2),
            "rps":            round(nep / sim_duration, 2),
            "min":    round(d[0], 2),
            "max":    round(d[-1], 2),
            "avg":    round(statistics.mean(d), 2),
            "median": round(statistics.median(d), 2),
            "p90":    _pct(d, 0.90),
            "p95":    _pct(d, 0.95),
            "p99":    _pct(d, 0.99),
            "stdev":  round(statistics.stdev(d) if nep > 1 else 0, 2),
        }

    sim_stats = {"overall": overall, "by_endpoint": ep_stats}
    sim_config = {
        "host":      sim_host,
        "num_users": sim_users,
        "duration":  sim_duration,
        "run_ts":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    report_path = create_load_test_excel_report(sim_stats, raw_results, sim_config)
    size_kb = os.path.getsize(report_path) / 1024
    print(f"[OK] Offline simulation report generated:")
    print(f"     {report_path}  ({size_kb:.1f} KB)")
