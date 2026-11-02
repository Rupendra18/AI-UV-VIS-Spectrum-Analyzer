# Installation Guide — AI UV-Vis Spectrum Analyzer

## Prerequisites

- **Python**: 3.10+
- **Node.js**: 18+ (for React Web App)
- **Android Studio**: Giraffe or later (for Kotlin Android App)

---

## 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

The Flask server will start at `http://localhost:5000`.

---

## 2. React Web App Setup

```bash
cd web_app
npm install
npm run dev
```

The Vite dev server will start at `http://localhost:5173`. Requests to `/api/*` will automatically proxy to `http://localhost:5000`.

---

## 3. Kotlin Android App Setup

1. Open Android Studio.
2. Select **Open an Existing Project** and choose the `android_app/` folder.
3. Sync Gradle dependencies.
4. Run on an Android Emulator or physical device (Android 8.0+ / API 26+).
