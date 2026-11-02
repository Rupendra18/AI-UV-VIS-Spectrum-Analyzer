# REST API Documentation — AI UV-Vis Spectrum Analyzer

All endpoints use JSON requests and responses under the `/api` base path. Authentication can be performed via standard session cookies or `Authorization: Bearer <jwt_token>` header.

---

## 1. Authentication Endpoints

### `POST /api/auth/register`
Registers a new scientist user.
- **Request Body:**
  ```json
  {
    "name": "Dr. Sarah Connor",
    "org_name": "Apex Research Labs",
    "email": "sarah@apex.org",
    "password": "SecretPassword123"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "status": "ok",
    "uid": "user-uuid-12345",
    "token": "eyJhbGciOiJIUzI1NiIsIn...",
    "user": { "name": "Dr. Sarah Connor", "email": "sarah@apex.org", "role": "User" }
  }
  ```

---

### `POST /api/auth/login`
Authenticates a user via email/password or Firebase ID Token.
- **Request Body:**
  ```json
  {
    "email": "sarah@apex.org",
    "password": "SecretPassword123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "status": "ok",
    "uid": "user-uuid-12345",
    "token": "eyJhbGciOiJIUzI1NiIsIn...",
    "user": { "name": "Dr. Sarah Connor", "role": "User" }
  }
  ```

---

### `GET /api/auth/profile`
Retrieves profile details for the authenticated user.

---

## 2. Spectrum Analysis & Prediction Endpoints

### `POST /api/upload`
Uploads a CSV spectral file (`multipart/form-data`) and runs Machine Learning prediction.
- **Form Part:** `file` (CSV file with `Wavelength` & `Absorbance` columns)
- **Response (200 OK):**
  ```json
  {
    "status": "success",
    "analysis": {
      "id": "analysis-uuid-99",
      "timestamp": "2026-08-19 14:30:00",
      "filename": "sample_spectrum.csv",
      "peak_wavelength": 320.0,
      "peak_absorbance": 1.25,
      "predicted_concentration": 15.3,
      "status": "HIGH",
      "confidence_score": 92.5,
      "algorithm": "Random Forest Regressor",
      "accuracy_percentage": 99.74,
      "rmse": 0.48,
      "mae": 0.38,
      "interpretation": "The UV-Vis absorption spectrum displays a peak at λmax = 320.0 nm...",
      "conclusion": "ALERT: The sample concentration of 15.3 ppm significantly exceeds..."
    }
  }
  ```

---

### `POST /api/predict`
Predicts analyte concentration from a JSON array of spectral data points without uploading a file.
- **Request Body:**
  ```json
  {
    "points": [
      { "Wavelength": 200, "Absorbance": 0.1 },
      { "Wavelength": 320, "Absorbance": 1.25 },
      { "Wavelength": 400, "Absorbance": 0.05 }
    ]
  }
  ```

---

## 3. History & Reports Endpoints

### `GET /api/history`
Query parameters: `search`, `status` (SAFE/MODERATE/HIGH), `sort_by` (`date_desc`, `date_asc`, `conc_desc`), `page`, `per_page`.

### `DELETE /api/history/<id>`
Deletes a specific analysis record.

### `GET /api/reports/<id>/pdf`
Returns binary PDF report stream for download.

### `GET /api/reports/<id>/csv`
Returns binary CSV summary download.
