"""
DAST Runner -- orchestrates all test categories and writes report.json
Usage:  python automated_test/runner.py
"""
import json, os, sys, time, datetime

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from config import load_config
from tests import (
    test_authn_bypass,
    test_authz_privesc,
    test_idor,
    test_rbac_matrix,
    test_token_tampering,
    test_injection,
    test_rate_limiting,
    test_hardcoded_creds,
)

REPORT_PATH = os.path.join(os.path.dirname(__file__), 'report.json')
SAVEPOINT   = os.path.join(os.path.dirname(__file__), 'savepoint_results.json')

def banner(title):
    print('\n' + '='*70)
    print(f'  {title}')
    print('='*70)

def check_server_reachable(base):
    import requests
    try:
        r = requests.get(base + '/login', timeout=5, allow_redirects=True)
        print(f'  [REACH] Server reachable -- HTTP {r.status_code}')
        return True
    except Exception as e:
        print(f'  [REACH] [FAIL] Cannot reach {base}: {e}')
        return False

def print_summary(results):
    total      = len(results)
    findings   = [r for r in results if r['finding']]
    by_sev     = {}
    for r in findings:
        by_sev.setdefault(r['severity'], []).append(r)

    banner('STEP 4 -- DAST REPORT SUMMARY')
    print(f'  Tests run   : {total}')
    print(f'  Findings    : {len(findings)}')
    print()
    for sev in ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'):
        items = by_sev.get(sev, [])
        if items:
            sym = {'CRITICAL': '[CRIT]', 'HIGH': '[HIGH]', 'MEDIUM': '[MED]', 'LOW': '[LOW]', 'INFO': '[INFO]'}.get(sev, '[INFO]')
            print(f'  {sym} {sev}: {len(items)}')
            for item in items:
                print(f'       [{item["test_category"]}] {item["method"]} {item["endpoint"]} [{item["role"]}]')
                print(f'         -> {item["note"][:120]}')

    print()
    if any(r['severity'] in ('CRITICAL', 'HIGH') for r in findings):
        print('  TOP ISSUES TO FIX FIRST:')
        for r in findings:
            if r['severity'] in ('CRITICAL', 'HIGH'):
                print(f'    [FAIL]  [{r["severity"]}] {r["test_category"]}  {r["method"]} {r["endpoint"]}')
                print(f'       {r["note"][:140]}')
    else:
        print('  [OK] No CRITICAL or HIGH findings.')
    print()
    print(f'  Full report -> {REPORT_PATH}')

def main():
    base, tokens = load_config()

    print(f'\n[CONFIG] Base URL : {base}')
    print(f'[CONFIG] Roles configured: ' +
          ', '.join(r for r,t in tokens.items() if t) or 'none')

    banner('CONNECTIVITY CHECK')
    if not check_server_reachable(base):
        print('\n  [!]  Server is DOWN or unreachable.')
        print(f'  Start the backend: cd backend && python app.py')
        print('  Then re-run: python automated_test/runner.py')
        sys.exit(1)

    all_results = []

    banner('CAT 1 -- AuthN Bypass')
    r1 = test_authn_bypass(base, tokens)
    all_results.extend(r1)
    _save(all_results)

    banner('CAT 2 -- AuthZ / Privilege Escalation')
    r2 = test_authz_privesc(base, tokens)
    all_results.extend(r2)
    _save(all_results)

    banner('CAT 3 -- IDOR')
    r3 = test_idor(base, tokens)
    all_results.extend(r3)
    _save(all_results)

    banner('CAT 4 -- RBAC Matrix')
    r4 = test_rbac_matrix(base, tokens)
    all_results.extend(r4)
    _save(all_results)

    banner('CAT 5 -- Token Tampering')
    r5 = test_token_tampering(base, tokens)
    all_results.extend(r5)
    _save(all_results)

    banner('CAT 6 -- Injection Detection')
    r6 = test_injection(base, tokens)
    all_results.extend(r6)
    _save(all_results)

    banner('CAT 7 -- Rate Limiting')
    r7 = test_rate_limiting(base, tokens)
    all_results.extend(r7)
    _save(all_results)

    banner('CAT 8 -- Hardcoded Credentials (static scan)')
    r8 = test_hardcoded_creds(base, tokens)
    all_results.extend(r8)

    # Write final report
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print(f'\n[REPORT] Written -> {REPORT_PATH}  ({len(all_results)} records)')

    print_summary(all_results)

def _save(results):
    """Persist savepoint after each category."""
    with open(SAVEPOINT, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()
