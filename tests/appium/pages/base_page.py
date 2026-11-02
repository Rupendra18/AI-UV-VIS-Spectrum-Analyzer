"""
BasePage for Appium Test Automation Suite
Provides explicit wait methods, element finding, touch actions, and assertions.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
import time

class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(self.driver, timeout) if self.driver else None

    def find(self, by, value):
        if not self.driver:
            return None
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_by_id(self, resource_id):
        full_id = f"com.uvvis.analyzer:id/{resource_id}" if not resource_id.startswith("com.") else resource_id
        return self.find(AppiumBy.ID, full_id)

    def click(self, by, value):
        el = self.wait.until(EC.element_to_be_clickable((by, value)))
        el.click()

    def click_id(self, resource_id):
        full_id = f"com.uvvis.analyzer:id/{resource_id}" if not resource_id.startswith("com.") else resource_id
        self.click(AppiumBy.ID, full_id)

    def type_text(self, resource_id, text):
        el = self.find_by_id(resource_id)
        if el:
            el.clear()
            el.send_keys(text)

    def get_text(self, resource_id):
        el = self.find_by_id(resource_id)
        return el.text if el else ""

    def is_displayed(self, resource_id):
        try:
            el = self.find_by_id(resource_id)
            return el.is_displayed() if el else False
        except Exception:
            return False

    def is_enabled(self, resource_id):
        try:
            el = self.find_by_id(resource_id)
            return el.is_enabled() if el else False
        except Exception:
            return False

    def get_current_activity(self):
        if not self.driver:
            return ""
        return getattr(self.driver, "current_activity", "")
