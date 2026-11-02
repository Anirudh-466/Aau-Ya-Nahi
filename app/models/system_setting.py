from datetime import datetime, timezone
from app import db

class SystemSetting(db.Model):
    """
    Persistent system configurations configurable by Admin.
    Controls attendance thresholds and medical attendance formulas.
    """
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    setting_value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @classmethod
    def get_setting(cls, key: str, default=None):
        row = cls.query.filter_by(setting_key=key).first()
        if row:
            return row.setting_value
        return default

    @classmethod
    def set_setting(cls, key: str, value: str, description: str = None):
        row = cls.query.filter_by(setting_key=key).first()
        if not row:
            row = cls(setting_key=key, setting_value=str(value), description=description)
            db.session.add(row)
        else:
            row.setting_value = str(value)
            if description:
                row.description = description
        db.session.commit()
        return row

    @classmethod
    def get_all_settings(cls) -> dict:
        """Returns all system settings with type-casted values."""
        defaults = {
            'required_attendance_threshold': 75.0,
            'warning_attendance_threshold': 65.0,
            'medical_formula_mode': 'standard_addition', # 'standard_addition', 'exemption_subtraction', 'capped_benefit', 'weighted_benefit'
            'max_medical_benefit_percent': 15.0,
            'medical_weight': 1.0,
            'semester_name': 'Spring Semester 2026',
            'university_name': 'SmartAttend Institute of Science & Technology',
            'max_medical_days_allowed': 30
        }
        rows = cls.query.all()
        result = dict(defaults)
        for r in rows:
            if r.setting_key in ('required_attendance_threshold', 'warning_attendance_threshold', 'max_medical_benefit_percent', 'medical_weight'):
                try:
                    result[r.setting_key] = float(r.setting_value)
                except ValueError:
                    pass
            elif r.setting_key in ('max_medical_days_allowed',):
                try:
                    result[r.setting_key] = int(r.setting_value)
                except ValueError:
                    pass
            else:
                result[r.setting_key] = r.setting_value
        return result
