# AI UV-VIS Spectrum Analyzer — Automated Testing Suite

Comprehensive automated test execution framework for the **AI UV-VIS Spectrum Analyzer** using **Selenium WebDriver** (Web UI/UX, registration, auth, analysis, graph rendering) and **Appium** (Android native UI, biometrics, lifecycle, permissions, chemometrics).

All execution results, KPI dashboards, and failure evidence are automatically compiled into professional Excel workbooks with embedded charts, freeze panes, and filters.

---

## 📁 Test Architecture & Reports Structure

```
test-reports/
├── Selenium_Web_Test_Report.xlsx      # Selenium Web Test Automation Report
├── Appium_Mobile_Test_Report.xlsx     # Appium Android Mobile Test Report
├── Complete_Test_Summary.xlsx         # Unified Executive Dashboard & KPI Matrix
├── requirements.txt                   # Dedicated testing Python dependencies
├── README.md                          # Test suite execution guide
└── screenshots/                       # Visual evidence & failure capture
    ├── selenium/                      # Web test screenshots
    └── appium/                        # Mobile test screenshots
```

---

## 🧪 Modules Tested

### 1. Selenium Web Automation
- **Module A: Registration Testing**: Empty field validation, email format, password complexity (uppercase, lowercase, number, special char, whitespace restriction), confirm password match, duplicate account prevention.
- **Module B: Authentication & Login**: Valid credentials, invalid password, nonexistent email, empty submission, lockouts, session logout.
- **Module C: Dashboard & Navigation**: Dashboard metrics loading, sidebar navigation, view visibility, responsive break-points, session renewal.
- **Module D: UV-VIS Spectrum Analyzer**: CSV dataset ingestion, valid spectrum parsing, bad file format rejection, $\lambda_{\text{max}}$ peak extraction, Plotly graph visualization, PDF report creation, error handling.

### 2. Appium Android Mobile Automation
- **Module A: Mobile Registration**: Field validation, password complexity, confirm password check, invalid submission handling.
- **Module B: Mobile Login**: Valid authentication, invalid password alert, empty inputs, session logout.
- **Module C: Mobile Dashboard**: View hierarchy, interactive components, responsive layout, navigation backstack.
- **Module D: Mobile UV-VIS Features**: Spectrum CSV selection via Document Picker, data curve rendering with MPAndroidChart, peak detection, ML concentration prediction, ISO PDF report generation.
- **Mobile System Scenarios**: App cold/warm launch, crash detection, network loss resilience, runtime permissions, device back-button handling.

---

## 🚀 Execution Instructions

### Prerequisites
1. Python 3.10+
2. Install test dependencies:
   ```bash
   pip install -r test-reports/requirements.txt
   ```

### Running Selenium Tests (Web Application)
1. Start the Flask Backend and React Web App:
   ```bash
   npm run dev
   ```
2. Execute the Selenium test suite:
   ```bash
   python tests/selenium/run_tests.py
   ```

### Running Appium Tests (Android Application)
1. Ensure an Android emulator or USB debugging device is connected:
   ```bash
   adb devices
   ```
2. Start the Appium Server:
   ```bash
   appium --port 4723
   ```
3. Execute the Appium test runner:
   ```bash
   python tests/appium/run_tests.py
   ```

---

## ⚙️ Automated CI/CD (GitHub Actions)

This repository includes automated GitHub Actions workflows:
- `.github/workflows/deploy-pages.yml`: Deploys React Web Frontend to GitHub Pages.
- `.github/workflows/load-test.yml`: Runs 100-user baseline load tests and publishes Excel reports.
- `.github/workflows/dast-test.yml`: Runs dynamic application security testing (DAST).
- `.github/workflows/mobile-qa-suite.yml`: Compiles and publishes 350+ mobile & web automated test reports.
