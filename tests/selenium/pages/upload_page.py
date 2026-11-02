"""
Page Object Model for Upload Page (/upload)
"""
from selenium.webdriver.common.by import By
from tests.selenium.pages.base_page import BasePage

class UploadPage(BasePage):
    DROPZONE = (By.CSS_SELECTOR, "div[role='presentation'], .dropzone, input[type='file']")
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
    ANALYZE_BTN = (By.CSS_SELECTOR, "button:contains('Analyze'), button:contains('Upload')")
    PROGRESS_BAR = (By.CSS_SELECTOR, ".MuiLinearProgress-root, .MuiCircularProgress-root")
    SUCCESS_ALERT = (By.CSS_SELECTOR, ".MuiAlert-standardSuccess")
    ERROR_ALERT = (By.CSS_SELECTOR, ".MuiAlert-standardError")

    def open(self):
        return self.navigate_to("/upload")

    def upload_file(self, file_path):
        file_input = self.find(self.FILE_INPUT)
        file_input.send_keys(file_path)
        return self
