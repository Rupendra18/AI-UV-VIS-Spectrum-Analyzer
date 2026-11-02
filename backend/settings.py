DEFAULT_SETTINGS = {
    'org_name': 'My Laboratory',
    'scientist_name': 'Scientist',
    'safe_limit': 5.0,
    'concentration_factor': 12.5,
    'theme': 'dark'
}

def sanitize_settings(form_data, current_settings=None):
    """
    Sanitize and extract settings from form/dict data.
    """
    updated = dict(current_settings or DEFAULT_SETTINGS)

    if 'org_name' in form_data:
        updated['org_name'] = str(form_data.get('org_name', '')).strip() or updated['org_name']
    if 'scientist_name' in form_data:
        updated['scientist_name'] = str(form_data.get('scientist_name', '')).strip() or updated['scientist_name']

    try:
        if 'safe_limit' in form_data:
            updated['safe_limit'] = float(form_data['safe_limit'])
    except (ValueError, TypeError):
        pass

    try:
        if 'concentration_factor' in form_data:
            updated['concentration_factor'] = float(form_data['concentration_factor'])
    except (ValueError, TypeError):
        pass

    if 'theme' in form_data:
        theme = str(form_data.get('theme', '')).lower()
        if theme in ['dark', 'light']:
            updated['theme'] = theme

    return updated
