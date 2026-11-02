"""
Page Object Model for Dashboard Page (/dashboard)
"""
from selenium.webdriver.common.by import By
from tests.selenium.pages.base_page import BasePage

class DashboardPage(BasePage):
    KPI_CARDS = (By.CSS_SELECTOR, ".MuiGrid-container .MuiPaper-root, .MuiCard-root")
    TABLE_ROWS = (By.CSS_SELECTOR, "table tbody tr")
    SIDEBAR_DRAWER = (By.CSS_SELECTOR, ".MuiDrawer-paper")
    NAVBAR = (By.CSS_SELECTOR, ".MuiAppBar-root, header")
    THEME_TOGGLE_BTN = (By.CSS_SELECTOR, "button[aria-label*='theme'], button[aria-label*='mode']")
    LOGOUT_BTN = (By.CSS_SELECTOR, "button[aria-label*='logout'], button:has(.MuiSvgIcon-root[data-testid='LogoutIcon'])")
    SPECTRAL_CHART = (By.CSS_SELECTOR, ".js-plotly-plot, .recharts-wrapper, svg.main-svg")

    def open(self):
        return self.navigate_to("/dashboard")

    def get_kpi_card_count(self):
        return len(self.find_all(self.KPI_CARDS))

    def has_spectral_chart(self):
        return self.is_visible(self.SPECTRAL_CHART, timeout=5)
