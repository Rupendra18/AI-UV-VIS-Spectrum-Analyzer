"""
SplashPage Object Model for SplashActivity
"""
from tests.appium.pages.base_page import BasePage
import time

class SplashPage(BasePage):
    ACTIVITY_NAME = ".ui.SplashActivity"

    def is_splash_active(self):
        return ".ui.SplashActivity" in self.get_current_activity()

    def wait_for_splash_transition(self, timeout=3):
        start = time.time()
        while time.time() - start < timeout:
            if not self.is_splash_active():
                return True
            time.sleep(0.2)
        return False
