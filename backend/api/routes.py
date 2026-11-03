"""
Backend REST API — AI UV-Vis Spectrum Analyzer
All endpoints communicate via JSON.
Supports session auth (Flask UI) and Bearer JWT auth (React/Android).
"""
import os
import uuid
import datetime as dt

import pandas as pd
from flask import Blueprint, request, jsonify, session, g

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ---------------------------------------------------------------------------
# JWT Helpers (optional — only when PyJWT is available & SECRET_KEY is set)
# ---------------------------------------------------------------------------
import functools

@functools.lru_cache(maxsize=2048)
def _decode_bearer(token: str):
    """Decode JWT Bearer token with LRU caching; returns payload dict or None."""
    try:
        import jwt
        secret = os.environ.get('JWT_SECRET', os.environ.get('FLASK_SECRET_KEY', 'uv-vis-spectrum-analyzer-jwt-secret-key-32bytes'))
        return jwt.decode(token, secret, algorithms=['HS256'])
    except Exception:
        return None


def _make_token(uid: str, email: str) -> str:
    """Issue a 30-day JWT for the given user."""
    import jwt
    secret = os.environ.get('JWT_SECRET', os.environ.get('FLASK_SECRET_KEY', 'uv-vis-spectrum-analyzer-jwt-secret-key-32bytes'))
    payload = {
        'uid': uid,
        'email': email,
        'exp': dt.datetime.utcnow() + dt.timedelta(days=30),
        'iat': dt.datetime.utcnow(),
    }
    return jwt.encode(payload, secret, algorithm='HS256')


def _get_uid() -> str | None:
    """
    Resolve user UID from (1) Flask session, (2) Bearer JWT, (3) X-User-ID header.
    """
    # 1. Session (web UI)
    uid = session.get('user_id')
    if uid:
        return uid

    # 2. Bearer JWT (React / Android)
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        payload = _decode_bearer(auth[7:])
        if payload and 'uid' in payload:
            return payload['uid']

    # 3. Explicit header (mobile debug)
    return request.headers.get('X-User-ID') or 'guest'


# ---------------------------------------------------------------------------
# Initialise blueprint with injected dependency functions
# ---------------------------------------------------------------------------

def init_api(load_settings_fn, save_settings_fn, load_analyses_fn, save_analysis_fn,
             get_user_doc_fn, save_user_doc_fn, is_firebase_configured_fn, firebase_auth_module,
             get_dashboard_stats_fn=None, get_cached_users_fn=None, save_users_fn=None):
    """Register all API routes with the Flask app's data-layer functions."""

    # ── Health Check ────────────────────────────────────────────────────────
    @api_bp.route('/health', methods=['GET'])
    def api_health():
        return jsonify({
            'status': 'ok',
            'message': 'UV-Vis Spectrum AI Backend is live and reachable',
            'timestamp': dt.datetime.now().isoformat()
        })

    # ── Auth ────────────────────────────────────────────────────────────────

    @api_bp.route('/auth/register', methods=['POST'])
    def api_register():
        data = request.get_json(silent=True) or request.form.to_dict()
        name = data.get('name', '').strip()
        org  = data.get('org_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not all([name, email, password]):
            return jsonify({'error': 'name, email and password are required'}), 400

        # Firebase path
        if is_firebase_configured_fn() and firebase_auth_module:
            try:
                fb_user = firebase_auth_module.create_user(email=email, password=password,
                                                           display_name=name)
                uid = fb_user.uid
                user_data = {'name': name, 'email': email, 'org_name': org,
                             'role': 'User', 'created_at': dt.datetime.now().isoformat()}
                save_user_doc_fn(uid, user_data)
                token = _make_token(uid, email)
                return jsonify({'status': 'ok', 'uid': uid, 'token': token, 'user': user_data})
            except Exception as e:
                return jsonify({'error': str(e)}), 400

        # Local fallback using cached users
        from werkzeug.security import generate_password_hash
        if get_cached_users_fn:
            users = list(get_cached_users_fn())
        else:
            import json, os as _os
            data_dir = _os.path.join(_os.path.dirname(__file__), '..', 'data')
            users_file = _os.path.join(data_dir, 'users.json')
            try:
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
            except Exception:
                users = []
        if any(u.get('email', '').lower() == email for u in users):
            return jsonify({'error': 'Email already registered'}), 409
        uid = str(uuid.uuid4())
        user_data = {'id': uid, 'name': name, 'email': email, 'org_name': org,
                     'role': 'User', 'password_hash': generate_password_hash(password),
                     'created_at': dt.datetime.now().isoformat()}
        users.append(user_data)
        if save_users_fn:
            save_users_fn(users)
        else:
            import json, os as _os
            data_dir = _os.path.join(_os.path.dirname(__file__), '..', 'data')
            users_file = _os.path.join(data_dir, 'users.json')
            _os.makedirs(data_dir, exist_ok=True)
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2)
        save_settings_fn(uid, {'org_name': org, 'scientist_name': name, 'safe_limit': 5.0})
        token = _make_token(uid, email)
        safe = {k: v for k, v in user_data.items() if k != 'password_hash'}
        return jsonify({'status': 'ok', 'uid': uid, 'token': token, 'user': safe}), 201

    @api_bp.route('/auth/login', methods=['POST'])
    def api_login():
        data = request.get_json(silent=True) or request.form.to_dict()
        id_token = data.get('idToken', '')
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # Firebase ID token path (React / Android pass Firebase idToken)
        if id_token and is_firebase_configured_fn() and firebase_auth_module:
            try:
                decoded = firebase_auth_module.verify_id_token(id_token)
                uid = decoded['uid']
                user_doc = get_user_doc_fn(uid)
                if not user_doc:
                    user_doc = {'name': decoded.get('name', email.split('@')[0]),
                                'email': decoded.get('email', email), 'role': 'User'}
                    save_user_doc_fn(uid, user_doc)
                token = _make_token(uid, email or decoded.get('email', ''))
                session['user_id'] = uid
                return jsonify({'status': 'ok', 'uid': uid, 'token': token, 'user': user_doc})
            except Exception as e:
                return jsonify({'error': str(e)}), 401

        # Local email+password path
        if not email or not password:
            return jsonify({'error': 'email and password required'}), 400
        from werkzeug.security import check_password_hash
        if get_cached_users_fn:
            users = get_cached_users_fn()
        else:
            import json, os as _os
            users_file = _os.path.join(_os.path.dirname(__file__), '..', 'data', 'users.json')
            try:
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
            except Exception:
                users = []
        user = next((u for u in users if u.get('email', '').lower() == email), None)
        if not user or not check_password_hash(user.get('password_hash', ''), password):
            return jsonify({'error': 'Invalid email or password'}), 401
        uid = user['id']
        session['user_id'] = uid
        token = _make_token(uid, email)
        safe = {k: v for k, v in user.items() if k != 'password_hash'}
        return jsonify({'status': 'ok', 'uid': uid, 'token': token, 'user': safe})

    @api_bp.route('/auth/logout', methods=['POST'])
    def api_logout():
        session.clear()
        return jsonify({'status': 'ok', 'message': 'Logged out'})

    @api_bp.route('/auth/forgot-password', methods=['POST'])
    def api_forgot_password():
        data = request.get_json(silent=True) or request.form.to_dict()
        email = data.get('email', '').strip().lower()
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        return jsonify({'status': 'ok', 'message': 'If this email is registered, password reset instructions have been sent.'})

    @api_bp.route('/auth/profile', methods=['GET', 'PUT'])
    def api_profile():
        uid = _get_uid()
        if uid == 'guest':
            return jsonify({'error': 'Authentication required'}), 401

        if request.method == 'GET':
            user = dict(get_user_doc_fn(uid) or {})
            user.pop('password_hash', None)
            return jsonify({'status': 'ok', 'user': user})

        # PUT — update profile
        data = request.get_json(silent=True) or request.form.to_dict()
        allowed = {'name', 'org_name', 'phone', 'bio', 'avatar_url'}
        update = {k: v for k, v in data.items() if k in allowed}
        save_user_doc_fn(uid, update)
        return jsonify({'status': 'ok', 'updated': update})

    # ── Dashboard ────────────────────────────────────────────────────────────

    @api_bp.route('/dashboard/stats', methods=['GET'])
    def api_dashboard_stats():
        uid = _get_uid()
        target_uid = uid if uid != 'guest' else None
        if get_dashboard_stats_fn:
            stats = get_dashboard_stats_fn(target_uid)
        else:
            analyses = load_analyses_fn(target_uid)
            total = len(analyses)
            safe = sum(1 for a in analyses if a.get('status') == 'SAFE')
            moderate = sum(1 for a in analyses if a.get('status') == 'MODERATE')
            high = sum(1 for a in analyses if a.get('status') == 'HIGH')
            avg_conc = round(
                sum(a.get('predicted_concentration', 0) for a in analyses) / total, 2
            ) if total > 0 else 0
            stats = {
                'total': total, 'safe': safe, 'moderate': moderate,
                'high_risk': high, 'avg_concentration': avg_conc,
                'latest_time': analyses[0]['timestamp'] if analyses else None,
            }
        return jsonify({'status': 'ok', 'stats': stats})

    # ── Upload & Predict ─────────────────────────────────────────────────────

    @api_bp.route('/upload', methods=['POST'])
    def api_upload():
        uid = _get_uid()

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        try:
            from utils.validation import validate_and_parse_csv
            from prediction import analyze_spectrum_df
            from utils.firebase import upload_to_storage

            df, err = validate_and_parse_csv(file)
            if err:
                return jsonify({'error': err}), 400

            settings = load_settings_fn(uid)
            analysis_res = analyze_spectrum_df(df, safe_limit=settings.get('safe_limit', 5.0))

            filename = file.filename
            entry = {
                'id': str(uuid.uuid4()),
                'timestamp': dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'filename': filename,
                'peak_wavelength': analysis_res['peak_wavelength'],
                'peak_absorbance': analysis_res['peak_absorbance'],
                'predicted_concentration': analysis_res['predicted_concentration'],
                'status': analysis_res['status'],
                'confidence_score': analysis_res['confidence_score'],
                'algorithm': analysis_res.get('algorithm', 'Random Forest Regressor'),
                'accuracy_percentage': analysis_res.get('accuracy_percentage', 0.0),
                'rmse': analysis_res.get('rmse', 0.0),
                'mae': analysis_res.get('mae', 0.0),
                'interpretation': analysis_res['interpretation'],
                'conclusion': analysis_res['conclusion'],
                'csv_url': '',
                'pdf_url': '',
            }

            doc_id = save_analysis_fn(uid, entry)
            entry['id'] = doc_id or entry['id']
            return jsonify({'status': 'success', 'analysis': entry})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api_bp.route('/predict', methods=['POST'])
    def api_predict():
        data = request.get_json(silent=True) or {}
        points = data.get('points', [])

        if not points or not isinstance(points, list):
            return jsonify({'error': 'Expected JSON body {"points":[{"Wavelength":…,"Absorbance":…}]}'}), 400
        try:
            from prediction import analyze_spectrum_df
            df = pd.DataFrame(points)
            if 'Wavelength' not in df.columns or 'Absorbance' not in df.columns:
                return jsonify({'error': 'Objects must contain Wavelength and Absorbance keys'}), 400

            uid = _get_uid()
            settings = load_settings_fn(uid)
            result = analyze_spectrum_df(df, safe_limit=settings.get('safe_limit', 5.0))
            return jsonify({'status': 'success', 'prediction': result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ── History ──────────────────────────────────────────────────────────────

    @api_bp.route('/history', methods=['GET'])
    def api_history():
        uid = _get_uid()
        analyses = load_analyses_fn(uid if uid != 'guest' else None)

        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        sort_by = request.args.get('sort_by', 'date_desc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        from history import filter_and_sort_history
        filtered = filter_and_sort_history(analyses, search=search,
                                           status_filter=status_filter, sort_by=sort_by)
        total = len(filtered)
        start = (page - 1) * per_page
        paginated = filtered[start:start + per_page]
        return jsonify({
            'status': 'success', 'history': paginated,
            'total': total, 'page': page, 'per_page': per_page,
        })

    @api_bp.route('/history/<analysis_id>', methods=['DELETE'])
    def api_delete_history(analysis_id):
        uid = _get_uid()
        if uid == 'guest':
            return jsonify({'error': 'Authentication required'}), 401
        # Import delete_analysis from app context
        try:
            import importlib, sys
            app_mod = sys.modules.get('__main__') or importlib.import_module('app')
            deleted = app_mod.delete_analysis(uid, analysis_id)
            if deleted:
                return jsonify({'status': 'success', 'deleted': analysis_id})
            return jsonify({'error': 'Analysis not found or permission denied'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ── Reports ──────────────────────────────────────────────────────────────

    @api_bp.route('/reports', methods=['GET'])
    def api_reports():
        uid = _get_uid()
        analyses = load_analyses_fn(uid if uid != 'guest' else None)
        reports_list = [
            {
                'id': a.get('id'),
                'filename': a.get('filename'),
                'timestamp': a.get('timestamp'),
                'status': a.get('status'),
                'predicted_concentration': a.get('predicted_concentration'),
                'algorithm': a.get('algorithm', 'Random Forest Regressor'),
                'confidence_score': a.get('confidence_score'),
                'pdf_url': a.get('pdf_url') or f"/report/download/{a.get('id')}",
                'csv_url': a.get('csv_url') or f"/report/csv/{a.get('id')}",
            }
            for a in analyses
        ]
        return jsonify({'status': 'success', 'reports': reports_list})

    @api_bp.route('/reports/<report_id>/pdf', methods=['GET'])
    def api_report_pdf(report_id):
        uid = _get_uid()
        analyses = load_analyses_fn(uid if uid != 'guest' else None)
        entry = next((a for a in analyses if a.get('id') == report_id), None)
        if not entry:
            return jsonify({'error': 'Report not found'}), 404
        try:
            from utils.pdf import generate_pdf_report
            settings = load_settings_fn(uid)
            user_doc = get_user_doc_fn(uid) or {}
            pdf_bytes = generate_pdf_report(entry, settings, user_doc)
            from flask import make_response
            response = make_response(pdf_bytes)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="report_{report_id[:8]}.pdf"'
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @api_bp.route('/reports/<report_id>/csv', methods=['GET'])
    def api_report_csv(report_id):
        uid = _get_uid()
        analyses = load_analyses_fn(uid if uid != 'guest' else None)
        entry = next((a for a in analyses if a.get('id') == report_id), None)
        if not entry:
            return jsonify({'error': 'Report not found'}), 404
        try:
            from reports import get_csv_summary_bytes
            from flask import make_response
            csv_bytes = get_csv_summary_bytes(entry)
            response = make_response(csv_bytes)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename="summary_{report_id[:8]}.csv"'
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ── Settings ─────────────────────────────────────────────────────────────

    @api_bp.route('/settings', methods=['GET', 'POST'])
    def api_settings():
        uid = _get_uid()
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form.to_dict()
            from settings import sanitize_settings
            current = load_settings_fn(uid)
            updated = sanitize_settings(data, current)
            save_settings_fn(uid, updated)
            return jsonify({'status': 'success', 'settings': updated})
        settings = load_settings_fn(uid)
        return jsonify({'status': 'success', 'settings': settings})

    # ── Notifications ────────────────────────────────────────────────────────

    @api_bp.route('/notifications', methods=['GET'])
    def api_notifications():
        uid = _get_uid()
        # Build notifications from recent high-risk analyses
        analyses = load_analyses_fn(uid if uid != 'guest' else None)
        notifs = []
        for a in analyses[:10]:
            if a.get('status') == 'HIGH':
                notifs.append({
                    'id': a.get('id'),
                    'type': 'alert',
                    'title': 'High Risk Detected',
                    'message': f"File {a.get('filename')} — {a.get('predicted_concentration')} ppm",
                    'timestamp': a.get('timestamp'),
                    'read': False,
                })
            elif a.get('status') == 'MODERATE':
                notifs.append({
                    'id': a.get('id'),
                    'type': 'warning',
                    'title': 'Moderate Risk',
                    'message': f"File {a.get('filename')} — {a.get('predicted_concentration')} ppm",
                    'timestamp': a.get('timestamp'),
                    'read': False,
                })
        return jsonify({'status': 'success', 'notifications': notifs, 'unread': len(notifs)})

    # ── Model Info ───────────────────────────────────────────────────────────

    @api_bp.route('/model/info', methods=['GET'])
    def api_model_info():
        try:
            from predictor import get_model_metrics
            metrics = get_model_metrics()
            return jsonify({'status': 'success', 'model': metrics})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return api_bp
