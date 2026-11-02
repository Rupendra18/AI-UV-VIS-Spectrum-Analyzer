"""
Base Page Object for Selenium Automated Testing
Provides robust synchronization, error-handling, and DOM interaction utilities.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class BasePage:
    def __init__(self, driver, base_url="http://localhost:5173", timeout=15):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def navigate_to(self, path=""):
        url = f"{self.base_url}/{path.lstrip('/')}"
        self.driver.get(url)
        self.wait_for_page_load()
        return self

    def wait_for_page_load(self):
        try:
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        except TimeoutException:
            pass

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        try:
            self.wait.until(EC.presence_of_element_located(locator))
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        return self

    def send_keys(self, locator, text, clear_first=True):
        element = self.find_visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        return self

    def get_text(self, locator):
        return self.find_visible(locator).text

    def is_visible(self, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def get_current_url(self):
        return self.driver.current_url

    def get_title(self):
        return self.driver.title

    def scroll_into_view(self, locator):
        elem = self.find(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
        time.sleep(0.3)
        return self

    def set_local_storage_item(self, key, value):
        self.driver.execute_script(f"window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

    def get_local_storage_item(self, key):
        return self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def clear_local_storage(self):
        self.driver.execute_script("window.localStorage.clear();")
