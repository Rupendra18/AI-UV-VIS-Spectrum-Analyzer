"""
MainDashboardPage Object Model for MainActivity
"""
from tests.appium.pages.base_page import BasePage

class MainDashboardPage(BasePage):
    ACTIVITY_NAME = ".ui.MainActivity"

    ID_FILE_NAME = "tvCurrentFileName"
    ID_REFRESH_BTN = "btnRefresh"
    ID_SELECT_FILE_BTN = "btnSelectFile"
    ID_PROGRESS_BAR = "progressBar"
    ID_CHART_SPECTRUM = "chartSpectrum"
    ID_PEAK_WAVELENGTH = "tvPeakWavelength"
    ID_PEAK_ABSORBANCE = "tvPeakAbsorbance"
    ID_CONCENTRATION = "tvConcentration"
    ID_STATUS = "tvStatus"
    ID_CONFIDENCE = "tvConfidence"
    ID_INTERPRETATION = "tvInterpretation"

    def click_upload_csv(self):
        self.click_id(self.ID_SELECT_FILE_BTN)

    def click_refresh(self):
        self.click_id(self.ID_REFRESH_BTN)

    def get_current_filename(self):
        return self.get_text(self.ID_FILE_NAME)

    def get_peak_wavelength(self):
        return self.get_text(self.ID_PEAK_WAVELENGTH)

    def get_peak_absorbance(self):
        return self.get_text(self.ID_PEAK_ABSORBANCE)

    def get_concentration(self):
        return self.get_text(self.ID_CONCENTRATION)

    def get_status_text(self):
        return self.get_text(self.ID_STATUS)

    def get_confidence_text(self):
        return self.get_text(self.ID_CONFIDENCE)

    def get_interpretation_text(self):
        return self.get_text(self.ID_INTERPRETATION)

    def is_chart_displayed(self):
        return self.is_displayed(self.ID_CHART_SPECTRUM)

    def is_progress_bar_visible(self):
        return self.is_displayed(self.ID_PROGRESS_BAR)
