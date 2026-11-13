import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}
ALLOWED_MIMES = {"image/png", "image/jpeg", "image/webp", "application/pdf"}

def allowed_file(filename: str, content_type: str = None) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    if content_type and content_type.lower() not in ALLOWED_MIMES:
        return False
    return True

def save_uploaded_file(file_storage, prefix: str = "med") -> str:
    """
    Safely stores an uploaded file with a randomized unique filename.
    Returns the generated secure filename.
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided")
        
    original_filename = secure_filename(file_storage.filename)
    if not allowed_file(original_filename, file_storage.content_type):
        raise ValueError("Invalid format. Allowed formats: PNG, JPG, JPEG, WEBP, PDF.")
        
    ext = original_filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"
    
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    
    target_path = os.path.join(upload_folder, unique_filename)
    file_storage.save(target_path)
    return unique_filename
