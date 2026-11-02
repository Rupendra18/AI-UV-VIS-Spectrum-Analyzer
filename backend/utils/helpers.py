import pandas as pd

def classify_status(concentration, safe_limit=5.0):
    """Classify risk level based on analyte concentration and safe threshold."""
    if concentration <= safe_limit:
        return 'SAFE'
    elif concentration <= safe_limit * 2:
        return 'MODERATE'
    else:
        return 'HIGH'


def calculate_confidence_score(df, peak_absorbance):
    """
    Calculate AI confidence score based on Signal-to-Noise Ratio (SNR).
    Score is clamped between 0.0 and 100.0.
    """
    try:
        if isinstance(df, dict):
            absorbances = pd.Series(df.get('Absorbance', []))
        elif isinstance(df, pd.DataFrame):
            absorbances = df['Absorbance'].dropna()
        else:
            absorbances = pd.Series(df)

        mean_abs = absorbances.mean()
        std_abs = absorbances.std()
        if std_abs == 0 or pd.isna(std_abs):
            return 50.0
        snr = (peak_absorbance - mean_abs) / std_abs
        score = min(100.0, max(0.0, snr * 20.0))
        return round(score, 1)
    except Exception:
        return 75.0


def get_interpretation(peak_wavelength, peak_absorbance, concentration, status, confidence):
    """Generate scientific interpretation text for UV-Vis spectral analysis."""
    if peak_wavelength < 280:
        band = "UV-C region (< 280 nm), characteristic of aromatic rings and conjugated systems"
    elif peak_wavelength < 315:
        band = "UV-B region (280–315 nm), commonly associated with nucleic acid and protein absorption"
    elif peak_wavelength < 400:
        band = "UV-A region (315–400 nm), indicative of extended conjugation or transition metal complexes"
    elif peak_wavelength < 500:
        band = "visible violet-blue region, suggesting the presence of coloured chromophores"
    elif peak_wavelength < 600:
        band = "visible green-yellow region, typical of compounds absorbing complementary red light"
    else:
        band = "visible red region (> 600 nm), indicating highly conjugated or metal complex chromophores"

    status_text = {
        'SAFE': 'within the acceptable safe threshold, indicating no immediate concern',
        'MODERATE': 'above the safe threshold but below the high-risk level, warranting further monitoring',
        'HIGH': 'significantly above the safe threshold, indicating a high-risk contamination level'
    }.get(status, 'undetermined')

    conf_text = 'high' if confidence >= 75 else 'moderate' if confidence >= 50 else 'low'

    return (
        f"The UV-Vis absorption spectrum displays a peak at λmax = {peak_wavelength} nm, "
        f"falling within the {band}. The measured peak absorbance of {peak_absorbance} AU "
        f"corresponds to a predicted analyte concentration of {concentration} ppm "
        f"using the Beer-Lambert calibration factor. The contamination risk classification is "
        f"'{status}' — the concentration is {status_text}. "
        f"The AI confidence score is {confidence}% ({conf_text} confidence), reflecting the "
        f"signal-to-noise ratio of the spectral measurement."
    )


def get_conclusion(status, concentration, safe_limit):
    """Generate final safety recommendation based on risk status."""
    if status == 'SAFE':
        return (
            f"The sample concentration of {concentration} ppm is within the safe limit of "
            f"{safe_limit} ppm. No remediation action is required at this time. "
            f"Continue routine monitoring as per standard operating procedures."
        )
    elif status == 'MODERATE':
        return (
            f"The sample concentration of {concentration} ppm exceeds the safe limit of "
            f"{safe_limit} ppm but remains below the high-risk threshold of {safe_limit * 2} ppm. "
            f"Increased monitoring frequency is recommended. Consider investigating potential "
            f"sources of contamination."
        )
    else:
        return (
            f"ALERT: The sample concentration of {concentration} ppm significantly exceeds "
            f"the safe limit of {safe_limit} ppm. Immediate investigation and remediation "
            f"action is required. Do not use this sample without further treatment and "
            f"re-testing by a qualified analyst."
        )
