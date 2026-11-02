import pandas as pd
from utils.helpers import classify_status, get_interpretation, get_conclusion
from predictor import predict_concentration

def analyze_spectrum_df(df, concentration_factor=12.5, safe_limit=5.0):
    """
    Analyze spectrum DataFrame using Random Forest Regressor ML model to predict concentration.
    Returns peak wavelength, peak absorbance, predicted concentration, ML algorithm name,
    model accuracy, confidence score, RMSE, MAE, feature importances, scientific interpretation,
    and conclusion.
    """
    import numpy as np

    # Fast path if already clean numeric DataFrame
    cols = [str(c).strip() for c in df.columns]
    if 'Wavelength' in cols and 'Absorbance' in cols:
        try:
            wl = pd.to_numeric(df['Wavelength'], errors='coerce').to_numpy(dtype=np.float64, copy=False)
            ab = pd.to_numeric(df['Absorbance'], errors='coerce').to_numpy(dtype=np.float64, copy=False)
            valid = ~np.isnan(wl) & ~np.isnan(ab)
            if np.any(valid):
                wl = wl[valid]
                ab = ab[valid]
                idx_max = int(np.argmax(ab))
                peak_wavelength = round(float(wl[idx_max]), 1)
                peak_absorbance = round(float(ab[idx_max]), 4)
                baseline_absorbance = round(float(np.min(ab)), 4)
            else:
                raise ValueError("No valid spectral data points found.")
        except Exception:
            df = df.copy()
            df.columns = df.columns.astype(str).str.strip()
            df['Wavelength'] = pd.to_numeric(df['Wavelength'], errors='coerce')
            df['Absorbance'] = pd.to_numeric(df['Absorbance'], errors='coerce')
            df = df.dropna(subset=['Wavelength', 'Absorbance'])
            if df.empty:
                raise ValueError("No valid spectral data points found.")
            idx_max = df['Absorbance'].idxmax()
            peak_row = df.loc[idx_max]
            peak_wavelength = round(float(peak_row['Wavelength']), 1)
            peak_absorbance = round(float(peak_row['Absorbance']), 4)
            baseline_absorbance = round(float(df['Absorbance'].min()), 4)
    else:
        df = df.copy()
        df.columns = df.columns.astype(str).str.strip()
        df['Wavelength'] = pd.to_numeric(df['Wavelength'], errors='coerce')
        df['Absorbance'] = pd.to_numeric(df['Absorbance'], errors='coerce')
        df = df.dropna(subset=['Wavelength', 'Absorbance'])
        if df.empty:
            raise ValueError("No valid spectral data points found.")
        idx_max = df['Absorbance'].idxmax()
        peak_row = df.loc[idx_max]
        peak_wavelength = round(float(peak_row['Wavelength']), 1)
        peak_absorbance = round(float(peak_row['Absorbance']), 4)
        baseline_absorbance = round(float(df['Absorbance'].min()), 4)

    # ML Model Concentration Prediction
    ml_res = predict_concentration(
        peak_wavelength=peak_wavelength,
        peak_absorbance=peak_absorbance,
        baseline_absorbance=baseline_absorbance
    )

    predicted_concentration = ml_res['predicted_concentration']
    algorithm_name = ml_res['algorithm']
    model_accuracy = ml_res['accuracy_percentage']
    confidence_score = ml_res['confidence_score']
    rmse = ml_res['rmse']
    mae = ml_res['mae']
    feature_importances = ml_res['feature_importances']

    status = classify_status(predicted_concentration, safe_limit)
    interpretation = get_interpretation(
        peak_wavelength, peak_absorbance, predicted_concentration, status, confidence_score
    )
    conclusion = get_conclusion(status, predicted_concentration, safe_limit)

    return {
        'peak_wavelength': peak_wavelength,
        'peak_absorbance': peak_absorbance,
        'baseline_absorbance': baseline_absorbance,
        'predicted_concentration': predicted_concentration,
        'algorithm': algorithm_name,
        'accuracy_percentage': model_accuracy,
        'confidence_score': confidence_score,
        'rmse': rmse,
        'mae': mae,
        'feature_importances': feature_importances,
        'status': status,
        'interpretation': interpretation,
        'conclusion': conclusion,
    }
