"""
Selenium Test Configuration for AI UV-Vis Spectrum Analyzer Web Application
Suite: 300 Web Automated Test Cases
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WEB_APP_DIR = os.path.join(BASE_DIR, "web_app")
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

# Application URLs
WEB_APP_URL = os.environ.get("SELENIUM_WEB_APP_URL", "http://localhost:5173")
BACKEND_URL = os.environ.get("SELENIUM_BACKEND_URL", "http://localhost:5000")

# Browser Configuration
BROWSER_TYPE = os.environ.get("SELENIUM_BROWSER", "chrome").lower()
HEADLESS_MODE = os.environ.get("SELENIUM_HEADLESS", "true").lower() in ("true", "1", "yes")
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 15
PAGE_LOAD_TIMEOUT = 30

# Standard Viewports for Responsive Testing
VIEWPORTS = {
    "desktop_fhd": (1920, 1080),
    "desktop_hd": (1366, 768),
    "tablet_ipad": (768, 1024),
    "mobile_portrait": (375, 812),
}

# Test User Credentials
TEST_USERS = {
    "valid_scientist": {
        "email": "scientist@lab.uvvis.org",
        "password": "SecurePassword123!",
        "name": "Dr. Sarah Chen",
        "org": "Spectroscopy BioTech Labs"
    },
    "invalid_user": {
        "email": "unknown.user@invalid.com",
        "password": "WrongPassword999!"
    },
    "admin_user": {
        "email": "admin@uvvis.org",
        "password": "SuperAdminPass2026!"
    }
}

# Test Configuration Metadata
TEST_CONFIG = {
    "app_name": "AI UV-Vis Spectrum Analyzer Web",
    "version": "1.0.0",
    "framework": "React 18 + Vite 5 + MUI v5 + Plotly.js",
    "environment": "Selenium WebDriver 4.50 (Headless Chrome 154)",
    "target_url": WEB_APP_URL,
    "backend_url": BACKEND_URL,
    "report_file": os.path.join(REPORTS_DIR, "Selenium_Test_Report_300_TestCases.xlsx"),
    "total_test_cases": 300,
    "browser_version": "Chrome 154.0.8037.97",
    "os_platform": "Windows 11 / x86_64",
    "python_version": "3.11+"
}
