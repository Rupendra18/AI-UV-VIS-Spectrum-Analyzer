"""
DAST Step 1 — Endpoint Discovery
Produces: automated_test/savepoint_endpoints.json
"""
import json, os, sys

ENDPOINTS = [
    # ── Public / Auth (no auth required) ────────────────────────────────────
    {"path": "/",               "method": "GET",    "access": "public",       "description": "Login page / splash redirect"},
    {"path": "/login",          "method": "GET",    "access": "public",       "description": "Login page"},
    {"path": "/login",          "method": "POST",   "access": "public",       "description": "Login form submit"},
    {"path": "/register",       "method": "GET",    "access": "public",       "description": "Register page"},
    {"path": "/register",       "method": "POST",   "access": "public",       "description": "Register form submit"},
    {"path": "/splash",         "method": "GET",    "access": "public",       "description": "Splash screen"},
    {"path": "/forgot-password","method": "GET",    "access": "public",       "description": "Forgot password page"},
    {"path": "/firebase-setup", "method": "GET",    "access": "public",       "description": "Firebase setup page"},

    # ── Web-UI Session Auth (requires session cookie) ────────────────────────
    {"path": "/logout",                          "method": "GET",  "access": "requires-auth", "description": "Logout"},
    {"path": "/dashboard",                       "method": "GET",  "access": "requires-auth", "description": "Dashboard"},
    {"path": "/upload",                          "method": "POST", "access": "requires-auth", "description": "Upload CSV file"},
    {"path": "/reports",                         "method": "GET",  "access": "requires-auth", "description": "Reports list"},
    {"path": "/report/delete/<report_id>",       "method": "POST", "access": "requires-auth", "description": "Delete report"},
    {"path": "/report/download/<report_id>",     "method": "GET",  "access": "requires-auth", "description": "Download PDF report"},
    {"path": "/report/view/<report_id>",         "method": "GET",  "access": "requires-auth", "description": "View PDF inline"},
    {"path": "/download/csv/<report_id>",        "method": "GET",  "access": "requires-auth", "description": "Download CSV summary"},
    {"path": "/history",                         "method": "GET",  "access": "requires-auth", "description": "Analysis history"},
    {"path": "/history/delete/<entry_id>",       "method": "POST", "access": "requires-auth", "description": "Delete history entry"},
    {"path": "/settings",                        "method": "GET",  "access": "requires-auth", "description": "Settings page"},
    {"path": "/settings",                        "method": "POST", "access": "requires-auth", "description": "Save settings"},

    # ── Firebase Session API (requires Firebase configured) ──────────────────
    {"path": "/api/login",    "method": "POST", "access": "public",       "description": "Firebase session login"},
    {"path": "/api/register", "method": "POST", "access": "public",       "description": "Firebase register"},

    # ── REST API Blueprint (/api/*) ──────────────────────────────────────────
    # Auth
    {"path": "/api/auth/register",       "method": "POST",   "access": "public",            "description": "REST register (local/Firebase)"},
    {"path": "/api/auth/login",          "method": "POST",   "access": "public",            "description": "REST login (local/Firebase)"},
    {"path": "/api/auth/logout",         "method": "POST",   "access": "requires-auth",     "description": "REST logout"},
    {"path": "/api/auth/profile",        "method": "GET",    "access": "requires-auth",     "description": "Get user profile"},
    {"path": "/api/auth/profile",        "method": "PUT",    "access": "requires-auth",     "description": "Update user profile"},

    # Dashboard
    {"path": "/api/dashboard/stats",     "method": "GET",    "access": "public-leaks-data", "description": "Dashboard KPI stats (guest fallback exposes all data)"},

    # Upload & Predict
    {"path": "/api/upload",              "method": "POST",   "access": "public-leaks-data", "description": "Upload & analyse CSV (no auth enforced — uses guest UID)"},
    {"path": "/api/predict",             "method": "POST",   "access": "public-leaks-data", "description": "Inline JSON prediction (no auth enforced)"},

    # History
    {"path": "/api/history",             "method": "GET",    "access": "public-leaks-data", "description": "Analysis history (guest gets all records)"},
    {"path": "/api/history/<id>",        "method": "DELETE", "access": "requires-auth",     "description": "Delete history entry"},

    # Reports
    {"path": "/api/reports",             "method": "GET",    "access": "public-leaks-data", "description": "Reports list (guest gets all records)"},
    {"path": "/api/reports/<id>/pdf",    "method": "GET",    "access": "public-leaks-data", "description": "Download PDF (guest fallback)"},
    {"path": "/api/reports/<id>/csv",    "method": "GET",    "access": "public-leaks-data", "description": "Download CSV (guest fallback)"},

    # Settings
    {"path": "/api/settings",            "method": "GET",    "access": "public-leaks-data", "description": "Get settings (guest fallback)"},
    {"path": "/api/settings",            "method": "POST",   "access": "public-leaks-data", "description": "Save settings (no auth enforced)"},

    # Notifications
    {"path": "/api/notifications",       "method": "GET",    "access": "public-leaks-data", "description": "Notifications (guest gets all high-risk alerts)"},

    # Model Info
    {"path": "/api/model/info",          "method": "GET",    "access": "public",            "description": "ML model info/metrics"},
]

def save_endpoints():
    out = os.path.join(os.path.dirname(__file__), 'savepoint_endpoints.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(ENDPOINTS, f, indent=2)
    print(f"\n[DISCOVERY] Saved {len(ENDPOINTS)} endpoints -> {out}\n")
    return ENDPOINTS

def print_endpoints():
    print("\n" + "="*80)
    print(" STEP 1 — DISCOVERED ENDPOINTS")
    print("="*80)
    grouped = {}
    for e in ENDPOINTS:
        g = e['access']
        grouped.setdefault(g, []).append(e)
    for group, items in grouped.items():
        print(f"\n  [{group.upper()}]")
        for e in items:
            print(f"    {e['method']:<6} {e['path']:<40}  — {e['description']}")
    print(f"\n  TOTAL: {len(ENDPOINTS)} endpoints\n")
    print("="*80)

if __name__ == '__main__':
    print_endpoints()
    save_endpoints()
    print("\n⏸  PAUSING: Review the endpoint list above.")
    print("   Confirm you are authorized to test all endpoints listed.")
    print("   Then run: python automated_test/runner.py")
