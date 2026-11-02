def filter_and_sort_history(analyses, search='', status_filter='', sort_by='date_desc'):
    """
    Search, filter by status, and sort spectrum analysis history entries.
    """
    results = list(analyses)

    if search:
        s = search.lower().strip()
        results = [
            a for a in results
            if s in a.get('filename', '').lower()
            or s in a.get('status', '').lower()
            or s in str(a.get('predicted_concentration', '')).lower()
            or s in str(a.get('peak_wavelength', '')).lower()
        ]

    if status_filter and status_filter.upper() in ['SAFE', 'MODERATE', 'HIGH']:
        results = [a for a in results if a.get('status') == status_filter.upper()]

    if sort_by == 'date_asc':
        results = list(reversed(results))
    elif sort_by == 'conc_desc':
        results = sorted(results, key=lambda x: x.get('predicted_concentration', 0), reverse=True)
    elif sort_by == 'conc_asc':
        results = sorted(results, key=lambda x: x.get('predicted_concentration', 0))

    return results
