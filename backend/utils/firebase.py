import os

FIREBASE_CONFIGURED = False
db = None
bucket = None
firebase_admin_app = None

SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'serviceAccountKey.json')

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth as firebase_auth, storage

    if os.path.exists(SERVICE_ACCOUNT_PATH):
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin_app = firebase_admin.initialize_app(cred, {
            'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', '')
        })
        db = firestore.client()
        try:
            bucket = storage.bucket()
            if not bucket.name:
                bucket = None
        except Exception:
            bucket = None
        FIREBASE_CONFIGURED = True
    else:
        FIREBASE_CONFIGURED = False
except Exception:
    FIREBASE_CONFIGURED = False


def is_firebase_configured():
    return FIREBASE_CONFIGURED


def get_db():
    return db


def get_bucket():
    return bucket


def upload_to_storage(local_path, remote_path, content_type='application/octet-stream'):
    """Upload a local file to Firebase Storage. Returns public URL or None."""
    if not FIREBASE_CONFIGURED or not bucket:
        return None
    try:
        blob = bucket.blob(remote_path)
        blob.upload_from_filename(local_path, content_type=content_type)
        blob.make_public()
        return blob.public_url
    except Exception:
        return None


def upload_bytes_to_storage(data_bytes, remote_path, content_type='application/octet-stream'):
    """Upload byte contents to Firebase Storage. Returns public URL or None."""
    if not FIREBASE_CONFIGURED or not bucket:
        return None
    try:
        blob = bucket.blob(remote_path)
        blob.upload_from_string(data_bytes, content_type=content_type)
        blob.make_public()
        return blob.public_url
    except Exception:
        return None
