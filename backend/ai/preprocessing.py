"""
AI Preprocessing Module — UV-Vis Spectrum Analyzer
Feature engineering helpers for ML pipeline.
"""

import numpy as np
import pandas as pd


def extract_features(df: pd.DataFrame) -> dict:
    """
    Extract ML-ready features from a validated spectrum DataFrame.

    Args:
        df: DataFrame with 'Wavelength' and 'Absorbance' columns.

    Returns:
        dict: {
            'peak_wavelength', 'peak_absorbance', 'baseline_absorbance',
            'absorbance_range', 'spectral_width_nm', 'mean_absorbance',
            'std_absorbance', 'snr'
        }
    """
    df = df.copy()
    df['Wavelength'] = pd.to_numeric(df['Wavelength'], errors='coerce')
    df['Absorbance'] = pd.to_numeric(df['Absorbance'], errors='coerce')
    df = df.dropna(subset=['Wavelength', 'Absorbance'])

    if df.empty:
        raise ValueError("No valid spectral data points found after cleaning.")

    peak_idx = df['Absorbance'].idxmax()
    peak_row = df.loc[peak_idx]

    peak_wavelength = round(float(peak_row['Wavelength']), 1)
    peak_absorbance = round(float(peak_row['Absorbance']), 4)
    baseline_absorbance = round(float(df['Absorbance'].min()), 4)
    absorbance_range = round(float(df['Absorbance'].max() - df['Absorbance'].min()), 4)
    spectral_width_nm = round(float(df['Wavelength'].max() - df['Wavelength'].min()), 1)
    mean_absorbance = round(float(df['Absorbance'].mean()), 4)
    std_absorbance = round(float(df['Absorbance'].std()), 4)

    # Signal-to-Noise Ratio
    snr = round((peak_absorbance - mean_absorbance) / std_absorbance, 3) if std_absorbance > 0 else 0.0

    return {
        'peak_wavelength': peak_wavelength,
        'peak_absorbance': peak_absorbance,
        'baseline_absorbance': baseline_absorbance,
        'absorbance_range': absorbance_range,
        'spectral_width_nm': spectral_width_nm,
        'mean_absorbance': mean_absorbance,
        'std_absorbance': std_absorbance,
        'snr': snr,
    }


def build_feature_row(peak_wavelength: float, peak_absorbance: float,
                      baseline_absorbance: float = 0.0) -> pd.DataFrame:
    """
    Build a single-row DataFrame matching the training feature schema.
    Used by predictor.py before scaling.
    """
    return pd.DataFrame([{
        'Peak_Wavelength': float(peak_wavelength),
        'Peak_Absorbance': float(peak_absorbance),
        'Baseline_Absorbance': float(baseline_absorbance),
    }])


def validate_absorbance(value: float) -> bool:
    """Check if absorbance value is physically plausible (0 – 4 AU)."""
    return 0.0 <= value <= 4.0


def validate_wavelength(value: float) -> bool:
    """Check if wavelength is within standard UV-Vis range (190 – 900 nm)."""
    return 190.0 <= value <= 900.0
