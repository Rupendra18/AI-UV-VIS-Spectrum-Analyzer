# Deployment Guide — AI UV-Vis Spectrum Analyzer

## 1. Backend Deployment (Render.com)

1. Connect your repository to Render.
2. Select **Web Service**.
3. Set Environment to **Python 3**.
4. Build Command: `pip install -r backend/requirements.txt`
5. Start Command: `gunicorn --bind 0.0.0.0:$PORT backend.app:app`
6. Add Environment Variables: `FLASK_SECRET_KEY`, `FIREBASE_STORAGE_BUCKET`.

---

## 2. React Web App Deployment (Vercel)

1. Import repository on Vercel.
2. Set Root Directory to `web_app`.
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Add Environment Variable: `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_API_KEY`.

---

## 3. Android Signed APK Generation

1. Open `android_app/` in Android Studio.
2. Navigate to **Build > Generate Signed Bundle / APK...**
3. Select **APK** and click Next.
4. Choose your Key Store path, alias, and passwords.
5. Select **release** build variant and click Create.
6. The signed `.apk` file will be generated in `android_app/app/release/`.
