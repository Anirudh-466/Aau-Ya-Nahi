from datetime import datetime, date, timezone
from app import db

class SubjectAttendance(db.Model):
    __tablename__ = 'subject_attendances'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', name='uq_student_subject'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, index=True)
    
    total_classes = db.Column(db.Integer, default=0, nullable=False)
    attended_classes = db.Column(db.Integer, default=0, nullable=False)
    medical_classes = db.Column(db.Integer, default=0, nullable=False)  # Officially approved medical hours/classes
    
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def missed_classes(self) -> int:
        return max(0, self.total_classes - self.attended_classes)

    @property
    def regular_percentage(self) -> float:
        if self.total_classes <= 0:
            return 100.0
        return round((self.attended_classes / self.total_classes) * 100, 2)

    @property
    def medical_percentage(self) -> float:
        """Percentage points contributed by medical attendance."""
        if self.total_classes <= 0:
            return 0.0
        return round((self.medical_classes / self.total_classes) * 100, 2)

    def calculate_final_percentage(self, formula_mode='standard_addition', max_benefit=15.0, weight=1.0) -> float:
        """
        Calculate final attendance based on institutional configuration:
        - standard_addition: (Attended + Medical) / Total * 100
        - exemption_subtraction: Attended / (Total - Medical) * 100 (Duty Leave / Medical Exemption)
        - capped_benefit: Regular % + min(Medical %, max_benefit)
        - weighted_benefit: (Attended + (Medical * weight)) / Total * 100
        """
        if self.total_classes <= 0:
            return 100.0

        if formula_mode == 'exemption_subtraction':
            effective_total = max(1, self.total_classes - self.medical_classes)
            pct = (self.attended_classes / effective_total) * 100
        elif formula_mode == 'capped_benefit':
            reg_pct = (self.attended_classes / self.total_classes) * 100
            med_pct = min((self.medical_classes / self.total_classes) * 100, max_benefit)
            pct = reg_pct + med_pct
        elif formula_mode == 'weighted_benefit':
            effective_attended = self.attended_classes + (self.medical_classes * weight)
            pct = (effective_attended / self.total_classes) * 100
        else: # standard_addition default
            pct = ((self.attended_classes + self.medical_classes) / self.total_classes) * 100

        return round(min(100.0, max(0.0, pct)), 2)

    def get_eligibility(self, final_pct: float = None, threshold: float = 75.0, warning_threshold: float = 65.0) -> dict:
        """
        Returns eligibility status dictionary:
        status: 'Safe' | 'Warning' | 'Shortage'
        badge_class: 'badge-safe' | 'badge-warning' | 'badge-danger'
        """
        if final_pct is None:
            final_pct = self.calculate_final_percentage()

        if final_pct >= threshold:
            return {
                'status': 'Safe',
                'badge_class': 'badge-safe',
                'color': '#10b981',
                'description': f'Attendance is above {threshold}%'
            }
        elif final_pct >= warning_threshold:
            return {
                'status': 'Warning',
                'badge_class': 'badge-warning',
                'color': '#f59e0b',
                'description': f'Attendance warning! Between {warning_threshold}% and {threshold}%'
            }
        else:
            return {
                'status': 'Shortage',
                'badge_class': 'badge-danger',
                'color': '#ef4444',
                'description': f'Critical shortage! Below {warning_threshold}%'
            }

    def to_dict(self, formula_mode='standard_addition', max_benefit=15.0, weight=1.0, threshold=75.0, warning_threshold=65.0):
        final_pct = self.calculate_final_percentage(formula_mode, max_benefit, weight)
        eligibility = self.get_eligibility(final_pct, threshold, warning_threshold)
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else '',
            'subject_code': self.subject.code if self.subject else '',
            'faculty_name': self.subject.faculty_name if self.subject else '',
            'credits': self.subject.credits if self.subject else 0,
            'total_classes': self.total_classes,
            'attended_classes': self.attended_classes,
            'missed_classes': self.missed_classes,
            'medical_classes': self.medical_classes,
            'regular_percentage': self.regular_percentage,
            'medical_percentage': self.medical_percentage,
            'final_percentage': final_pct,
            'eligibility': eligibility
        }


class AttendanceRecord(db.Model):
    """Chronological individual class attendance logs."""
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, index=True)
    session_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)  # 'Present', 'Absent', 'Late', 'Medical'
    remarks = db.Column(db.String(255), nullable=True)
    recorded_by = db.Column(db.String(100), default='System')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else '',
            'subject_code': self.subject.code if self.subject else '',
            'session_date': self.session_date.strftime('%Y-%m-%d'),
            'status': self.status,
            'remarks': self.remarks,
            'recorded_by': self.recorded_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }
