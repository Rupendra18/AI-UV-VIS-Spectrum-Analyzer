import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from utils.validation import allowed_file, validate_and_parse_csv
from utils.firebase import upload_to_storage
from prediction import analyze_spectrum_df

def process_file_upload(file_obj, upload_folder, uid, settings, save_analysis_fn):
    """
    Validates, saves, analyzes uploaded CSV spectrum file and persists analysis entry.
    Returns (success_boolean, result_data_or_error_msg, filename).
    """
    if not file_obj or file_obj.filename == '':
        return False, "No file selected.", None

    if not allowed_file(file_obj.filename):
        return False, "Invalid file type. Please upload a CSV file.", None

    df, err = validate_and_parse_csv(file_obj)
    if err:
        return False, err, None

    filename = secure_filename(file_obj.filename)
    filepath = os.path.join(upload_folder, filename)
    file_obj.seek(0)
    file_obj.save(filepath)

    safe_limit = settings.get('safe_limit', 5.0)

    analysis_res = analyze_spectrum_df(df, safe_limit=safe_limit)

    csv_url = upload_to_storage(filepath, f'csv/{uid}/{filename}', 'text/csv')

    entry = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
        'csv_url': csv_url or '',
        'pdf_url': '',
    }

    doc_id = save_analysis_fn(uid, entry)
    entry['id'] = doc_id or entry['id']
    return True, entry, filename
