import os
import sys
import unittest
import json
import pandas as pd

# Add workspace directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app, load_settings, save_settings, load_analyses, save_analysis
from prediction import analyze_spectrum_df
from predictor import predict_concentration, get_model_metrics
from utils.helpers import classify_status, calculate_confidence_score, get_interpretation, get_conclusion
from utils.validation import validate_and_parse_csv
from utils.graph import build_figure
from utils.pdf import generate_pdf_report
from reports import get_csv_summary_bytes
from history import filter_and_sort_history

class SystemVerificationTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_ml_model_prediction(self):
        """Test ML Random Forest prediction returns algorithm name, accuracy, and concentration."""
        result = predict_concentration(peak_wavelength=320.0, peak_absorbance=1.25, baseline_absorbance=0.05)

        self.assertIn('predicted_concentration', result)
        self.assertIn('algorithm', result)
        self.assertIn('accuracy_percentage', result)
        self.assertIn('rmse', result)
        self.assertIn('mae', result)
        self.assertIn('confidence_score', result)
        self.assertIn('feature_importances', result)

        self.assertGreater(result['predicted_concentration'], 0.0)
        self.assertEqual(result['algorithm'], 'Random Forest Regressor')
        self.assertGreater(result['accuracy_percentage'], 90.0)  # Trained model should be >90%

    def test_02_prediction_pipeline_with_ml(self):
        """Test analyze_spectrum_df uses ML model and returns all expected fields."""
        data = {
            'Wavelength': [200, 250, 300, 320, 350, 400],
            'Absorbance': [0.1, 0.3, 0.7, 1.25, 0.6, 0.2]
        }
        df = pd.DataFrame(data)
        res = analyze_spectrum_df(df, safe_limit=5.0)

        self.assertEqual(res['peak_wavelength'], 320.0)
        self.assertEqual(res['peak_absorbance'], 1.25)
        self.assertGreater(res['predicted_concentration'], 0.0)
        self.assertIn(res['status'], ['SAFE', 'MODERATE', 'HIGH'])
        self.assertGreater(res['confidence_score'], 0.0)
        self.assertIn('algorithm', res)
        self.assertIn('accuracy_percentage', res)
        self.assertIn('rmse', res)
        self.assertIn('mae', res)
        self.assertIn('λmax = 320.0 nm', res['interpretation'])

    def test_03_model_metrics_evaluation(self):
        """Test model metrics contain R2, RMSE, MAE and feature importances."""
        metrics = get_model_metrics()
        self.assertIn('r2_score', metrics)
        self.assertIn('rmse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('feature_importances', metrics)
        self.assertGreater(metrics['r2_score'], 0.90)  # R2 > 90%
        fi = metrics['feature_importances']
        self.assertIn('Peak_Absorbance', fi)
        self.assertIn('Peak_Wavelength', fi)

    def test_04_plotly_figure_generation(self):
        """Test Plotly spectrum graph structure."""
        data = {'Wavelength': [200, 300, 400], 'Absorbance': [0.2, 0.8, 0.1]}
        df = pd.DataFrame(data)
        fig = build_figure(df, 'test_sample.csv', 300.0, 0.8)
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 2)  # Line trace + peak marker trace

    def test_05_pdf_generation_with_ml_fields(self):
        """Test ReportLab PDF compilation includes ML metadata fields."""
        entry = {
            'id': 'test-12345678',
            'timestamp': '2026-08-19 12:00:00',
            'filename': 'test_sample.csv',
            'peak_wavelength': 320.0,
            'peak_absorbance': 1.2,
            'predicted_concentration': 15.0,
            'status': 'HIGH',
            'confidence_score': 92.5,
            'algorithm': 'Random Forest Regressor',
            'accuracy_percentage': 99.74,
            'rmse': 0.48,
            'mae': 0.38,
            'interpretation': 'Sample test interpretation.',
            'conclusion': 'Sample test conclusion.'
        }
        settings = {'org_name': 'Test Lab', 'scientist_name': 'Tester'}
        user_info = {'name': 'Tester'}
        pdf_bytes = generate_pdf_report(entry, settings, user_info)
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_06_csv_export_with_ml_fields(self):
        """Test CSV summary export includes ML algorithm and metrics."""
        entry = {
            'timestamp': '2026-08-19 12:00:00',
            'filename': 'test.csv',
            'peak_wavelength': 320.0,
            'peak_absorbance': 1.25,
            'predicted_concentration': 15.3,
            'status': 'HIGH',
            'confidence_score': 92.5,
            'algorithm': 'Random Forest Regressor',
            'accuracy_percentage': 99.74,
            'rmse': 0.48,
            'mae': 0.38,
            'interpretation': 'Test interpretation.',
            'conclusion': 'Test conclusion.'
        }
        csv_bytes = get_csv_summary_bytes(entry)
        csv_text = csv_bytes.decode('utf-8')
        self.assertIn('ML Algorithm', csv_text)
        self.assertIn('Random Forest Regressor', csv_text)
        self.assertIn('Model Accuracy', csv_text)
        self.assertIn('99.74', csv_text)

    def test_07_history_filtering_and_sorting(self):
        """Test searching, filtering, and sorting analysis history."""
        analyses = [
            {'filename': 'alpha.csv', 'status': 'SAFE', 'predicted_concentration': 2.0},
            {'filename': 'beta.csv', 'status': 'HIGH', 'predicted_concentration': 18.0},
            {'filename': 'gamma.csv', 'status': 'MODERATE', 'predicted_concentration': 7.5},
        ]
        search_res = filter_and_sort_history(analyses, search='alpha')
        self.assertEqual(len(search_res), 1)
        filter_res = filter_and_sort_history(analyses, status_filter='HIGH')
        self.assertEqual(len(filter_res), 1)
        sort_res = filter_and_sort_history(analyses, sort_by='conc_desc')
        self.assertEqual(sort_res[0]['predicted_concentration'], 18.0)

    def test_08_rest_api_predict_with_ml(self):
        """Test /api/predict returns ML algorithm name and accuracy_percentage."""
        payload = {
            'points': [
                {'Wavelength': 250, 'Absorbance': 0.1},
                {'Wavelength': 300, 'Absorbance': 0.9},
                {'Wavelength': 350, 'Absorbance': 0.2}
            ]
        }
        res = self.client.post('/api/predict', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        prediction = data['prediction']
        self.assertEqual(prediction['peak_wavelength'], 300.0)
        self.assertIn('algorithm', prediction)
        self.assertIn('accuracy_percentage', prediction)
        self.assertGreater(prediction['accuracy_percentage'], 90.0)

    def test_09_rest_api_settings(self):
        """Test /api/settings GET and POST."""
        res_set = self.client.get('/api/settings')
        self.assertEqual(res_set.status_code, 200)
        res_update = self.client.post('/api/settings', json={'org_name': 'ML Lab', 'safe_limit': 6.0})
        self.assertEqual(res_update.status_code, 200)

    def test_10_web_routes(self):
        """Test Flask web app GET endpoints remain functional."""
        res_login = self.client.get('/login?nosplash=1')
        self.assertEqual(res_login.status_code, 200)
        res_reg = self.client.get('/register')
        self.assertEqual(res_reg.status_code, 200)
        res_forgot = self.client.get('/forgot-password')
        self.assertEqual(res_forgot.status_code, 200)


if __name__ == '__main__':
    unittest.main()
