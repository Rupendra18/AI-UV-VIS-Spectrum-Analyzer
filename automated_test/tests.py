"""
DAST Test Categories 1-8
Each function returns a list of test-result dicts.
"""
import sys, time, datetime, json, io
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
import requests

DELAY = 0.3   # seconds between requests

def _ts():
    return datetime.datetime.utcnow().isoformat() + 'Z'

def _req(method, url, headers=None, json_body=None, files=None, data=None, allow_redirects=False):
    """Make a single timed request; return (status, elapsed_ms, body_text)."""
    try:
        r = requests.request(
            method, url,
            headers=headers or {},
            json=json_body,
            files=files,
            data=data,
            timeout=10,
            allow_redirects=allow_redirects,
        )
        ms = round(r.elapsed.total_seconds() * 1000)
        try:
            body = r.text[:500]
        except Exception:
            body = ''
        return r.status_code, ms, body
    except requests.exceptions.ConnectionError:
        return 0, 0, 'CONNECTION_REFUSED'
    except requests.exceptions.Timeout:
        return 0, 0, 'TIMEOUT'
    except Exception as ex:
        return 0, 0, str(ex)

def _auth_header(token):
    if token:
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    return {'Content-Type': 'application/json'}

def _rec(endpoint, method, role, status, expected_status, finding, severity, ms, category, note):
    clean_note = str(note).encode('ascii', errors='replace').decode('ascii')
    return {
        'endpoint': endpoint,
        'method': method,
        'role': role,
        'status': status,
        'expected_status': expected_status,
        'finding': finding,
        'severity': severity,
        'response_time_ms': ms,
        'test_category': category,
        'note': clean_note,
        'timestamp': _ts(),
    }

# -----------------------------------------------------------------------------
# CAT 1 -- AuthN Bypass
# Protected endpoints called with NO token / malformed token / expired token
# -----------------------------------------------------------------------------
def test_authn_bypass(base, tokens):
    results = []
    cat = 'AuthN-Bypass'

    protected_api = [
        ('GET',  '/api/auth/profile'),
        ('GET',  '/api/history'),
        ('GET',  '/api/reports'),
        ('GET',  '/api/dashboard/stats'),
        ('GET',  '/api/settings'),
        ('GET',  '/api/notifications'),
    ]

    malformed_tokens = [
        ('no-token',       None),
        ('malformed',      'notavalidtoken'),
        ('expired',        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJ0ZXN0IiwiZXhwIjoxfQ.invalid_sig'),
        ('bearer-empty',   ''),
        ('bearer-null',    'null'),
        ('bearer-admin-claim', 'eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1aWQiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.'),
    ]

    for method, path in protected_api:
        for tok_name, tok_val in malformed_tokens:
            url = base + path
            hdrs = {}
            if tok_val is not None:
                hdrs['Authorization'] = f'Bearer {tok_val}'
            hdrs['Content-Type'] = 'application/json'
            status, ms, body = _req(method, url, headers=hdrs)
            time.sleep(DELAY)

            # For API endpoints, 200 = bypass finding; 401/403 = good
            finding = (status == 200)
            # Special: /api/history and similar may return 200 even for guests (design issue)
            # We flag 2xx on /api/auth/profile as definitely bad
            severity = 'CRITICAL' if (finding and path == '/api/auth/profile') else (
                        'HIGH'     if (finding and path in ('/api/history', '/api/reports', '/api/notifications')) else (
                        'MEDIUM'   if finding else 'INFO'))
            note = f'token_variant={tok_name} body_preview={body[:100]}'
            results.append(_rec(path, method, f'unauthenticated/{tok_name}',
                                status, '401 or 403', finding, severity, ms, cat, note))

            sym = '[FAIL] FINDING' if finding else '[OK]'
            print(f'  [{cat}] {sym}  {method} {path} [{tok_name}] -> {status}')
    return results


# -----------------------------------------------------------------------------
# CAT 2 -- AuthZ / Privilege Escalation
# -----------------------------------------------------------------------------
def test_authz_privesc(base, tokens):
    results = []
    cat = 'AuthZ-PrivEsc'

    # Admin-only conceptual endpoints -- test with user token
    admin_targets = [
        ('GET',  '/api/auth/profile'),        # Own profile is ok, but IDOR via X-User-ID?
        ('GET',  '/api/dashboard/stats'),
        ('GET',  '/api/history'),
        ('GET',  '/api/reports'),
        ('GET',  '/api/notifications'),
        ('GET',  '/api/model/info'),
        ('GET',  '/api/settings'),
    ]
    user_token = tokens.get('user', '')
    if not user_token:
        print(f'  [{cat}] [!]  No user token -- skipping privilege-escalation tests (not configured in input.json)')
        results.append(_rec('/api/*', 'GET', 'user', 0, 'N/A', False, 'INFO', 0, cat,
                            'user token not configured in input.json -- skipped'))
        return results

    for method, path in admin_targets:
        url = base + path
        status, ms, body = _req(method, url, headers=_auth_header(user_token))
        time.sleep(DELAY)
        finding = status == 200   # user-token can reach these -- may be intentional
        severity = 'INFO'
        note = f'user_token_access={"yes" if finding else "no"} body_preview={body[:100]}'
        results.append(_rec(path, method, 'user', status, '200 (user scope)',
                            False, severity, ms, cat, note))
        print(f'  [{cat}]  {method} {path} [user] -> {status}')
    return results


# -----------------------------------------------------------------------------
# CAT 3 -- IDOR
# Vary ID params to reach another principal\'s object.
# -----------------------------------------------------------------------------
def test_idor(base, tokens):
    results = []
    cat = 'IDOR'

    # Probe a range of synthetic IDs -- if we get 200 bodies with real data that is IDOR
    synthetic_ids = [
        '00000000-0000-0000-0000-000000000001',
        '11111111-1111-1111-1111-111111111111',
        'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
        '../../../etc/passwd',
        "' OR '1'='1",
        '0',
        '1',
        '-1',
        'null',
        '%00',
    ]

    idor_endpoints = [
        ('/api/reports/{id}/pdf',  'GET'),
        ('/api/reports/{id}/csv',  'GET'),
        ('/report/download/{id}',  'GET'),
        ('/report/view/{id}',      'GET'),
        ('/download/csv/{id}',     'GET'),
    ]

    # Guest has no token -- best scenario to test unauthenticated IDOR
    for path_tpl, method in idor_endpoints:
        for sid in synthetic_ids[:5]:  # limit to 5 per endpoint
            import urllib.parse
            safe_id = urllib.parse.quote(str(sid), safe='')
            path = path_tpl.replace('{id}', safe_id)
            url = base + path
            status, ms, body = _req(method, url, headers={'Content-Type': 'application/json'})
            time.sleep(DELAY)

            # A 200 with a PDF/CSV body on an unauthenticated request = IDOR
            finding = (status == 200 and 'Report not found' not in body and 'error' not in body.lower()[:50])
            severity = 'HIGH' if finding else 'INFO'
            note = f'probe_id={sid[:30]} body_preview={body[:80]}'
            results.append(_rec(path_tpl, method, 'unauthenticated', status,
                                '404 or 401', finding, severity, ms, cat, note))
            sym = '[FAIL] FINDING' if finding else '[OK]'
            print(f'  [{cat}] {sym}  {method} {path_tpl} id={sid[:20]} -> {status}')
    return results


# -----------------------------------------------------------------------------
# CAT 4 -- RBAC Matrix
# -----------------------------------------------------------------------------
def test_rbac_matrix(base, tokens):
    results = []
    cat = 'RBAC-Matrix'

    roles_tested = {
        'guest':  '',
        'user':   tokens.get('user', ''),
        'admin':  tokens.get('admin', ''),
    }
    all_api_endpoints = [
        ('GET',    '/api/auth/profile'),
        ('GET',    '/api/dashboard/stats'),
        ('GET',    '/api/history'),
        ('GET',    '/api/reports'),
        ('GET',    '/api/settings'),
        ('POST',   '/api/settings'),
        ('GET',    '/api/notifications'),
        ('GET',    '/api/model/info'),
        ('POST',   '/api/auth/logout'),
    ]

    for method, path in all_api_endpoints:
        for role, tok in roles_tested.items():
            url = base + path
            hdrs = _auth_header(tok)
            if method == 'POST' and path == '/api/settings':
                status, ms, body = _req(method, url, headers=hdrs,
                                        json_body={'safe_limit': 5.0})
            else:
                status, ms, body = _req(method, url, headers=hdrs)
            time.sleep(DELAY)

            # Determine expected vs actual
            if path == '/api/auth/profile':
                expected = '401' if role == 'guest' else '200'
                finding  = (role == 'guest' and status == 200)
            elif path in ('/api/settings',) and method == 'POST':
                expected = '401 or 403' if role == 'guest' else '200'
                finding  = (role == 'guest' and status in (200, 201))
            else:
                expected = '200'
                finding  = False   # informational

            severity = 'HIGH' if finding else 'INFO'
            note = f'body_preview={body[:80]}'
            results.append(_rec(path, method, role, status, expected,
                                finding, severity, ms, cat, note))
            sym = '[FAIL]' if finding else '[OK]'
            print(f'  [{cat}] {sym}  {method} {path} [{role}] -> {status}')
    return results


# -----------------------------------------------------------------------------
# CAT 5 -- Token Tampering
# Flip JWT claims without re-signing; server MUST reject (non-2xx)
# -----------------------------------------------------------------------------
def test_token_tampering(base, tokens):
    results = []
    cat = 'Token-Tampering'

    import base64

    def forge_jwt(uid, role='admin', algorithm='HS256', use_none_alg=False):
        """Forge a JWT with modified claims -- NOT re-signed correctly."""
        header = {'alg': 'none' if use_none_alg else algorithm, 'typ': 'JWT'}
        payload = {
            'uid': uid,
            'email': 'attacker@evil.com',
            'role': role,
            'exp': 9999999999,
            'iat': 1000000000,
        }
        def b64url(d):
            return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b'=').decode()
        h = b64url(header)
        p = b64url(payload)
        if use_none_alg:
            return f'{h}.{p}.'  # empty signature
        else:
            return f'{h}.{p}.INVALIDSIGNATURE'

    tampered_tokens = [
        ('alg-none-admin',      forge_jwt('any_uid', 'admin', use_none_alg=True)),
        ('alg-none-user',       forge_jwt('any_uid', 'user',  use_none_alg=True)),
        ('wrong-sig-admin',     forge_jwt('any_uid', 'admin', use_none_alg=False)),
        ('wrong-sig-user',      forge_jwt('any_uid', 'user',  use_none_alg=False)),
        ('uid-override-guest',  forge_jwt('guest', 'admin', use_none_alg=False)),
    ]

    probe_endpoints = [
        ('GET',  '/api/auth/profile'),
        ('GET',  '/api/history'),
        ('GET',  '/api/reports'),
        ('GET',  '/api/settings'),
    ]

    for tok_name, tok_val in tampered_tokens:
        for method, path in probe_endpoints:
            url = base + path
            hdrs = {'Authorization': f'Bearer {tok_val}', 'Content-Type': 'application/json'}
            status, ms, body = _req(method, url, headers=hdrs)
            time.sleep(DELAY)

            # Server SHOULD reject tampered tokens
            # CRITICAL: alg=none accepted = severe vulnerability
            finding_critical = (tok_name.startswith('alg-none') and status == 200)
            finding_high     = (not finding_critical and status == 200 and 'wrong-sig' in tok_name)
            finding          = finding_critical or finding_high
            severity         = 'CRITICAL' if finding_critical else ('HIGH' if finding_high else 'INFO')
            note = f'tamper={tok_name} body_preview={body[:80]}'
            results.append(_rec(path, method, f'tampered/{tok_name}',
                                status, '401 or 403', finding, severity, ms, cat, note))
            sym = '[FAIL] FINDING' if finding else '[OK]'
            print(f'  [{cat}] {sym}  {method} {path} [{tok_name}] -> {status}')
    return results


# -----------------------------------------------------------------------------
# CAT 6 -- Injection Detection
# SQLi / NoSQLi payloads in params -- detection only
# -----------------------------------------------------------------------------
def test_injection(base, tokens):
    results = []
    cat = 'Injection'

    payloads = [
        ("sqli-basic",   "' OR '1'='1"),
        ("sqli-comment", "' OR 1=1--"),
        ("sqli-union",   "' UNION SELECT null,null--"),
        ("nosqli-ne",    '{"$ne": null}'),
        ("xss-script",   '<script>alert(1)</script>'),
        ("path-trav",    '../../etc/passwd'),
        ("null-byte",    '%00'),
    ]

    # Inject in query params for GET endpoints
    get_targets = [
        '/api/history?search={}',
        '/api/history?status={}',
        '/api/reports',
    ]

    # Inject in JSON body for POST endpoints
    post_targets = [
        ('/api/auth/login',    {'email': '{}', 'password': 'test'}),
        ('/api/auth/register', {'name': '{}', 'email': 'test@t.com', 'password': 'pwd123'}),
        ('/api/predict',       {'points': [{'Wavelength': '{}', 'Absorbance': 0.5}]}),
    ]

    for pname, pval in payloads:
        # GET injection
        for tpl in get_targets:
            if '{}' in tpl:
                url = base + tpl.format(requests.utils.quote(pval))
            else:
                url = base + tpl
            t0 = time.time()
            status, ms, body = _req('GET', url, headers={'Content-Type': 'application/json'})
            elapsed = time.time() - t0
            time.sleep(DELAY)

            # Flag: 500 = unhandled error (possible injection); >5s timing = possible blind
            finding = (status == 500 or elapsed > 5.0)
            severity = 'HIGH' if finding else 'INFO'
            note = f'payload={pname} elapsed={elapsed:.2f}s body_preview={body[:80]}'
            results.append(_rec(tpl, 'GET', f'unauthenticated/{pname}',
                                status, '200 or 400', finding, severity, ms, cat, note))
            sym = '[FAIL] FINDING' if finding else '[OK]'
            print(f'  [{cat}] {sym}  GET {tpl[:40]} [{pname}] -> {status}')

        # POST injection
        for path, body_tpl in post_targets:
            import copy
            body_data = copy.deepcopy(body_tpl)
            # Replace '{}' placeholders with payload
            body_str = json.dumps(body_data).replace('"{}"', json.dumps(pval))
            try:
                body_data = json.loads(body_str)
            except Exception:
                body_data = body_tpl

            t0 = time.time()
            status, ms, body_resp = _req('POST', base + path, headers={'Content-Type': 'application/json'},
                                         json_body=body_data)
            elapsed = time.time() - t0
            time.sleep(DELAY)

            finding = (status == 500 or elapsed > 5.0)
            severity = 'HIGH' if finding else 'INFO'
            note = f'payload={pname} elapsed={elapsed:.2f}s body_preview={body_resp[:80]}'
            results.append(_rec(path, 'POST', f'unauthenticated/{pname}',
                                status, '200 or 400 or 401', finding, severity, ms, cat, note))
            sym = '[FAIL] FINDING' if finding else '[OK]'
            print(f'  [{cat}] {sym}  POST {path} [{pname}] -> {status}')
    return results


# -----------------------------------------------------------------------------
# CAT 7 -- Rate Limiting
# Send ~30 rapid requests; expect 429 within the burst
# -----------------------------------------------------------------------------
def test_rate_limiting(base, tokens):
    results = []
    cat = 'RateLimit'
    BURST = 30

    probes = [
        ('POST', '/api/auth/login',    {'email': 'rate@test.com', 'password': 'badpass'}),
        ('GET',  '/api/history',       None),
        ('GET',  '/api/model/info',    None),
    ]

    for method, path, body in probes:
        url = base + path
        statuses = []
        for i in range(BURST):
            status, ms, _ = _req(method, url,
                                  headers={'Content-Type': 'application/json'},
                                  json_body=body)
            statuses.append(status)
            # No artificial delay -- we want to stress it

        got_429 = 429 in statuses
        finding = not got_429  # no 429 = no rate limiting = finding
        severity = 'MEDIUM' if finding else 'INFO'
        rate_limited_at = next((i+1 for i,s in enumerate(statuses) if s == 429), None)
        note = (f'burst={BURST} statuses_summary={dict((s,statuses.count(s)) for s in set(statuses))} '
                f'rate_limited_at_req={rate_limited_at}')
        results.append(_rec(path, method, 'unauthenticated', 
                            429 if got_429 else statuses[-1],
                            '429 within burst', finding, severity,
                            0, cat, note))
        sym = '[FAIL] NO RATE LIMIT' if finding else '[OK] rate limited'
        print(f'  [{cat}] {sym}  {method} {path}  -- {note}')
    return results


# -----------------------------------------------------------------------------
# CAT 8 -- Hardcoded Credentials (static code scan)
# -----------------------------------------------------------------------------
def test_hardcoded_creds(base, tokens):
    """Scan the codebase for committed secrets / hardcoded credentials."""
    results = []
    cat = 'Hardcoded-Creds'
    import re, os, pathlib

    ROOT = pathlib.Path(__file__).parent.parent
    SCAN_EXTS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.env',
                 '.yml', '.yaml', '.properties', '.txt', '.md'}
    SKIP_DIRS = {'node_modules', '.git', '__pycache__', 'dist', 'build',
                 '.gradle', 'venv', 'env', '.idea', 'automated_test'}

    patterns = [
        ('hardcoded-flask-secret',   re.compile(r"secret_key\s*=\s*['\"][^'\"]{8,}['\"]", re.I)),
        ('hardcoded-jwt-secret',     re.compile(r"(JWT_SECRET|jwt_secret)\s*[=:]\s*['\"][^'\"]{8,}['\"]", re.I)),
        ('hardcoded-password',       re.compile(r"password\s*=\s*['\"][^'\"]{4,}['\"]", re.I)),
        ('hardcoded-api-key',        re.compile(r"(api_key|apikey|API_KEY)\s*[=:]\s*['\"][^'\"]{8,}['\"]", re.I)),
        ('private-key-header',       re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----")),
        ('google-service-account',   re.compile(r'"type"\s*:\s*"service_account"')),
        ('firebase-config-apikey',   re.compile(r'apiKey\s*:\s*["\'][A-Za-z0-9_-]{20,}["\']')),
        ('default-secret-in-code',   re.compile(r'uv-vis-spectrum')),
    ]

    findings = []
    for root, dirs, files in os.walk(str(ROOT)):
        # Prune skip directories in-place so os.walk does not recurse into them
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            ext = os.path.splitext(fname)[1]
            if ext not in SCAN_EXTS:
                continue
            full_path = os.path.join(root, fname)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue
            fpath = pathlib.Path(full_path)
            for pname, pat in patterns:
                for m in pat.finditer(content):
                    line_no = content[:m.start()].count('\n') + 1
                    snippet = m.group(0)[:80].replace('\n', ' ').encode('ascii', errors='replace').decode('ascii')
                    rel = str(fpath.relative_to(ROOT))
                    findings.append({'pattern': pname, 'file': rel,
                                     'line': line_no, 'snippet': snippet})
                    print(f'  [{cat}] [FIND]  {pname}  {rel}:{line_no}  -> {snippet}')
                    results.append(_rec(
                        f'{rel}:{line_no}', 'STATIC', 'codebase',
                        0, 'no-secrets-in-code', True,
                        'HIGH' if 'private-key' in pname or 'service-account' in pname else 'MEDIUM',
                        0, cat,
                        f'pattern={pname} snippet={snippet}',
                    ))

    if not findings:
        print(f'  [{cat}] [OK]  No obvious hardcoded secrets found in codebase')
        results.append(_rec('codebase', 'STATIC', 'codebase', 0,
                            'no-secrets-in-code', False, 'INFO', 0, cat,
                            'No obvious hardcoded secrets detected'))
    return results
