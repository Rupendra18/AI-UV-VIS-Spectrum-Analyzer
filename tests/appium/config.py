"""
Appium Test Configuration for UV-Vis Spectrum AI Android Application
Package: com.uvvis.analyzer
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APK_PATH = os.path.join(BASE_DIR, "android_app", "app", "build", "outputs", "apk", "debug", "app-debug.apk")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

APPIUM_SERVER_URL = "http://127.0.0.1:4723"

DESIRED_CAPABILITIES = {
    "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": "Android_Emulator_API_34",
    "app": APK_PATH,
    "appPackage": "com.uvvis.analyzer",
    "appActivity": "com.uvvis.analyzer.ui.SplashActivity",
    "noReset": False,
    "fullReset": False,
    "newCommandTimeout": 300,
    "autoGrantPermissions": True,
    "ensureWebviewsHavePages": True,
    "nativeWebScreenshot": True,
    "connectHardwareKeyboard": True,
    "gpsEnabled": False
}

TEST_CONFIG = {
    "app_name": "UV-Vis Spectrum AI",
    "version": "1.0.0",
    "environment": "Android 13/14 (UiAutomator2)",
    "target_package": "com.uvvis.analyzer",
    "backend_url": "http://10.0.2.2:5000",
    "report_file": os.path.join(REPORTS_DIR, "Appium_Test_Report_300_TestCases.xlsx"),
    "total_test_cases": 300
}
