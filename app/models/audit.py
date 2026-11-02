from datetime import datetime, timezone
from app import db

class AuditLog(db.Model):
    """
    Security and action audit logs.
    Tracks authentication, medical approvals/rejections, attendance overrides, and suspicious events.
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    target_type = db.Column(db.String(50), nullable=True)  # 'MedicalApplication', 'SubjectAttendance', 'User', etc.
    target_id = db.Column(db.String(50), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), default='INFO', nullable=False) # 'INFO', 'WARNING', 'SECURITY_ALERT'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    @classmethod
    def log(cls, action: str, user_id=None, target_type=None, target_id=None, ip_address=None, user_agent=None, details=None, severity='INFO'):
        try:
            entry = cls(
                user_id=user_id,
                action=action,
                target_type=target_type,
                target_id=str(target_id) if target_id else None,
                ip_address=ip_address,
                user_agent=(user_agent[:250] if user_agent else None),
                details=details,
                severity=severity
            )
            db.session.add(entry)
            db.session.commit()
            return entry
        except Exception:
            db.session.rollback()
            return None

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'System / Anonymous',
            'user_role': self.user.role if self.user else 'N/A',
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'ip_address': self.ip_address,
            'details': self.details,
            'severity': self.severity,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
