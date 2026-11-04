import os
import json
import uuid
import io
import math
import pandas as pd
import plotly
import plotly.graph_objects as go
from datetime import datetime
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, make_response, g, jsonify)
from werkzeug.utils import secure_filename
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Import Modular Utilities & Feature Modules ───────────────────────────────
from utils.firebase import (
    FIREBASE_CONFIGURED, db, bucket, firebase_admin_app, firebase_auth,
    upload_to_storage, upload_bytes_to_storage
)
from utils.helpers import (
    classify_status, calculate_confidence_score, get_interpretation, get_conclusion
)
from utils.validation import allowed_file, validate_and_parse_csv
from utils.graph import build_figure
from utils.pdf import generate_pdf_report
from prediction import analyze_spectrum_df
from upload import process_file_upload
from reports import get_pdf_response, get_csv_summary_bytes
from history import filter_and_sort_history
from settings import DEFAULT_SETTINGS, sanitize_settings
from api.routes import init_api

# ── Flask App Initialization ──────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'uv-vis-spectrum-secret-key-2024')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max upload
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ── CORS (allows React, Vite, and Android mobile apps to call the API) ──────
try:
    from flask_cors import CORS
    CORS(app, resources={r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "Authorization", "X-User-ID"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }})
except ImportError:
    pass  # flask-cors not installed — API still works for same-origin requests

# Local data fallback paths
import threading

DATA_DIR = os.path.join(app.root_path, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
ANALYSES_FILE = os.path.join(DATA_DIR, 'analyses.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# ── Thread-Safe In-Memory Cache Store ──────────────────────────────────────────
_data_lock = threading.RLock()
_cache_store = {
    'analyses': None,
    'analyses_mtime': 0,
    'settings': None,
    'settings_mtime': 0,
    'users': None,
    'users_mtime': 0,
    'stats': {},  # uid -> dict
}


def _get_cached_json(path, cache_key, default):
    """Retrieve JSON with in-memory caching and mtime validation."""
    with _data_lock:
        if os.path.exists(path):
            try:
                mtime = os.path.getmtime(path)
                if _cache_store[cache_key] is not None and _cache_store[f'{cache_key}_mtime'] == mtime:
                    return _cache_store[cache_key]
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                _cache_store[cache_key] = data
                _cache_store[f'{cache_key}_mtime'] = mtime
                return data
            except Exception:
                if _cache_store[cache_key] is not None:
                    return _cache_store[cache_key]
        return default


def _set_cached_json(path, cache_key, data):
    """Persist JSON atomically and update in-memory cache."""
    with _data_lock:
        _cache_store[cache_key] = data
        _cache_store['stats'].clear()
        try:
            temp_path = f"{path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, separators=(',', ':'))
            os.replace(temp_path, path)
            _cache_store[f'{cache_key}_mtime'] = os.path.getmtime(path)
        except Exception:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, separators=(',', ':'))
                _cache_store[f'{cache_key}_mtime'] = os.path.getmtime(path)
            except Exception:
                pass


def _load_json(path, default=None):
    """Safely read JSON files, returning default if file does not exist or fails to parse."""
    if default is None:
        default = []
    cache_key = None
    if path == USERS_FILE:
        cache_key = 'users'
    elif path == SETTINGS_FILE:
        cache_key = 'settings'
    elif path == ANALYSES_FILE:
        cache_key = 'analyses'

    if cache_key:
        return _get_cached_json(path, cache_key, default)

    with _data_lock:
        if not os.path.exists(path):
            return default
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default


def _save_json(path, data):
    """Safely save JSON data to file with atomic write and cache synchronization."""
    cache_key = None
    if path == USERS_FILE:
        cache_key = 'users'
    elif path == SETTINGS_FILE:
        cache_key = 'settings'
    elif path == ANALYSES_FILE:
        cache_key = 'analyses'

    if cache_key:
        _set_cached_json(path, cache_key, data)
        return

    with _data_lock:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            temp_path = f"{path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, path)
        except Exception:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass


# ── Helpers: Database & Storage Data Layer ───────────────────────────────────

def get_user_doc(uid):
    """Get user record from Firestore or fast in-memory cache."""
    if FIREBASE_CONFIGURED and db:
        try:
            doc = db.collection('Users').document(uid).get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            pass
    users = _get_cached_json(USERS_FILE, 'users', [])
    u = next((u for u in users if u.get('id') == uid), None)
    return dict(u) if u else None


def save_user_doc(uid, data):
    if FIREBASE_CONFIGURED and db:
        try:
            db.collection('Users').document(uid).set(data, merge=True)
            return
        except Exception:
            pass
    users = list(_get_cached_json(USERS_FILE, 'users', []))
    users = [u for u in users if u.get('id') != uid]
    users.append({'id': uid, **data})
    _set_cached_json(USERS_FILE, 'users', users)


def load_settings(uid=None):
    settings = dict(DEFAULT_SETTINGS)
    if uid is None:
        return settings
    if FIREBASE_CONFIGURED and db:
        try:
            doc = db.collection('Settings').document(uid).get()
            if doc.exists:
                settings.update(doc.to_dict())
                return settings
        except Exception:
            pass
    all_settings = _get_cached_json(SETTINGS_FILE, 'settings', {})
    if isinstance(all_settings, dict):
        if uid in all_settings:
            settings.update(all_settings[uid])
        elif 'org_name' in all_settings:
            settings.update(all_settings)
    return settings


def save_settings(uid, settings):
    if FIREBASE_CONFIGURED and db:
        try:
            db.collection('Settings').document(uid).set(settings, merge=True)
            return
        except Exception:
            pass
    all_settings = dict(_get_cached_json(SETTINGS_FILE, 'settings', {}))
    if isinstance(all_settings, dict) and 'org_name' in all_settings:
        all_settings = {}
    all_settings[uid] = settings
    _set_cached_json(SETTINGS_FILE, 'settings', all_settings)


def load_analyses(uid=None):
    """Retrieve spectrum analyses in reverse chronological order from memory cache."""
    if FIREBASE_CONFIGURED and db:
        try:
            from firebase_admin import firestore
            query = db.collection('Analyses')
            if uid:
                query = query.where('user_id', '==', uid)
            docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
            return [{'id': d.id, **d.to_dict()} for d in docs]
        except Exception:
            pass
    all_analyses = _get_cached_json(ANALYSES_FILE, 'analyses', [])
    if uid:
        filtered = [a for a in all_analyses if a.get('user_id') == uid or 'user_id' not in a]
    else:
        filtered = all_analyses
    # Return reversed list (latest first)
    return list(reversed(filtered))


def save_analysis(uid, entry):
    """Save a new analysis entry. Returns the doc ID."""
    entry['user_id'] = uid
    if FIREBASE_CONFIGURED and db:
        try:
            doc_ref = db.collection('Analyses').document()
            doc_ref.set(entry)
            return doc_ref.id
        except Exception:
            pass
    all_analyses = list(_get_cached_json(ANALYSES_FILE, 'analyses', []))
    all_analyses.append(entry)
    _set_cached_json(ANALYSES_FILE, 'analyses', all_analyses)
    return entry['id']


def delete_analysis(uid, analysis_id):
    if FIREBASE_CONFIGURED and db:
        try:
            doc = db.collection('Analyses').document(analysis_id).get()
            if doc.exists and doc.to_dict().get('user_id') == uid:
                doc.reference.delete()
                return True
        except Exception:
            pass
    all_analyses = list(_get_cached_json(ANALYSES_FILE, 'analyses', []))
    entry = next((a for a in all_analyses if a.get('id') == analysis_id), None)
    if entry and (entry.get('user_id') == uid or 'user_id' not in entry):
        all_analyses = [a for a in all_analyses if a.get('id') != analysis_id]
        _set_cached_json(ANALYSES_FILE, 'analyses', all_analyses)
        return True
    return False


def get_dashboard_stats(uid=None):
    """Calculate or retrieve cached dashboard KPIs."""
    with _data_lock:
        if uid in _cache_store['stats']:
            return _cache_store['stats'][uid]

        analyses = load_analyses(uid)
        total = len(analyses)
        safe = sum(1 for a in analyses if a.get('status') == 'SAFE')
        moderate = sum(1 for a in analyses if a.get('status') == 'MODERATE')
        high = sum(1 for a in analyses if a.get('status') == 'HIGH')
        avg_conc = (round(sum(a.get('predicted_concentration', 0)
                             for a in analyses) / total, 2) if total > 0 else 0)
        latest = analyses[0]['timestamp'] if analyses else None
        res = {
            'total': total,
            'safe': safe,
            'moderate': moderate,
            'high_risk': high,
            'avg_concentration': avg_conc,
            'latest_time': latest,
        }
        _cache_store['stats'][uid] = res
        return res


# ── Register REST API Blueprint ──────────────────────────────────────────────
api_blueprint = init_api(
    load_settings_fn=load_settings,
    save_settings_fn=save_settings,
    load_analyses_fn=load_analyses,
    save_analysis_fn=save_analysis,
    get_user_doc_fn=get_user_doc,
    save_user_doc_fn=save_user_doc,
    is_firebase_configured_fn=lambda: FIREBASE_CONFIGURED,
    firebase_auth_module=firebase_auth,
    get_dashboard_stats_fn=get_dashboard_stats,
    get_cached_users_fn=lambda: _get_cached_json(USERS_FILE, 'users', []),
    save_users_fn=lambda users: _set_cached_json(USERS_FILE, 'users', users),
)
app.register_blueprint(api_blueprint)


# ── Auth Middleware ───────────────────────────────────────────────────────────

@app.before_request
def load_logged_in_user():
    uid = session.get('user_id')
    if uid is None:
        g.user = None
    else:
        g.user = get_user_doc(uid)
        if g.user:
            g.user['id'] = uid

    allowed_routes = {
        'splash', 'login', 'register', 'forgot_password', 'firebase_setup',
        'api_login', 'api_register', 'static', 'api.api_upload', 'api.api_predict',
        'api.api_history', 'api.api_reports', 'api.api_settings'
    }
    if request.endpoint and request.endpoint not in allowed_routes and not request.endpoint.startswith('api.'):
        if g.user is None:
            return redirect(url_for('login'))


# ── Splash & Auth Routes ───────────────────────────────────────────────────────

@app.route('/splash')
def splash():
    if g.user:
        return redirect(url_for('dashboard'))
    return render_template('splash.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/login/', methods=['GET', 'POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return ('', 204)
    if g.user:
        return redirect(url_for('dashboard'))
    if request.method == 'GET' and not session.get('splash_shown') and request.args.get('nosplash') != '1':
        session['splash_shown'] = True
        return render_template('splash.html')

    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form.to_dict()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        if not FIREBASE_CONFIGURED:
            from werkzeug.security import check_password_hash
            users = _load_json(USERS_FILE, [])
            user = next((u for u in reversed(users) if u.get('email', '').lower() == email), None)
            if user and check_password_hash(user.get('password_hash', ''), password):
                session.clear()
                session['user_id'] = user['id']
                if request.is_json:
                    return jsonify({'status': 'ok', 'uid': user['id']})
                return redirect(url_for('dashboard'))
            if request.is_json:
                return jsonify({'error': 'Invalid email or password'}), 401
            flash('Invalid email or password.', 'danger')
        else:
            if request.is_json:
                return jsonify({'error': 'Please use Firebase Authentication'}), 400
            flash('Please use the login form with Firebase Authentication.', 'danger')
    return render_template('login.html', firebase_configured=FIREBASE_CONFIGURED)


@app.route('/register', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/register/', methods=['GET', 'POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return ('', 204)
    if g.user:
        return redirect(url_for('dashboard'))
    if request.method == 'POST' and not FIREBASE_CONFIGURED:
        from werkzeug.security import generate_password_hash
        name = request.form.get('name', '').strip()
        org = request.form.get('org_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not all([name, org, email, password]):
            flash('All fields are required.', 'danger')
            return render_template('register.html', firebase_configured=FIREBASE_CONFIGURED)
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', firebase_configured=FIREBASE_CONFIGURED)
        users = _load_json(USERS_FILE, [])
        if any(u.get('email', '').lower() == email for u in users):
            flash('Email already registered.', 'danger')
            return render_template('register.html', firebase_configured=FIREBASE_CONFIGURED)
        uid = str(uuid.uuid4())
        user_data = {
            'id': uid, 'name': name, 'org_name': org,
            'email': email, 'role': 'User',
            'password_hash': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }
        users.append(user_data)
        _save_json(USERS_FILE, users)
        save_settings(uid, {**DEFAULT_SETTINGS, 'org_name': org, 'scientist_name': name})
        session.clear()
        session['user_id'] = uid
        return redirect(url_for('dashboard'))
    return render_template('register.html', firebase_configured=FIREBASE_CONFIGURED)


@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')


@app.route('/firebase-setup')
def firebase_setup():
    return render_template('firebase_setup.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ── Firebase Auth API (called from JS) ───────────────────────────────────────

@app.route('/api/login', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/api/login/', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/api/auth/login', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/api/auth/login/', methods=['GET', 'POST', 'OPTIONS'])
def api_login():
    """Authenticate via Firebase ID token or email/password fallback."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    if request.method == 'GET':
        return jsonify({
            'status': 'ok',
            'endpoint': 'login',
            'methods': ['POST', 'GET', 'OPTIONS'],
            'message': 'Login endpoint is active. Submit POST with email and password or idToken.'
        }), 200

    data = request.get_json(silent=True) or request.form.to_dict()
    id_token = data.get('idToken', '')
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # 1. Firebase auth flow
    if id_token and FIREBASE_CONFIGURED and firebase_auth:
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            uid = decoded['uid']
            email = decoded.get('email', '')
            name = decoded.get('name', email.split('@')[0])
            existing = get_user_doc(uid)
            if not existing:
                user_data = {
                    'name': name, 'email': email, 'role': 'User',
                    'created_at': datetime.now().isoformat()
                }
                save_user_doc(uid, user_data)
                save_settings(uid, {**DEFAULT_SETTINGS, 'scientist_name': name})
            session.clear()
            session['user_id'] = uid
            return jsonify({'status': 'ok', 'uid': uid})
        except Exception as e:
            return jsonify({'error': str(e)}), 401

    # 2. Local email/password flow
    if email and password:
        from werkzeug.security import check_password_hash
        users = _cache_store.get('users') or _load_json(USERS_FILE, [])
        user = next((u for u in reversed(users) if u.get('email', '').lower() == email), None)
        if not user and os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    disk_users = json.load(f)
                user = next((u for u in reversed(disk_users) if u.get('email', '').lower() == email), None)
            except Exception:
                pass
        if user and check_password_hash(user.get('password_hash', ''), password):
            session.clear()
            session['user_id'] = user['id']
            return jsonify({'status': 'ok', 'uid': user['id'], 'user': {'name': user.get('name'), 'email': user.get('email'), 'role': user.get('role', 'User')}})
        return jsonify({'error': 'Invalid email or password'}), 401

    return jsonify({'error': 'Email and password or valid idToken required'}), 400


@app.route('/api/register', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/api/register/', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/api/auth/register', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/api/auth/register/', methods=['GET', 'POST', 'OPTIONS'])
def api_register():
    """Register a new user via Firebase Auth token or local credentials."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    if request.method == 'GET':
        return jsonify({
            'status': 'ok',
            'endpoint': 'register',
            'methods': ['POST', 'GET', 'OPTIONS'],
            'message': 'Registration endpoint is active. Submit POST with name, email, and password.'
        }), 200

    data = request.get_json(silent=True) or request.form.to_dict()
    id_token = data.get('idToken', '')
    name = data.get('name', '').strip()
    org_name = data.get('org_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # 1. Firebase auth flow
    if id_token and FIREBASE_CONFIGURED and firebase_auth:
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            uid = decoded['uid']
            email = decoded.get('email', '')
            user_data = {
                'name': name or email.split('@')[0],
                'email': email,
                'org_name': org_name,
                'role': 'User',
                'created_at': datetime.now().isoformat()
            }
            save_user_doc(uid, user_data)
            save_settings(uid, {**DEFAULT_SETTINGS,
                                 'org_name': org_name,
                                 'scientist_name': name})
            session.clear()
            session['user_id'] = uid
            return jsonify({'status': 'ok', 'uid': uid})
        except Exception as e:
            return jsonify({'error': str(e)}), 401

    # 2. Local registration flow
    if email and password and name:
        from werkzeug.security import generate_password_hash
        users = list(_get_cached_json(USERS_FILE, 'users', []))
        if any(u.get('email', '').lower() == email for u in users):
            return jsonify({'error': 'Email already registered'}), 409
        uid = str(uuid.uuid4())
        user_data = {
            'id': uid,
            'name': name,
            'email': email,
            'org_name': org_name,
            'role': 'User',
            'password_hash': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }
        users.append(user_data)
        _set_cached_json(USERS_FILE, 'users', users)
        save_settings(uid, {**DEFAULT_SETTINGS, 'org_name': org_name, 'scientist_name': name})
        session.clear()
        session['user_id'] = uid
        return jsonify({'status': 'ok', 'uid': uid}), 201

    return jsonify({'error': 'Name, email and password required'}), 400


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    uid = g.user['id']
    graphJSON = None
    featureImportanceJSON = None
    peak_wavelength = peak_absorbance = predicted_concentration = None
    status = analysis_id = confidence_score = interpretation = None
    algorithm_name = None
    model_accuracy = rmse = mae = None

    filename = session.get('uploaded_filename')
    settings = load_settings(uid)
    stats = get_dashboard_stats(uid)
    analyses = load_analyses(uid)
    recent_activity = analyses[:5]

    if filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            try:
                df, err = validate_and_parse_csv(filepath)
                if err:
                    flash(err, 'danger')
                    session.pop('uploaded_filename', None)
                    return redirect(url_for('dashboard'))

                res = analyze_spectrum_df(
                    df,
                    safe_limit=settings.get('safe_limit', 5.0)
                )

                peak_wavelength = res['peak_wavelength']
                peak_absorbance = res['peak_absorbance']
                predicted_concentration = res['predicted_concentration']
                status = res['status']
                confidence_score = res['confidence_score']
                interpretation = res['interpretation']
                algorithm_name = res.get('algorithm', 'Random Forest Regressor')
                model_accuracy = res.get('accuracy_percentage', None)
                rmse = res.get('rmse', None)
                mae = res.get('mae', None)
                feature_importances = res.get('feature_importances', {})

                # Build spectrum Plotly graph
                fig = build_figure(df, filename, peak_wavelength, peak_absorbance)
                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

                # Build Feature Importance Plotly Bar Chart
                if feature_importances:
                    feat_names = [k.replace('_', ' ') for k in feature_importances.keys()]
                    feat_vals = [round(v * 100, 1) for v in feature_importances.values()]
                    colors_list = ['#3b82f6', '#8b5cf6', '#06b6d4']
                    fi_fig = go.Figure(go.Bar(
                        x=feat_vals,
                        y=feat_names,
                        orientation='h',
                        marker=dict(
                            color=colors_list[:len(feat_names)],
                            line=dict(color='rgba(255,255,255,0.1)', width=1)
                        ),
                        text=[f'{v}%' for v in feat_vals],
                        textposition='outside',
                        textfont=dict(color='#f8fafc', size=12)
                    ))
                    fi_fig.update_layout(
                        template='plotly_dark',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#94a3b8', family='Inter, sans-serif'),
                        margin=dict(l=140, r=40, t=30, b=40),
                        xaxis=dict(title=dict(text='Importance (%)'), range=[0, 110], gridcolor='rgba(51,65,85,0.4)'),
                        yaxis=dict(gridcolor='rgba(0,0,0,0)'),
                        height=220,
                        showlegend=False,
                    )
                    featureImportanceJSON = json.dumps(fi_fig, cls=plotly.utils.PlotlyJSONEncoder)

                for entry in analyses:
                    if entry.get('filename') == filename:
                        analysis_id = entry.get('id')
                        break

            except Exception as e:
                app.logger.error(f"Dashboard calculation error: {e}")
                flash(f'Error processing file: {e}', 'danger')
                session.pop('uploaded_filename', None)
        else:
            session.pop('uploaded_filename', None)

    return render_template(
        'dashboard.html',
        active_page='dashboard',
        graphJSON=graphJSON,
        featureImportanceJSON=featureImportanceJSON,
        peak_wavelength=peak_wavelength,
        peak_absorbance=peak_absorbance,
        predicted_concentration=predicted_concentration,
        status=status,
        confidence_score=confidence_score,
        interpretation=interpretation,
        algorithm_name=algorithm_name,
        model_accuracy=model_accuracy,
        rmse=rmse,
        mae=mae,
        stats=stats,
        recent_activity=recent_activity,
        settings=settings,
        analysis_id=analysis_id,
        firebase_configured=FIREBASE_CONFIGURED,
    )


# ── Upload ────────────────────────────────────────────────────────────────────

@app.route('/upload', methods=['POST'])
def upload_file():
    uid = g.user['id']

    if 'file' not in request.files:
        flash('No file part in request.', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['file']
    settings = load_settings(uid)

    success, result, filename = process_file_upload(
        file_obj=file,
        upload_folder=app.config['UPLOAD_FOLDER'],
        uid=uid,
        settings=settings,
        save_analysis_fn=save_analysis
    )

    if success:
        session['uploaded_filename'] = filename
        flash(f'✓ "{filename}" analysed successfully!', 'success')
    else:
        flash(result, 'danger')

    return redirect(url_for('dashboard'))


# ── Reports ───────────────────────────────────────────────────────────────────

@app.route('/reports')
def reports():
    uid = g.user['id']
    all_reports = load_analyses(uid)
    return render_template('reports.html', active_page='reports',
                           reports=all_reports,
                           firebase_configured=FIREBASE_CONFIGURED)


@app.route('/report/delete/<report_id>', methods=['POST'])
def delete_report(report_id):
    uid = g.user['id']
    success = delete_analysis(uid, report_id)
    if success:
        flash('Report deleted successfully.', 'success')
    else:
        flash('Report not found or access denied.', 'danger')
    return redirect(url_for('reports'))


@app.route('/report/download/<report_id>')
def download_report(report_id):
    uid = g.user['id']
    analyses = load_analyses(uid)
    entry = next((a for a in analyses if a.get('id') == report_id), None)
    if not entry:
        flash('Report not found.', 'danger')
        return redirect(url_for('reports'))

    settings = load_settings(uid)
    user_info = g.user or {}

    pdf_bytes, filename, err = get_pdf_response(entry, settings, user_info)
    if err:
        flash(err, 'danger')
        return redirect(url_for('reports'))

    if FIREBASE_CONFIGURED and bucket and not entry.get('pdf_url'):
        pdf_url = upload_bytes_to_storage(
            pdf_bytes, f'reports/{uid}/report_{report_id[:8]}.pdf', 'application/pdf')
        if pdf_url and db:
            try:
                db.collection('Analyses').document(report_id).update({'pdf_url': pdf_url})
            except Exception:
                pass

    resp = make_response(pdf_bytes)
    resp.headers['Content-Type'] = 'application/pdf'
    resp.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return resp


@app.route('/report/view/<report_id>')
def view_report(report_id):
    uid = g.user['id']
    analyses = load_analyses(uid)
    entry = next((a for a in analyses if a.get('id') == report_id), None)
    if not entry:
        flash('Report not found.', 'danger')
        return redirect(url_for('reports'))

    settings = load_settings(uid)
    user_info = g.user or {}

    pdf_bytes, filename, err = get_pdf_response(entry, settings, user_info, is_inline=True)
    if err:
        flash(err, 'danger')
        return redirect(url_for('reports'))

    resp = make_response(pdf_bytes)
    resp.headers['Content-Type'] = 'application/pdf'
    resp.headers['Content-Disposition'] = f'inline; filename={filename}'
    return resp


@app.route('/download/csv/<report_id>')
def download_csv(report_id):
    uid = g.user['id']
    analyses = load_analyses(uid)
    entry = next((a for a in analyses if a.get('id') == report_id), None)
    if not entry:
        flash('Report not found.', 'danger')
        return redirect(url_for('reports'))

    csv_bytes = get_csv_summary_bytes(entry)
    resp = make_response(csv_bytes)
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = f'attachment; filename=analysis_{report_id[:8]}.csv'
    return resp


# ── History ───────────────────────────────────────────────────────────────────

@app.route('/history')
def history():
    uid = g.user['id']
    analyses = load_analyses(uid)

    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status_filter', '').strip()
    sort_by = request.args.get('sort_by', 'date_desc')

    filtered_analyses = filter_and_sort_history(
        analyses, search=search, status_filter=status_filter, sort_by=sort_by
    )

    return render_template('history.html', active_page='history',
                           history=filtered_analyses,
                           search=search,
                           status_filter=status_filter,
                           sort_by=sort_by)


@app.route('/history/delete/<entry_id>', methods=['POST'])
def delete_history(entry_id):
    uid = g.user['id']
    success = delete_analysis(uid, entry_id)
    if success:
        flash('Entry deleted.', 'success')
    else:
        flash('Access denied or entry not found.', 'danger')
    return redirect(url_for('history'))


# ── Settings ──────────────────────────────────────────────────────────────────

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    uid = g.user['id']
    current = load_settings(uid)
    if request.method == 'POST':
        updated = sanitize_settings(request.form, current)
        save_settings(uid, updated)
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html', active_page='settings', settings=current)


if __name__ == '__main__':
    # Detect local Wi-Fi / LAN IPv4 address for mobile access
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = socket.gethostbyname(socket.gethostname())

    print("=" * 68)
    print("  AI UV-VIS SPECTRUM ANALYZER — BACKEND SERVER")
    print("=" * 68)
    print(f"  * Host Binding       : 0.0.0.0:5000 (Listening on all interfaces)")
    print(f"  * Local PC URL       : http://127.0.0.1:5000")
    print(f"  * Mobile Phone URL   : http://{local_ip}:5000/")
    print(f"  * Mobile API Base    : http://{local_ip}:5000/api/")
    print("=" * 68)
    print("  Make sure your mobile phone is connected to the same Wi-Fi.")
    print("=" * 68)

    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000, threads=32, connection_limit=500, channel_timeout=30)
    except Exception as e:
        print(f"  * Starting standard multi-threaded WSGI server (fallback: {e})...")
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
