from datetime import datetime, date, timezone
import uuid
from app import db

class MedicalApplication(db.Model):
    """
    Medical Attendance Applications submitted by students.
    Strictly protected against student modification once submitted/approved.
    """
    __tablename__ = 'medical_applications'

    id = db.Column(db.Integer, primary_key=True)
    application_number = db.Column(db.String(36), unique=True, nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, index=True)
    
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    requested_classes = db.Column(db.Integer, nullable=False, default=1)
    approved_classes = db.Column(db.Integer, nullable=False, default=0)
    
    reason = db.Column(db.Text, nullable=False)
    certificate_filename = db.Column(db.String(255), nullable=False)
    certificate_original_name = db.Column(db.String(255), nullable=False)
    certificate_mimetype = db.Column(db.String(100), nullable=True)
    certificate_size = db.Column(db.Integer, nullable=True)
    
    # Status: 'Pending', 'Approved', 'Rejected'
    status = db.Column(db.String(20), default='Pending', nullable=False, index=True)
    admin_remarks = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    is_locked = db.Column(db.Boolean, default=True, nullable=False)  # Immutable by students once submitted
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    @classmethod
    def generate_app_number(cls) -> str:
        current_year = date.today().year
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"MED-{current_year}-{random_suffix}"

    @property
    def duration_days(self) -> int:
        if self.start_date and self.end_date:
            return max(1, (self.end_date - self.start_date).days + 1)
        return 1

    @property
    def status_badge_class(self) -> str:
        mapping = {
            'Approved': 'badge-safe',
            'Pending': 'badge-warning',
            'Rejected': 'badge-danger'
        }
        return mapping.get(self.status, 'badge-secondary')

    def to_dict(self):
        return {
            'id': self.id,
            'application_number': self.application_number,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else '',
            'student_reg': self.student.registration_number if self.student else '',
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else '',
            'subject_code': self.subject.code if self.subject else '',
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else '',
            'duration_days': self.duration_days,
            'requested_classes': self.requested_classes,
            'approved_classes': self.approved_classes,
            'reason': self.reason,
            'certificate_filename': self.certificate_filename,
            'certificate_original_name': self.certificate_original_name,
            'status': self.status,
            'status_badge_class': self.status_badge_class,
            'admin_remarks': self.admin_remarks or '',
            'reviewer_name': self.reviewer.full_name if self.reviewer else '',
            'reviewed_at': self.reviewed_at.strftime('%Y-%m-%d %H:%M') if self.reviewed_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }
