<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Kotlin-MVVM-7F52FF?logo=kotlin&logoColor=white" />
  <img src="https://img.shields.io/badge/Firebase-Auth%20%7C%20Firestore%20%7C%20Storage-FFCA28?logo=firebase&logoColor=black" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

# 🧪 AI UV-Vis Spectrum Analyzer

An **enterprise-grade, multi-platform** chemical analysis software suite powered by **Machine Learning**, interactive spectral plotting, automated peak detection, and PDF report generation.

> Built with Python Flask · React 18 + Vite · Kotlin MVVM · Firebase · scikit-learn

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Category | Highlights |
|----------|-----------|
| 🤖 **AI/ML Engine** | Random Forest Regressor predicting concentration from UV-Vis spectral curves with **R² ≈ 99.7%** accuracy |
| ⚛️ **React Web App** | Vite-powered SPA with Material UI v5, glassmorphism design, Plotly interactive charts, Framer Motion animations |
| 📱 **Android App** | Native Kotlin app with MVVM architecture, Retrofit, Coroutines, and **biometric fingerprint** login |
| 🔐 **Authentication** | Firebase Auth (email/password) with local JSON fallback; JWT-based API tokens |
| 📊 **Spectral Analysis** | Automated λmax peak detection, absorbance/transmittance conversion, multi-wavelength plotting |
| 📄 **PDF Reports** | ISO-style ReportLab documents with peak highlights, QR codes, scientist signatures, AI confidence scores |
| 🔥 **Firebase** | Unified Authentication, Firestore database, and Cloud Storage with graceful local fallback |
| 🧪 **Comprehensive Testing** | 300+ Appium mobile tests, 300+ Selenium web tests, load testing with Excel reports |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  React 18 +  │  │  Kotlin MVVM     │  │  Flutter (Dart)  │   │
│  │  Vite Web    │  │  Android App     │  │  Mobile App      │   │
│  └──────┬───────┘  └──────┬───────────┘  └──────┬───────────┘   │
└─────────┼─────────────────┼──────────────────────┼──────────────┘
          │     REST API    │                      │
          ▼                 ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask REST API)                      │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Auth &   │  │ Spectrum  │  │ Report   │  │ ML Prediction │  │
│  │ Users    │  │ Analysis  │  │ Builder  │  │ Engine        │  │
│  └──────────┘  └───────────┘  └──────────┘  └───────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │  Firebase  │ │ Local JSON │ │ ML Models  │
   │  Cloud     │ │ Fallback   │ │ (sklearn)  │
   └────────────┘ └────────────┘ └────────────┘
```

---

## 📁 Project Structure

```
AI_UV_VIS_SPECTRUM_ANALYZER/
│
├── backend/                    # Python Flask REST API & ML Engine
│   ├── ai/                    # AI preprocessing pipeline
│   ├── api/                   # REST API route definitions
│   ├── models/                # Trained ML model & dataset
│   ├── static/                # CSS, JS, images for web templates
│   ├── templates/             # Jinja2 HTML templates
│   ├── utils/                 # Firebase, PDF, graph, validation utilities
│   ├── app.py                 # Flask application entry point
│   ├── prediction.py          # Spectrum prediction logic
│   ├── predictor.py           # ML model training & inference
│   ├── train_model.py         # Model training script
│   └── requirements.txt       # Python dependencies
│
├── web_app/                    # React 18 + Vite Glassmorphism Web App
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── contexts/          # React Context (Auth)
│   │   ├── firebase/          # Firebase configuration
│   │   ├── pages/             # Page-level components
│   │   ├── services/          # API service layer
│   │   └── theme/             # MUI theme customization
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── android_app/                # Kotlin MVVM Native Android App
│   └── app/src/main/
│       └── java/com/uvvis/analyzer/
│           ├── data/          # Models & Repository
│           ├── network/       # Retrofit API client
│           └── ui/            # Activities & ViewModel
│
├── firebase/                   # Firebase Security Rules & Config
├── datasets/                   # UV-Vis ML Training Dataset (1200 samples)
├── deployment/                 # Docker, Render, Vercel configs
├── docs/                       # Architecture, API, Install & Deploy guides
├── tests/                      # Comprehensive Test Suites
│   ├── appium/                # 300+ Mobile automation tests
│   ├── selenium/              # 300+ Web automation tests
│   ├── load/                  # Performance & load testing
│   └── backend/               # Backend unit tests
├── automated_test/             # DAST security testing framework
│
├── .gitignore
├── LICENSE                     # MIT License
├── package.json                # Root dev launcher (concurrently)
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+ & npm
- **Android Studio** (for the Android app)
- **Firebase project** (optional — app works with local fallback)

### 1. Clone the Repository

```bash
git clone https://github.com/Rupendra18/AI-UV-VIS-Spectrum-Analyzer.git
cd AI-UV-VIS-Spectrum-Analyzer
```

### 2. Backend (Flask API)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # Edit with your Firebase config (optional)
python app.py                 # Starts on http://localhost:5000
```

### 3. Web App (React + Vite)

```bash
cd web_app
npm install
npm run dev                   # Starts on http://localhost:5173
```

### 4. One-Command Dev (Backend + Web)

```bash
# From the project root
npm install
npm run dev
```

### 5. Android App

1. Open `android_app/` in **Android Studio**
2. Sync Gradle
3. Click **Run ▶** on an emulator or device

### 6. Train the ML Model (Optional)

```bash
cd backend
python train_model.py         # Generates model.pkl & scaler.pkl
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.10+, Flask 3.0, scikit-learn, pandas, ReportLab, Plotly, PyJWT |
| **Web Frontend** | React 18, Vite 5, Material UI 5, Framer Motion, react-plotly.js, Recharts |
| **Android** | Kotlin, MVVM, Retrofit, Coroutines, Biometric API, Material Design |
| **Database** | Firebase Firestore (cloud) / Local JSON (fallback) |
| **Auth** | Firebase Auth / Local bcrypt with JWT tokens |
| **Storage** | Firebase Cloud Storage / Local filesystem |
| **Testing** | Appium, Selenium, openpyxl (Excel reports), Custom load test framework |
| **Deployment** | Docker, Render, Vercel |

---

## 🧪 Testing

### Mobile Tests (Appium) — 300+ Test Cases

```bash
cd tests/appium
python run_tests.py
# Report: tests/appium/reports/Appium_Test_Report_300_TestCases.xlsx
```

### Web Tests (Selenium) — 300+ Test Cases

```bash
cd tests/selenium
python run_tests.py
# Report: tests/selenium/reports/Selenium_Test_Report_300_TestCases.xlsx
```

### Load Testing

```bash
cd tests/load
python main.py
# Reports generated in tests/load/reports/
```

### Backend Unit Tests

```bash
cd backend
python -m pytest tests/
```

### DAST Security Testing

```bash
cd automated_test
python runner.py
```

See individual test suite READMEs for detailed documentation:
- [Appium Test Suite](tests/appium/README.md)
- [Selenium Test Suite](tests/selenium/README.md)
- [Load Testing](tests/load/README.md)

---

## 🚢 Deployment

| Platform | Config File | Guide |
|----------|------------|-------|
| **Docker** | [`deployment/Dockerfile`](deployment/Dockerfile) | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) |
| **Render** | [`deployment/render.yaml`](deployment/render.yaml) | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) |
| **Vercel** | [`deployment/vercel.json`](deployment/vercel.json) | [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) |

---

## 📚 Documentation

| Document | Description |
|----------|------------|
| 📖 [REST API Reference](docs/API.md) | Complete API endpoint documentation |
| 🏗️ [System Architecture](docs/ARCHITECTURE.md) | High-level architecture & design decisions |
| ⚙️ [Installation Guide](docs/INSTALL.md) | Step-by-step setup instructions |
| 🚀 [Deployment Guide](docs/DEPLOYMENT.md) | Docker, Render & Vercel deployment |
| 🔧 [Backend README](backend/README.md) | Backend-specific documentation |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Rupendra T**
- GitHub: [@Rupendra18](https://github.com/Rupendra18)

---

<p align="center">
  Made with ❤️ for scientific research and chemical analysis
</p>
