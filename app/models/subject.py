from datetime import datetime, timezone
from app import db

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    semester = db.Column(db.Integer, nullable=False, default=6)
    department = db.Column(db.String(100), default='Computer Science')
    credits = db.Column(db.Integer, default=4)
    faculty_name = db.Column(db.String(100), default='Prof. Department Faculty')
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    attendances = db.relationship('SubjectAttendance', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    medical_applications = db.relationship('MedicalApplication', backref='subject', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'semester': self.semester,
            'department': self.department,
            'credits': self.credits,
            'faculty_name': self.faculty_name,
            'is_active': self.is_active
        }
