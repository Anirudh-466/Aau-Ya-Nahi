import unittest
import io
from app import create_app, db
from app.models.user import User
from app.models.subject import Subject
from app.models.attendance import SubjectAttendance
from app.models.medical import MedicalApplication
from app.models.system_setting import SystemSetting
from app.services.attendance_service import AttendanceService
from app.services.report_service import ReportService

class SmartAttendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        # Create settings
        SystemSetting.set_setting('required_attendance_threshold', '75.0')
        SystemSetting.set_setting('warning_attendance_threshold', '65.0')
        SystemSetting.set_setting('medical_formula_mode', 'standard_addition')
        SystemSetting.set_setting('max_medical_benefit_percent', '15.0')

        # Create Admin
        self.admin = User(
            username='admin_test',
            email='admin@test.com',
            full_name='Admin Tester',
            role='admin'
        )
        self.admin.set_password('AdminTest@123')
        db.session.add(self.admin)

        # Create Student
        self.student = User(
            username='student_test',
            email='student@test.com',
            full_name='Student Tester',
            registration_number='REG1001',
            role='student',
            semester=6
        )
        self.student.set_password('StudentTest@123')
        db.session.add(self.student)

        # Create Subject
        self.subject = Subject(
            code='CS999',
            name='Test Subject',
            semester=6,
            department='CSE',
            credits=4,
            faculty_name='Prof. Test'
        )
        db.session.add(self.subject)
        db.session.commit()

        # Create Attendance
        self.attendance = SubjectAttendance(
            student_id=self.student.id,
            subject_id=self.subject.id,
            total_classes=40,
            attended_classes=26,
            medical_classes=4
        )
        db.session.add(self.attendance)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_argon2_password_hashing(self):
        """Verify Argon2id password hashing and validation."""
        self.assertTrue(self.student.check_password('StudentTest@123'))
        self.assertFalse(self.student.check_password('WrongPassword'))

    def test_attendance_calculations(self):
        """Verify regular, medical, and final percentage calculations."""
        # Conducted: 40, Attended: 26 -> Regular: 26/40 = 65%
        self.assertEqual(self.attendance.regular_percentage, 65.0)
        # Medical: 4/40 = 10%
        self.assertEqual(self.attendance.medical_percentage, 10.0)
        # Standard Addition Final: (26 + 4)/40 = 30/40 = 75%
        final_pct = self.attendance.calculate_final_percentage(formula_mode='standard_addition')
        self.assertEqual(final_pct, 75.0)
        # Eligibility
        eligibility = self.attendance.get_eligibility(final_pct)
        self.assertEqual(eligibility['status'], 'Safe')

    def test_configurable_formulas(self):
        """Verify institutionally configurable medical calculation modes."""
        # 1. Exemption Subtraction: 26 / (40 - 4) = 26 / 36 = 72.22%
        sub_pct = self.attendance.calculate_final_percentage(formula_mode='exemption_subtraction')
        self.assertAlmostEqual(sub_pct, 72.22, places=1)

        # 2. Capped Benefit with cap 5%: 65% + min(10%, 5%) = 70%
        capped_pct = self.attendance.calculate_final_percentage(formula_mode='capped_benefit', max_benefit=5.0)
        self.assertEqual(capped_pct, 70.0)

        # 3. Weighted Benefit with weight 0.5: (26 + 2)/40 = 28/40 = 70%
        weighted_pct = self.attendance.calculate_final_percentage(formula_mode='weighted_benefit', weight=0.5)
        self.assertEqual(weighted_pct, 70.0)

    def test_smart_calculator_service(self):
        """Verify Smart Attendance Calculator logic."""
        res = AttendanceService.run_smart_calculator(
            total=40,
            attended=26,
            medical=4,
            upcoming=10,
            target_pct=75.0
        )
        self.assertEqual(res['regular_pct'], 65.0)
        self.assertEqual(res['adjusted_pct'], 75.0)
        # Target is 75%, currently at 75%, so required additional classes = 0
        self.assertEqual(res['required_classes_to_reach_target'], 0)
        self.assertTrue(res['is_currently_safe'])

    def test_recovery_calculator_when_shortage(self):
        """Verify required classes to recover from shortage."""
        # Total: 40, Attended: 20, Medical: 0 -> 50%
        # Target: 75%
        # Formula: (20 + x) / (40 + x) >= 0.75 => 20 + x >= 30 + 0.75x => 0.25x >= 10 => x >= 40 classes!
        needed = AttendanceService.calculate_required_classes(
            total=40,
            attended=20,
            medical=0,
            target_pct=75.0,
            formula_mode='standard_addition'
        )
        self.assertEqual(needed, 40)

    def test_pdf_report_generation(self):
        """Verify ReportLab PDF stream generation succeeds."""
        pdf_buffer = ReportService.generate_student_pdf(self.student)
        self.assertIsInstance(pdf_buffer, io.BytesIO)
        pdf_content = pdf_buffer.getvalue()
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_unauthorized_admin_access(self):
        """Verify students cannot access admin pages."""
        # Login as student
        with self.client:
            self.client.post('/auth/login', data={
                'identity': 'student_test',
                'password': 'StudentTest@123'
            })
            resp = self.client.get('/admin/dashboard')
            self.assertEqual(resp.status_code, 403)

if __name__ == '__main__':
    unittest.main()
