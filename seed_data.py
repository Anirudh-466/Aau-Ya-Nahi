"""
SmartAttend Database Seeder
Populates realistic demo accounts, subjects, attendance logs, and certified medical requests.
"""

import os
from datetime import datetime, date, timedelta, timezone
from app import create_app, db
from app.models.user import User
from app.models.subject import Subject
from app.models.attendance import SubjectAttendance, AttendanceRecord
from app.models.medical import MedicalApplication
from app.models.system_setting import SystemSetting
from app.models.audit import AuditLog

def create_sample_certificate(filepath: str, student_name: str, app_number: str):
    """Creates a sample dummy medical certificate PNG if it doesn't already exist."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        from PIL import Image, ImageDraw
        # Create a simple clean medical certificate graphic
        img = Image.new('RGB', (800, 600), color='#ffffff')
        draw = ImageDraw.Draw(img)
        # Border
        draw.rectangle([(20, 20), (780, 580)], outline='#4f46e5', width=3)
        draw.rectangle([(30, 30), (770, 570)], outline='#06b6d4', width=1)
        # Header banner
        draw.rectangle([(30, 30), (770, 110)], fill='#f0f4f9')
        # We can draw simulated lines/text
        draw.text((220, 50), "METROPOLITAN HOSPITAL & HEALTHCARE", fill='#0f172a')
        draw.text((250, 80), "OFFICIAL MEDICAL CERTIFICATE & DISCHARGE SUMMARY", fill='#4f46e5')
        draw.text((60, 150), f"Document Ref: {app_number}", fill='#64748b')
        draw.text((60, 190), f"This is to certify that: {student_name}", fill='#0f172a')
        draw.text((60, 230), "Was evaluated and treated under medical supervision.", fill='#0f172a')
        draw.text((60, 270), "Diagnosis: Acute Viral Gastroenteritis & High Pyrexia", fill='#0f172a')
        draw.text((60, 310), "Medical Recommendation: Complete bed rest and fluid recovery.", fill='#0f172a')
        draw.text((60, 350), "Status: Clinically verified by authorized physician.", fill='#059669')
        # Doctor signature placeholder
        draw.line([(500, 500), (720, 500)], fill='#0f172a', width=2)
        draw.text((520, 510), "Dr. Marcus Vance, M.D.", fill='#0f172a')
        draw.text((520, 530), "Chief Medical Officer", fill='#64748b')

        img.save(filepath, 'PNG')

def seed_database():
    app = create_app('development')
    with app.app_context():
        print("Resetting and recreating database tables...")
        db.drop_all()
        db.create_all()

        print("Creating system settings...")
        SystemSetting.set_setting('required_attendance_threshold', '75.0', 'Required minimum attendance %')
        SystemSetting.set_setting('warning_attendance_threshold', '65.0', 'Warning attendance trigger %')
        SystemSetting.set_setting('medical_formula_mode', 'standard_addition', 'Institutional medical calculation method')
        SystemSetting.set_setting('max_medical_benefit_percent', '15.0', 'Maximum attendance boost allowed from medical leaves')
        SystemSetting.set_setting('medical_weight', '1.0', 'Weight multiplier for medical hours')
        SystemSetting.set_setting('max_medical_days_allowed', '30', 'Max medically excused days per semester')
        SystemSetting.set_setting('semester_name', 'Spring Semester 2026', 'Academic Semester Title')
        SystemSetting.set_setting('university_name', 'SmartAttend Institute of Science & Technology', 'Institution Name')

        print("Creating administrative accounts...")
        admin = User(
            username='admin',
            email='admin@smartattend.edu',
            full_name='Dr. Arthur Vance',
            role='admin',
            registration_number='ADM-2026-001',
            university='SmartAttend Institute of Science & Technology',
            course='Faculty Administration',
            branch='Dean of Student Affairs',
            semester=6
        )
        admin.set_password('Admin@12345')
        db.session.add(admin)

        print("Creating subjects...")
        subjects_data = [
            {'code': 'CS601', 'name': 'Operating Systems', 'credits': 4, 'faculty': 'Prof. David Miller', 'dept': 'Computer Science'},
            {'code': 'CS602', 'name': 'Java Programming & Enterprise Tech', 'credits': 4, 'faculty': 'Dr. Samantha Reed', 'dept': 'Computer Science'},
            {'code': 'CS603', 'name': 'Database Management Systems', 'credits': 4, 'faculty': 'Prof. Robert Taylor', 'dept': 'Computer Science'},
            {'code': 'MA601', 'name': 'Applied Mathematics & Statistics', 'credits': 3, 'faculty': 'Dr. Elena Rostova', 'dept': 'Mathematics'},
            {'code': 'CS604', 'name': 'Machine Learning & Predictive Models', 'credits': 4, 'faculty': 'Dr. Alan Turing Jr.', 'dept': 'Artificial Intelligence'},
            {'code': 'CS605', 'name': 'Computer Networks & Security Protocols', 'credits': 4, 'faculty': 'Prof. Michael Hastings', 'dept': 'Information Technology'}
        ]

        created_subjects = []
        for s in subjects_data:
            sub = Subject(
                code=s['code'],
                name=s['name'],
                semester=6,
                department=s['dept'],
                credits=s['credits'],
                faculty_name=s['faculty'],
                description=f"Core curriculum for Semester 6 covering theory and practical lab implementation of {s['name']}."
            )
            db.session.add(sub)
            created_subjects.append(sub)

        db.session.commit()

        print("Creating students...")
        # 1. Main Student Alex Morgan
        alex = User(
            username='alexmorgan',
            email='alex.morgan@smartattend.edu',
            full_name='Alex Morgan',
            role='student',
            registration_number='RA2111003010042',
            university='SmartAttend Institute of Science & Technology',
            course='B.Tech',
            branch='Computer Science & Engineering',
            semester=6,
            phone='+1 (555) 234-8901'
        )
        alex.set_password('Student@12345')
        db.session.add(alex)

        # 2. High attendance student Sarah Chen
        sarah = User(
            username='sarahchen',
            email='sarah.chen@smartattend.edu',
            full_name='Sarah Chen',
            role='student',
            registration_number='RA2111003010088',
            university='SmartAttend Institute of Science & Technology',
            course='B.Tech',
            branch='Computer Science & Engineering',
            semester=6,
            phone='+1 (555) 345-6789'
        )
        sarah.set_password('Student@12345')
        db.session.add(sarah)

        # 3. Student with shortage warning Raj Patel
        raj = User(
            username='rajpatel',
            email='raj.patel@smartattend.edu',
            full_name='Raj Patel',
            role='student',
            registration_number='RA2111003010115',
            university='SmartAttend Institute of Science & Technology',
            course='B.Tech',
            branch='Computer Science & Engineering',
            semester=6,
            phone='+1 (555) 456-7890'
        )
        raj.set_password('Student@12345')
        db.session.add(raj)

        db.session.commit()

        print("Setting up subject attendance balances for Alex Morgan...")
        # Alex Morgan balances (Matches the prompt's exact scenario)
        alex_balances = [
            # CS601 Operating Systems: 60 conducted, 44 attended, 8 medical -> Reg: 73.3%, Med: 13.3%, Final: 86.7%
            {'code': 'CS601', 'total': 60, 'attended': 44, 'medical': 8},
            # CS602 Java: 50 conducted, 35 attended, 5 medical -> Reg: 70%, Med: 10%, Final: 80%
            {'code': 'CS602', 'total': 50, 'attended': 35, 'medical': 5},
            # CS603 DBMS: 40 conducted, 26 attended, 6 medical -> Reg: 65%, Med: 15%, Final: 80%
            {'code': 'CS603', 'total': 40, 'attended': 26, 'medical': 6},
            # MA601 Mathematics: 45 conducted, 32 attended, 4 medical -> Reg: 71.1%, Med: 8.9%, Final: 80%
            {'code': 'MA601', 'total': 45, 'attended': 32, 'medical': 4},
            # CS604 Machine Learning: 50 conducted, 34 attended, 7 medical -> Reg: 68%, Med: 14%, Final: 82%
            {'code': 'CS604', 'total': 50, 'attended': 34, 'medical': 7},
            # CS605 Computer Networks: 48 conducted, 28 attended, 2 medical -> Reg: 58.3%, Med: 4.2%, Final: 62.5% (Shortage!)
            {'code': 'CS605', 'total': 48, 'attended': 28, 'medical': 2}
        ]

        sub_map = {s.code: s for s in created_subjects}
        for b in alex_balances:
            sub = sub_map[b['code']]
            att = SubjectAttendance(
                student_id=alex.id,
                subject_id=sub.id,
                total_classes=b['total'],
                attended_classes=b['attended'],
                medical_classes=b['medical']
            )
            db.session.add(att)

        # Balances for Sarah Chen (Safe student)
        for s in created_subjects:
            att = SubjectAttendance(
                student_id=sarah.id,
                subject_id=s.id,
                total_classes=50,
                attended_classes=44,
                medical_classes=3
            )
            db.session.add(att)

        # Balances for Raj Patel (Warning/Shortage student)
        for s in created_subjects:
            att = SubjectAttendance(
                student_id=raj.id,
                subject_id=s.id,
                total_classes=50,
                attended_classes=31,
                medical_classes=2
            )
            db.session.add(att)

        db.session.commit()

        print("Generating realistic sample medical certificates & applications...")
        med_folder = app.config['MEDICAL_UPLOAD_FOLDER']
        
        # Medical App 1: Approved - OS
        file1 = f"med_{alex.id}_os_cert.png"
        create_sample_certificate(os.path.join(med_folder, file1), alex.full_name, "MED-2026-A101")
        med1 = MedicalApplication(
            application_number="MED-2026-A101",
            student_id=alex.id,
            subject_id=sub_map['CS601'].id,
            start_date=date.today() - timedelta(days=40),
            end_date=date.today() - timedelta(days=34),
            requested_classes=8,
            approved_classes=8,
            reason="Acute gastroenteritis and dehydration. Advised bed rest by hospital resident.",
            certificate_filename=file1,
            certificate_original_name="Hospital_Medical_Discharge_Slip.png",
            certificate_mimetype="image/png",
            status="Approved",
            admin_remarks="Verified physician stamp and medical center registry.",
            reviewed_by=admin.id,
            reviewed_at=datetime.now(timezone.utc) - timedelta(days=33)
        )
        db.session.add(med1)

        # Medical App 2: Approved - Java
        file2 = f"med_{alex.id}_java_cert.png"
        create_sample_certificate(os.path.join(med_folder, file2), alex.full_name, "MED-2026-A102")
        med2 = MedicalApplication(
            application_number="MED-2026-A102",
            student_id=alex.id,
            subject_id=sub_map['CS602'].id,
            start_date=date.today() - timedelta(days=25),
            end_date=date.today() - timedelta(days=21),
            requested_classes=5,
            approved_classes=5,
            reason="High grade viral pyrexia and weakness.",
            certificate_filename=file2,
            certificate_original_name="Clinic_Prescription_BedRest.png",
            certificate_mimetype="image/png",
            status="Approved",
            admin_remarks="Approved according to standard attendance waiver rules.",
            reviewed_by=admin.id,
            reviewed_at=datetime.now(timezone.utc) - timedelta(days=20)
        )
        db.session.add(med2)

        # Medical App 3: Approved - DBMS
        file3 = f"med_{alex.id}_dbms_cert.png"
        create_sample_certificate(os.path.join(med_folder, file3), alex.full_name, "MED-2026-A103")
        med3 = MedicalApplication(
            application_number="MED-2026-A103",
            student_id=alex.id,
            subject_id=sub_map['CS603'].id,
            start_date=date.today() - timedelta(days=18),
            end_date=date.today() - timedelta(days=13),
            requested_classes=6,
            approved_classes=6,
            reason="Orthopedic ankle sprain treatment and physical therapy.",
            certificate_filename=file3,
            certificate_original_name="Orthopedic_Certificate.png",
            certificate_mimetype="image/png",
            status="Approved",
            admin_remarks="Verified physiotherapy certificate.",
            reviewed_by=admin.id,
            reviewed_at=datetime.now(timezone.utc) - timedelta(days=12)
        )
        db.session.add(med3)

        # Medical App 4: Pending - Computer Networks (Ready for Admin to test approve/reject!)
        file4 = f"med_{alex.id}_cn_cert.png"
        create_sample_certificate(os.path.join(med_folder, file4), alex.full_name, "MED-2026-0042")
        med4 = MedicalApplication(
            application_number="MED-2026-0042",
            student_id=alex.id,
            subject_id=sub_map['CS605'].id,
            start_date=date.today() - timedelta(days=4),
            end_date=date.today() - timedelta(days=1),
            requested_classes=4,
            approved_classes=0,
            reason="Severe respiratory tract infection and laryngitis. Doctor advised 4 days recuperation.",
            certificate_filename=file4,
            certificate_original_name="Medical_Certificate_Laryngitis.png",
            certificate_mimetype="image/png",
            status="Pending",
            admin_remarks=None
        )
        db.session.add(med4)

        # Medical App 5: Rejected sample for audit demonstration
        file5 = f"med_{alex.id}_math_cert.png"
        create_sample_certificate(os.path.join(med_folder, file5), alex.full_name, "MED-2026-R099")
        med5 = MedicalApplication(
            application_number="MED-2026-R099",
            student_id=alex.id,
            subject_id=sub_map['MA601'].id,
            start_date=date.today() - timedelta(days=50),
            end_date=date.today() - timedelta(days=48),
            requested_classes=3,
            approved_classes=0,
            reason="Headache and minor fatigue.",
            certificate_filename=file5,
            certificate_original_name="Doctor_Note_Minor.png",
            certificate_mimetype="image/png",
            status="Rejected",
            admin_remarks="Insufficient documentation: Missing official hospital seal and diagnostic slip.",
            reviewed_by=admin.id,
            reviewed_at=datetime.now(timezone.utc) - timedelta(days=47)
        )
        db.session.add(med5)

        db.session.commit()

        print("Generating individual chronological attendance session logs...")
        # Create past 30 days of lecture logs
        today = date.today()
        for i in range(25, -1, -1):
            session_date = today - timedelta(days=i)
            # Skip weekends
            if session_date.weekday() >= 5:
                continue

            for sub in created_subjects:
                # Randomize mostly Present with some Absent and Medical
                day_offset = (i + sub.id) % 7
                if day_offset == 0:
                    status = 'Absent'
                    remarks = 'Unexcused absence'
                elif day_offset == 1 and sub.code == 'CS601':
                    status = 'Medical'
                    remarks = 'Medically excused by department'
                elif day_offset == 2 and sub.code == 'CS605':
                    status = 'Late'
                    remarks = 'Arrived 10 mins late'
                else:
                    status = 'Present'
                    remarks = 'Regular session completed'

                rec = AttendanceRecord(
                    student_id=alex.id,
                    subject_id=sub.id,
                    session_date=session_date,
                    status=status,
                    remarks=remarks,
                    recorded_by=sub.faculty_name
                )
                db.session.add(rec)

        print("Adding sample security audit logs...")
        AuditLog.log(
            action='SYSTEM_INITIALIZATION',
            user_id=admin.id,
            ip_address='127.0.0.1',
            details='SmartAttend database schema and parameters seeded successfully.'
        )
        AuditLog.log(
            action='LOGIN_SUCCESS',
            user_id=alex.id,
            ip_address='192.168.1.45',
            details=f"Student {alex.username} logged into student dashboard."
        )
        AuditLog.log(
            action='MEDICAL_APPLICATION_SUBMITTED',
            user_id=alex.id,
            target_type='MedicalApplication',
            target_id=med4.id,
            ip_address='192.168.1.45',
            details=f"Application {med4.application_number} submitted for CS605."
        )

        db.session.commit()
        print("\n=======================================================")
        print(" SmartAttend Database Seeded Successfully! ")
        print("=======================================================")
        print("DEMO CREDENTIALS:")
        print("  1. Student Portal: alex.morgan@smartattend.edu / Student@12345")
        print("     Roll Number:    RA2111003010042")
        print("  2. Admin Portal:   admin@smartattend.edu / Admin@12345")
        print("=======================================================\n")

if __name__ == '__main__':
    seed_database()
