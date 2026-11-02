"""
Page Object Model for Login Page (/login)
"""
from selenium.webdriver.common.by import By
from tests.selenium.pages.base_page import BasePage

class LoginPage(BasePage):
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password'], input[type='text']")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_ALERT = (By.CSS_SELECTOR, ".MuiAlert-root")
    FORGOT_PASSWORD_LINK = (By.CSS_SELECTOR, "a[href*='forgot-password']")
    REGISTER_LINK = (By.CSS_SELECTOR, "a[href*='register']")
    TOGGLE_PASSWORD_BTN = (By.CSS_SELECTOR, "button[aria-label*='password'], button .MuiSvgIcon-root[data-testid*='Visibility']")

    def open(self):
        return self.navigate_to("/login")

    def login(self, email, password):
        self.send_keys(self.EMAIL_INPUT, email)
        self.send_keys(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)
        return self

    def get_error_message(self):
        if self.is_visible(self.ERROR_ALERT):
            return self.get_text(self.ERROR_ALERT)
        return ""
