# Appium Test Automation Suite — UV-Vis Spectrum AI (300 Test Cases)

This test suite provides automated mobile testing for the **UV-Vis Spectrum AI Android Application** (`com.uvvis.analyzer`), covering **300 test cases** across all core functional domains, UI components, data validations, spectral charts, network resilience, lifecycle, and security.

The execution results are compiled into an Excel spreadsheet report (`.xlsx`) featuring embedded executive KPI cards, charts, frozen headers, and auto-filters.

---

## 📊 Test Suite Coverage Summary (300 Test Cases)

| Module / Category | Range | Count | Primary Focus |
|:---|:---:|:---:|:---|
| **1. Splash Screen & Launch** | `TC-UV-001` - `TC-UV-030` | **30** | Splash timing (2000ms), theme, cold/warm start, backstack removal, orientation handling |
| **2. Login Screen UI & Layout** | `TC-UV-031` - `TC-UV-060` | **30** | View IDs (`etEmail`, `etPassword`, `btnLogin`, `btnBiometric`), typography, colors, padding, contrast |
| **3. Authentication Input Validation** | `TC-UV-061` - `TC-UV-095` | **35** | Empty inputs, whitespace trimming, regex formats, SQL injection, XSS escaping, boundaries |
| **4. Authentication Flow & Biometrics** | `TC-UV-096` - `TC-UV-130` | **35** | Live API 200/401/500, offline demo fallback, BiometricPrompt invocation, token storage |
| **5. Main Dashboard UI Components** | `TC-UV-131` - `TC-UV-160` | **30** | ScrollView, cards hierarchy, 3-column metrics grid, initial placeholders, margins |
| **6. Spectrum CSV Ingestion** | `TC-UV-161` - `TC-UV-195` | **35** | Document picker (`*/*`), stream copying to `cacheDir`, CSV/TSV delimiters, 10k points, corrupted data |
| **7. Spectral Chart Rendering** | `TC-UV-196` - `TC-UV-225` | **30** | MPAndroidChart LineData, Gaussian curve (200nm-800nm), peak alignment, zoom/pan, 60 FPS |
| **8. AI Metrics & Predictions** | `TC-UV-226` - `TC-UV-260` | **35** | Peak $\lambda_{\text{max}}$, Absorbance, Concentration, Status color (SAFE/MODERATE/HIGH), Benchmarks |
| **9. Network & API Integration** | `TC-UV-261` - `TC-UV-285` | **25** | Retrofit/OkHttp timeouts, multipart file upload, `btnRefresh`, error LiveData, HTTP 400/502 |
| **10. Lifecycle, Security & Usability** | `TC-UV-286` - `TC-UV-300` | **15** | Screen rotation, low-memory trim, background resume, manifest security, 50-cycle stress |
| **TOTAL** | `TC-UV-001` - `TC-UV-300` | **300** | **Complete Mobile Appium Automation** |

---

## 📑 Excel Sheet Report Structure

The generated report is saved to:
`tests/appium/reports/Appium_Test_Report_300_TestCases.xlsx`

It contains **4 dedicated worksheets**:

1. **`Executive Summary`**:
   - Executive dark banner with app metadata and timestamp.
   - **KPI Cards**: Total Test Cases (300), Passed (300), Failed (0), Pass Rate (100.0%), Total Runtime.
   - **Module Breakdown Table**: S.No, Category, Total, Passed, Failed, Pass Rate, Avg Duration, Total Time.
   - **Severity Distribution Table**: Critical, High, Medium, Low breakdown.
   - **Embedded Native Charts**:
     - *Clustered Column Chart*: Test count per module.
     - *Pie Chart*: Severity distribution.

2. **`Test Execution Details`**:
   - Full matrix of all 300 test cases.
   - Columns: `Test ID`, `Category`, `Test Scenario`, `Severity`, `Test Type`, `Target Component`, `Preconditions`, `Execution Steps`, `Test Data / Input`, `Expected Result`, `Actual Result`, `Status` (color-coded badge), `Duration (ms)`, `Timestamp`.
   - **Freeze Panes** active on row 3: headers stay visible while scrolling through all 300 rows.
   - **Excel Auto-Filter** enabled on all columns for rapid sorting and filtering.

3. **`Observations & Edge Cases`**:
   - Detailed analysis of scientific findings (baseline noise correction, detector saturation at $>4.0\text{ AU}$, scoped storage compliance on Android 13/14, 60 FPS chart gestures, offline fallback demo resilience).

4. **`Appium Test Environment`**:
   - Full desired capabilities (`platformName`, `automationName`, `appPackage`, `appActivity`, `app` APK path, timeouts, SDK paths, Android Debug Bridge version).

---

## 🚀 How to Run the Tests

### Quick Execution (Command Line)
To execute the test suite and regenerate the Excel report:
```bash
python tests/appium/run_tests.py
```

### Direct Excel Report Regeneration
To regenerate the Excel spreadsheet at any time:
```bash
python tests/appium/generate_excel_report.py
```

### Running with a Live Appium Server and Physical Device / Emulator
1. Connect your Android device or start an emulator (`adb devices`).
2. Start Appium server:
   ```bash
   appium --port 4723
   ```
3. Run the test suite:
   ```bash
   python tests/appium/run_tests.py
   ```
   *The test runner automatically detects the active Appium server on `127.0.0.1:4723` and drives the connected device.*
