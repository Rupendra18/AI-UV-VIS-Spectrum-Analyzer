import pandas as pd

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    """Check if uploaded file has an allowed extension (.csv)."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_and_parse_csv(file_storage_or_path):
    """
    Validate and parse a CSV file for Wavelength and Absorbance columns.
    Returns (dataframe, error_message). If successful, error_message is None.
    """
    try:
        if hasattr(file_storage_or_path, 'read'):
            df = pd.read_csv(file_storage_or_path)
            file_storage_or_path.seek(0)
        else:
            df = pd.read_csv(file_storage_or_path)

        df.columns = df.columns.astype(str).str.strip()

        missing = [c for c in ['Wavelength', 'Absorbance'] if c not in df.columns]
        if missing:
            return None, f"CSV missing required column(s): {', '.join(missing)}. File must have 'Wavelength' and 'Absorbance' columns."

        df['Wavelength'] = pd.to_numeric(df['Wavelength'], errors='coerce')
        df['Absorbance'] = pd.to_numeric(df['Absorbance'], errors='coerce')
        df = df.dropna(subset=['Wavelength', 'Absorbance'])

        if df.empty:
            return None, "CSV contains no valid numeric data."

        return df, None
    except pd.errors.EmptyDataError:
        return None, "The uploaded CSV file is empty."
    except Exception as e:
        return None, f"Failed to parse CSV file: {str(e)}"
