from flask import Blueprint, send_from_directory, abort, current_app, request
from flask_login import login_required, current_user
from app.models.medical import MedicalApplication
from app.models.audit import AuditLog

files_bp = Blueprint('files', __name__)

@files_bp.route('/medical/<filename>')
@login_required
def get_medical_file(filename):
    """
    Secure file retrieval route for medical certificates.
    Strictly checks authorization to prevent IDOR (Insecure Direct Object Reference).
    Only the student who submitted the document or an authorized administrator can view/download.
    """
    med_app = MedicalApplication.query.filter_by(certificate_filename=filename).first()
    if not med_app:
        abort(404)

    # Authorization Check
    if not current_user.is_admin and current_user.id != med_app.student_id:
        AuditLog.log(
            action='UNAUTHORIZED_DOCUMENT_ACCESS_ATTEMPT',
            user_id=current_user.id,
            target_type='MedicalApplication',
            target_id=med_app.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"User {current_user.username} (ID {current_user.id}) attempted to access medical certificate of student ID {med_app.student_id}",
            severity='SECURITY_ALERT'
        )
        abort(403)

    return send_from_directory(
        current_app.config['MEDICAL_UPLOAD_FOLDER'],
        filename,
        as_attachment=False
    )


@files_bp.route('/avatar/<filename>')
@login_required
def get_avatar(filename):
    """Serves uploaded user profile avatars."""
    return send_from_directory(
        current_app.config['AVATAR_UPLOAD_FOLDER'],
        filename
    )
