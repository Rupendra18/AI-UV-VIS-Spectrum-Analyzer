# Baseline & Load Testing Suite — AI UV-Vis Spectrum Analyzer

Automated baseline and concurrent load testing suite for the **AI UV-Vis Spectrum Analyzer REST API**.

Simulates real user behavior with configurable virtual users (default **100 concurrent users**) executing continuous API workflows for a full **60-second window**, evaluating Requests Per Second (RPS), response latency percentiles, error rates, and compiling all metrics into an executive-grade Excel workbook.

---

## 📊 Summary of Optimized Load Test (100 Concurrent Users / 60 Seconds)

| Metric | Original Result | Optimized Result | User Target / SLA | Status | Improvement |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Average Latency** | 1,663.89 ms | **334.0 ms** | < 500 ms | ✅ PASSED | **-80.0% Latency** |
| **Median Latency (P50)** | 1,594.51 ms | **330.8 ms** | < 500 ms | ✅ PASSED | **-79.2% Latency** |
| **90th Percentile (P90)** | 2,180.60 ms | **436.6 ms** | < 800 ms | ✅ PASSED | **-80.0% Latency** |
| **95th Percentile (P95)** | 2,487.87 ms | **478.4 ms** | < 1,000 ms | ✅ PASSED | **-80.8% Latency** |
| **99th Percentile (P99)** | 2,868.26 ms | **647.0 ms** | < 1,500 ms | ✅ PASSED | **-77.4% Latency** |
| **Maximum Latency** | 3,735.40 ms | **1,088.1 ms** | Controlled | ✅ PASSED | **-70.9% Latency** |
| **Throughput (RPS)** | 54.74 req/s | **218.38 req/s** | > 100 req/s | ✅ PASSED | **+299% (4x Boost)** |
| **Total Requests Processed** | 3,452 | **13,316** | Continuous (60s) | ✅ PASSED | **+385% Volume** |
| **Success Rate / Availability**| 100.0% | **100.0%** (13,316/13,316) | 100% | ✅ ZERO ERRORS | Flawless |
| **Failed Requests** | 0 | **0 (0.0% Error Rate)** | 0 | ✅ ZERO ERRORS | Flawless |

---

## 📑 Per-Endpoint Performance Breakdown

| API Endpoint | Method | Requests Handled | RPS | Avg Latency | P95 Latency | P99 Latency | Error Rate |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `/api/dashboard/stats` | `GET` | **4,048** | 66.4 | **328.1 ms** | 454.8 ms | 519.5 ms | **0.0%** |
| `/api/history` | `GET` | **2,685** | 44.0 | **338.8 ms** | 460.4 ms | 524.0 ms | **0.0%** |
| `/api/history?search=...` | `GET` | **1,367** | 22.4 | **332.7 ms** | 458.4 ms | 521.4 ms | **0.0%** |
| `/api/reports` | `GET` | **1,323** | 21.7 | **342.9 ms** | 460.2 ms | 516.2 ms | **0.0%** |
| `/api/settings` | `GET` | **1,005** | 16.5 | **329.7 ms** | 454.2 ms | 517.8 ms | **0.0%** |
| `/api/notifications` | `GET` | **847** | 13.9 | **326.2 ms** | 446.7 ms | 502.1 ms | **0.0%** |
| `/api/model/info` | `GET` | **690** | 11.3 | **189.4 ms** | 286.2 ms | 336.4 ms | **0.0%** |
| `/api/auth/profile` | `GET` | **684** | 11.2 | **328.0 ms** | 446.8 ms | 526.4 ms | **0.0%** |
| `/api/predict` (JSON ML) | `POST` | **417** | 6.8 | **423.6 ms** | 575.8 ms | 649.3 ms | **0.0%** |
| `/api/upload` (CSV Ingestion) | `POST` | **250** | 4.1 | **647.3 ms** | 859.6 ms | 969.6 ms | **0.0%** |
| **TOTAL** | — | **13,316** | **218.38** | **334.0 ms** | **478.4 ms** | **647.0 ms** | **0.0%** |

---

## 📈 Excel Report Structure (5 Worksheets)

The generated report file is saved at:
```
tests/load/reports/Load_Test_Report_20261005_135728.xlsx  (192.9 KB)
```

1. **Executive Summary**:
   - Executive dark banner with run metadata and timestamp.
   - **6 KPI Metric Cards**: Total Requests (13,316), Requests/Sec (218.38), Pass Rate (100.0%), Avg Latency (334.0 ms), P95 Latency (478.4 ms), Max Latency (1088.1 ms).
   - Response time distribution table with SLA threshold indicators.
   - Throughput & reliability audit table.

2. **Per-Endpoint Breakdown**:
   - All 10 endpoints with complete latency percentiles (Min, Avg, Median, P90, P95, P99, Max).
   - **Embedded Column Chart**: Average vs P95 latency per endpoint.

3. **Time-Series Data**:
   - Grouped into 5-second observation buckets over the 60-second test window.
   - **2 Embedded Line Charts**: Requests per Second (RPS) over time & Average Response Time (ms) over time.

4. **Raw Request Log**:
   - Full sample of individual request entries with timestamps, HTTP status, endpoint, method, duration, and PASS/FAIL badge.
   - Excel Auto-Filters and Freeze Panes enabled.

5. **Test Environment**:
   - Concurrency settings, virtual user count, test duration, timeout parameters, payload specifications, and weighted traffic distribution.

---

## 🚀 How to Run the Load Test

### 1. Default Run (100 Virtual Users, 60 Seconds)
```bash
python tests/load/main.py
```

### 2. Custom Parameters
```bash
# 50 users for 30 seconds
python tests/load/main.py --users 50 --duration 30

# 200 users for 2 minutes (120s)
python tests/load/main.py --users 200 --duration 120 --host http://127.0.0.1:5000
```
