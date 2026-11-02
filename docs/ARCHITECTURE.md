# System Architecture — AI UV-Vis Spectrum Analyzer

```
                           +------------------------+
                           |  Firebase Project      |
                           |  (Auth, Firestore,     |
                           |   Storage, Hosting)    |
                           +-----------+------------+
                                       ^
                                       |
    +-----------------------+          |          +-----------------------+
    |   React Web App       |          |          |  Kotlin Android App   |
    |   (web_app/)          |----------+----------|  (android_app/)       |
    |   Port 5173           |                     |  Retrofit + Coroutines|
    +-----------+-----------+                     +-----------+-----------+
                |                                             |
                +----------------------+----------------------+
                                       | JSON REST API
                                       v
                           +------------------------+
                           |   Flask Backend API    |
                           |   (backend/)           |
                           |   Port 5000            |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           |   AI Prediction Engine |
                           |   Random Forest Model  |
                           |   (backend/predictor.py|
                           |    models/model.pkl)   |
                           +------------------------+
```

## System Components

1. **Flask Backend (`backend/`)**: Entry point `app.py`. Hosts all REST APIs under `/api/*`, Jinja2 templates for existing web access, and connects to the AI engine.
2. **AI Prediction Engine (`backend/ai/`, `backend/predictor.py`)**: Uses scikit-learn Random Forest Regressor (`models/model.pkl`, `scaler.pkl`) to predict analyte concentration from peak wavelength, absorbance, and baseline signal.
3. **React Web App (`web_app/`)**: Created with Vite + React 18, Material UI v5, Framer Motion, and Plotly.js. Features dark/light themes, drag-and-drop CSV upload, interactive charts, and glassmorphic UI.
4. **Android Native App (`android_app/`)**: Native Kotlin app following MVVM architecture, Retrofit for REST APIs, Biometric prompt authentication, and MPAndroidChart for spectral curves.
5. **Firebase Platform (`firebase/`)**: Single shared Firebase project handling user authentication (Email/Password), Firestore document database, and Cloud Storage for CSV uploads and PDF reports.
