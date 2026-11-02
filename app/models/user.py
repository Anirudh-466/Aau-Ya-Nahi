from datetime import datetime, timezone
from flask_login import UserMixin
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from app import db, login_manager

ph = PasswordHasher()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'admin'
    
    # Profile information
    full_name = db.Column(db.String(100), nullable=False)
    registration_number = db.Column(db.String(50), unique=True, nullable=True, index=True)
    university = db.Column(db.String(120), default='SmartAttend Institute of Science & Technology')
    course = db.Column(db.String(50), default='B.Tech')
    branch = db.Column(db.String(50), default='Computer Science & Engineering')
    semester = db.Column(db.Integer, default=6)
    phone = db.Column(db.String(20), nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)  # File name in uploads/avatars
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    attendances = db.relationship('SubjectAttendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    medical_applications = db.relationship('MedicalApplication', foreign_keys='MedicalApplication.student_id', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    reviewed_applications = db.relationship('MedicalApplication', foreign_keys='MedicalApplication.reviewed_by', backref='reviewer', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')

    def set_password(self, password: str):
        """Hash password using Argon2id algorithm."""
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")
        self.password_hash = ph.hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password against Argon2 hash."""
        if not self.password_hash or not password:
            return False
        try:
            return ph.verify(self.password_hash, password)
        except (VerifyMismatchError, VerificationError):
            return False

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    @property
    def is_student(self) -> bool:
        return self.role == 'student'

    def get_avatar_url(self) -> str:
        """Return URL or fallback avatar path."""
        if self.profile_photo:
            return f"/files/avatar/{self.profile_photo}"
        return "/static/img/default-avatar.svg"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'registration_number': self.registration_number,
            'university': self.university,
            'course': self.course,
            'branch': self.branch,
            'semester': self.semester,
            'phone': self.phone,
            'avatar_url': self.get_avatar_url()
        }

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
