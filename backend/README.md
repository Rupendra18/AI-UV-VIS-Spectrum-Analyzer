# AI UV-Vis Spectrum Analyzer 🔬

An advanced Web & Mobile AI application for spectral analysis, peak identification ($\lambda_{\text{max}}$), concentration prediction via Beer-Lambert principles, SNR-based confidence scoring, automated ReportLab PDF reports, and real-time Firebase sync.

---

## 🌟 Key Features

- **Spectral Peak Detection**: Automatic detection of $\lambda_{\text{max}}$ and peak absorbance from uploaded CSV files.
- **AI Concentration Prediction & Risk Assessment**: Instant sample concentration estimation and risk categorization (`SAFE`, `MODERATE`, `HIGH`).
- **Interactive Plotly Visualization**: Dynamic spectrum charts with glowing cyan line, red peak marker, vertical $\lambda_{\text{max}}$ reference line, hover tooltips, and full-screen view.
- **Automated PDF Reports**: High-quality ReportLab PDF generation with executive summaries, metadata, and scientific interpretations.
- **Firebase Integration**: User authentication, Firestore cloud sync (`Users`, `Analyses`, `Reports`, `Settings`), and Cloud Storage for CSV and PDF reports.
- **REST APIs**: Complete JSON endpoints for mobile and third-party integrations under `/api/`.
- **Flutter Mobile App**: Separate Material Design 3 & Glassmorphism application located in `mobile_app/`.

---

## 🚀 Quick Start (Flask Web App)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📱 Mobile App (Flutter)

Located in `mobile_app/`.

Run with Flutter SDK:
```bash
cd mobile_app
flutter pub get
flutter run
```

---

## 📄 REST API Endpoints

- `POST /api/upload`: Upload CSV and perform spectral analysis.
- `POST /api/predict`: Predict concentration from spectral data points array.
- `GET /api/history`: Fetch user's spectral analysis history.
- `GET /api/reports`: Retrieve report download links.
- `GET /api/settings` & `POST /api/settings`: Get or update user threshold settings.
