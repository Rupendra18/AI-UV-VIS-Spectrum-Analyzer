"""
DAST config loader — reads input.json at runtime.
Tokens are never written to the report (only presence is noted).
"""
import json, os, sys

_INPUT = os.path.join(os.path.dirname(__file__), '..', 'input.json')

def load_config():
    try:
        with open(_INPUT, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except FileNotFoundError:
        sys.exit(f"[FATAL] input.json not found at {_INPUT}")
    except json.JSONDecodeError as e:
        sys.exit(f"[FATAL] input.json parse error: {e}")

    base = cfg.get('baseUrl', '').rstrip('/')
    if not base:
        sys.exit("[FATAL] 'baseUrl' missing in input.json")

    tokens = {}
    for role in ('admin', 'user', 'guest'):
        t = cfg.get(role, '')
        # treat placeholder strings as missing
        if t and not t.startswith('REPLACE_WITH'):
            tokens[role] = t
        else:
            tokens[role] = ''

    return base, tokens
