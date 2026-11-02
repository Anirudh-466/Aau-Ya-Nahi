import os
import uuid
from functools import wraps
from flask import abort, request, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.models.audit import AuditLog

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin:
            AuditLog.log(
                action='UNAUTHORIZED_ADMIN_ACCESS_ATTEMPT',
                user_id=current_user.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details=f"User {current_user.username} attempted to access admin endpoint: {request.path}",
                severity='SECURITY_ALERT'
            )
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_student:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename: str, allowed_extensions=None) -> bool:
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_secure_file(file_storage, target_folder, prefix="doc") -> tuple[str, str, int, str]:
    """
    Saves uploaded file securely with UUID filename to prevent directory traversal and overwrite attacks.
    Returns: (stored_filename, original_filename, file_size, mimetype)
    """
    original_name = secure_filename(file_storage.filename or 'upload')
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'dat'
    stored_name = f"{prefix}_{uuid.uuid4().hex}.{ext}"
    target_path = os.path.join(target_folder, stored_name)
    
    file_storage.save(target_path)
    file_size = os.path.getsize(target_path)
    mimetype = file_storage.mimetype or 'application/octet-stream'

    return stored_name, original_name, file_size, mimetype
