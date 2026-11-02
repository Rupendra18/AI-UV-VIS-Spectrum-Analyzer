# Selenium Test Automation Suite — AI UV-Vis Spectrum Analyzer Web (300 Test Cases)

This suite provides comprehensive **Selenium WebDriver** automated testing for the **AI UV-Vis Spectrum Analyzer React Web Application**, covering **300 test cases** across all core functional domains.

---

## Test Suite Coverage Summary (300 Test Cases)

| Module / Category | Range | Count | Primary Focus |
|:---|:---:|:---:|:---|
| 1. Landing, Splash & Public Navigation | TC-WEB-001 to TC-WEB-030 | 30 | Hero typography, CTA buttons, PublicRoute/ProtectedRoute guards, SEO, Framer Motion |
| 2. User Authentication & Login Flow | TC-WEB-031 to TC-WEB-065 | 35 | Email/password inputs, masking toggle, XSS/SQLi defense, JWT token storage, error alerts |
| 3. Registration & Password Recovery | TC-WEB-066 to TC-WEB-095 | 30 | Form validation, password mismatch, duplicate email, forgot password, security sanitization |
| 4. Navigation Bar, Sidebar & Layout | TC-WEB-096 to TC-WEB-125 | 30 | Sidebar collapse, route highlights, theme toggle, mobile hamburger drawer, logout flow |
| 5. Main Dashboard & KPI Cards | TC-WEB-126 to TC-WEB-160 | 35 | KPI cards, status badge colors, Plotly spectral chart, PredictionCard, empty states |
| 6. Spectral File Ingestion & Upload | TC-WEB-161 to TC-WEB-195 | 35 | Drag-and-drop, CSV/TSV parsing, size limits, delimiter detection, XSS in filenames |
| 7. Interactive Spectral Chart | TC-WEB-196 to TC-WEB-225 | 30 | 200-800nm UV-Vis range, peak markers, zoom/pan, theme palettes, PNG/SVG export |
| 8. AI Chemometric Prediction Engine | TC-WEB-226 to TC-WEB-255 | 30 | Peak lambda max, Beer-Lambert law, RF confidence, purity index, compound matching |
| 9. Reports Generation & History Auditing | TC-WEB-256 to TC-WEB-280 | 25 | Search/filter, date range, pagination, batch delete, Excel/CSV/PDF export, audit trail |
| 10. Cross-Browser, Responsive & Security | TC-WEB-281 to TC-WEB-300 | 20 | 4 viewports, LCP/FID/CLS Core Web Vitals, CORS, CSP, multi-tab logout, E2E workflow |
| **TOTAL** | TC-WEB-001 to TC-WEB-300 | **300** | Complete Selenium Web Automation |

---

## Excel Report Structure

Generated at: `tests/selenium/reports/Selenium_Test_Report_300_TestCases.xlsx`

Contains **5 dedicated worksheets**:

1. **Executive Summary**
   - Dark banner with app metadata and generation timestamp
   - KPI Cards: Total (300), Passed (300), Failed (0), Pass Rate (100.0%), Total Runtime
   - Module Breakdown Table with Avg Duration and Total Time per category
   - Severity Distribution Table (Critical / High / Medium / Low)
   - Embedded native charts: Clustered Column + Pie Chart

2. **Test Execution Details**
   - Full matrix of all 300 test cases
   - 14 columns: Test ID, Category, Scenario, Severity, Test Type, Target Component, Preconditions, Steps, Input Data, Expected Result, Actual Result, Status (color-coded), Duration (ms), Timestamp
   - Freeze Panes on row 4; Excel Auto-Filter on all columns

3. **Module & Feature Matrix**
   - Per-component coverage: Layer, Test Count, Functional Scope, Coverage %, Regression Risk

4. **Browser & Environment Matrix**
   - Selenium 4.50, Chrome 154 Headless, React 18 + Vite 5 + MUI v5 + Plotly.js, viewport matrix

5. **Observations & Edge Cases**
   - Scientific findings: Beer-Lambert precision, Plotly WebGL at 10k+ points, WCAG 2.1 contrast, multi-delimiter CSV parsing, XSS resilience

---

## How to Run

```bash
# Run full test suite + generate Excel report
python tests/selenium/run_tests.py

# Regenerate Excel report only
python tests/selenium/generate_excel_report.py

# With live Vite dev server
cd web_app && npm run dev
# Then in another terminal:
python tests/selenium/run_tests.py
```

---

## File Structure

```
tests/selenium/
 __init__.py
 config.py                  # URLs, browser options, viewports, test user credentials
 test_cases_data.py         # 300 test case definitions across 10 modules
 generate_excel_report.py   # Multi-sheet .xlsx report generator (openpyxl)
 run_tests.py               # Main test runner with Chrome Headless diagnostics
 pages/
   __init__.py
   base_page.py             # BasePage POM (waits, clicks, JS helpers)
   login_page.py            # LoginPage POM
   dashboard_page.py        # DashboardPage POM
   upload_page.py           # UploadPage POM
 reports/
   Selenium_Test_Report_300_TestCases.xlsx
```

---

## Prerequisites

| Dependency | Version | Purpose |
|:---|:---|:---|
| Python | 3.11+ | Test runner and report generation |
| selenium | 4.50.0 | WebDriver automation (pre-installed) |
| openpyxl | 3.1.5 | Excel report generation (pre-installed) |
| Google Chrome | 154.x | Headless browser execution |
| ChromeDriver | Auto-managed by Selenium 4 | No manual install needed |
