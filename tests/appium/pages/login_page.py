"""
LoginPage Object Model for LoginActivity
"""
from tests.appium.pages.base_page import BasePage

class LoginPage(BasePage):
    ACTIVITY_NAME = ".ui.LoginActivity"
    ID_EMAIL = "etEmail"
    ID_PASSWORD = "etPassword"
    ID_LOGIN_BTN = "btnLogin"
    ID_BIOMETRIC_BTN = "btnBiometric"

    def enter_email(self, email):
        self.type_text(self.ID_EMAIL, email)

    def enter_password(self, password):
        self.type_text(self.ID_PASSWORD, password)

    def click_sign_in(self):
        self.click_id(self.ID_LOGIN_BTN)

    def click_biometric(self):
        self.click_id(self.ID_BIOMETRIC_BTN)

    def login(self, email, password):
        self.enter_email(email)
        self.enter_password(password)
        self.click_sign_in()

    def get_login_button_text(self):
        return self.get_text(self.ID_LOGIN_BTN)

    def is_login_button_enabled(self):
        return self.is_enabled(self.ID_LOGIN_BTN)
