import os
import sys

# Ensure backend directory is in python path when run standalone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


if __name__ == '__main__':
    # Ensure terminal output supports UTF-8 on Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print("=" * 65)
    print("  AI UV-VIS SPECTRUM ANALYZER - MACHINE LEARNING INFERENCE ENGINE")
    print("=" * 65)

    sample_file = os.path.join(os.path.dirname(__file__), 'uploads', 'sample_test.csv')
    if os.path.exists(sample_file):
        print(f"\n[INFO] Loading sample spectrum data from:\n       {sample_file}")
        test_df = pd.read_csv(sample_file)
    else:
        print("\n[INFO] Generating synthetic test spectrum DataFrame...")
        import numpy as np
        wl = np.linspace(200, 800, 61)
        ab = 0.05 + 1.25 * np.exp(-((wl - 320) / 40) ** 2)
        test_df = pd.DataFrame({'Wavelength': wl, 'Absorbance': ab})

    print(f"\n[INPUT DATASET PREVIEW] ({len(test_df)} data points):")
    print(test_df.to_string(index=False))

    print("\n[INFO] Executing Random Forest spectral feature analysis and prediction...")
    res = analyze_spectrum_df(test_df)

    print("\n" + "=" * 65)
    print("  SPECTRAL & ML PREDICTION RESULTS")
    print("=" * 65)
    print(f"  Peak Wavelength (Lambda_max) : {res['peak_wavelength']} nm")
    print(f"  Peak Absorbance (Amax)       : {res['peak_absorbance']}")
    print(f"  Baseline Absorbance          : {res['baseline_absorbance']}")
    print(f"  Predicted Concentration      : {res['predicted_concentration']} mg/L")
    print(f"  Safety Status                : {res['status']}")
    print(f"  ML Algorithm                 : {res['algorithm']}")
    print(f"  Model Accuracy               : {res['accuracy_percentage']}%")
    print(f"  Confidence Score             : {res['confidence_score']}%")
    print(f"  Error Metrics                : RMSE = {res['rmse']} | MAE = {res['mae']}")

    if res.get('feature_importances'):
        print("\n[FEATURE IMPORTANCES]")
        for feature, imp in res['feature_importances'].items():
            print(f"  - {feature:<22}: {imp:.4f} ({imp * 100:.1f}%)")

    # Safe encode interpretation and conclusion for display
    interp = res['interpretation'].encode('ascii', errors='replace').decode('ascii')
    concl = res['conclusion'].encode('ascii', errors='replace').decode('ascii')

    print(f"\n[SCIENTIFIC INTERPRETATION]\n  {interp}")
    print(f"\n[CONCLUSION]\n  {concl}")
    print("=" * 65)
