import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

def generate_uv_vis_dataset(num_samples=1200, random_state=42):
    """
    Generate synthetic UV-Vis spectral dataset for analyte concentration prediction.
    Features: Peak_Wavelength (nm), Peak_Absorbance (AU), Baseline_Absorbance (AU)
    Target: Concentration (ppm)
    """
    np.random.seed(random_state)
    
    # Feature distributions
    peak_wavelength = np.random.uniform(200.0, 750.0, num_samples)
    peak_absorbance = np.random.uniform(0.05, 2.5, num_samples)
    baseline_absorbance = np.random.uniform(0.01, 0.15, num_samples)
    
    # Nonlinear Beer-Lambert with stray light correction factor & noise
    # Concentration (ppm) = (Peak_Absorbance - Baseline) * factor + wavelength-dependent shift
    wavelength_factor = 1.0 + 0.15 * np.sin(peak_wavelength / 100.0)
    net_absorbance = np.maximum(0.001, peak_absorbance - baseline_absorbance)
    
    # Beer-Lambert linear term + subtle quadratic saturation at high absorbances
    true_concentration = (net_absorbance * 12.5 * wavelength_factor) + 0.5 * (net_absorbance ** 1.5)
    
    # Add minor measurement noise (e.g. 2% random variation)
    noise = np.random.normal(0, 0.1, num_samples)
    concentration = np.maximum(0.1, true_concentration + noise)
    
    df = pd.DataFrame({
        'Peak_Wavelength': np.round(peak_wavelength, 1),
        'Peak_Absorbance': np.round(peak_absorbance, 4),
        'Baseline_Absorbance': np.round(baseline_absorbance, 4),
        'Concentration': np.round(concentration, 2)
    })
    return df


def train_and_save_model(models_dir=None):
    """
    Train Random Forest Regressor and save artifacts:
    - models/model.pkl
    - models/scaler.pkl
    - models/model_metrics.json
    """
    if models_dir is None:
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
    
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Dataset Generation
    df = generate_uv_vis_dataset(num_samples=1200)
    
    # Save training dataset to models/dataset.csv
    dataset_path = os.path.join(models_dir, 'dataset.csv')
    df.to_csv(dataset_path, index=False)
    
    X = df[['Peak_Wavelength', 'Peak_Absorbance', 'Baseline_Absorbance']]
    y = df['Concentration']
    
    # 2. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 3. Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Train Random Forest Regressor
    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # 5. Model Evaluation
    y_pred = model.predict(X_test_scaled)
    r2 = float(r2_score(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    mae = float(mean_absolute_error(y_test, y_pred))
    
    feature_importances = {
        col: float(imp)
        for col, imp in zip(X.columns, model.feature_importances_)
    }
    
    metrics = {
        'algorithm': 'Random Forest Regressor',
        'r2_score': round(r2, 4),
        'accuracy_percentage': round(r2 * 100.0, 2),
        'rmse': round(rmse, 4),
        'mae': round(mae, 4),
        'n_samples': len(df),
        'n_estimators': 150,
        'feature_importances': feature_importances
    }
    
    # 6. Save Artifacts
    model_path = os.path.join(models_dir, 'model.pkl')
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    metrics_path = os.path.join(models_dir, 'model_metrics.json')
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"[OK] Model trained successfully!")
    print(f"  Algorithm: {metrics['algorithm']}")
    print(f"  R² Score: {metrics['r2_score']} ({metrics['accuracy_percentage']}%)")
    print(f"  RMSE: {metrics['rmse']}")
    print(f"  MAE: {metrics['mae']}")
    print(f"  Saved artifacts to: {models_dir}")
    
    return metrics


if __name__ == '__main__':
    train_and_save_model()
