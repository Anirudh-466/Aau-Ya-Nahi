from datetime import datetime, date, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, Response
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models.user import User
from app.models.subject import Subject
from app.models.attendance import SubjectAttendance, AttendanceRecord
from app.models.medical import MedicalApplication
from app.models.system_setting import SystemSetting
from app.models.audit import AuditLog
from app.forms.admin_forms import SubjectForm, AttendanceOverrideForm, MedicalReviewForm, SystemSettingsForm
from app.forms.auth_forms import StudentRegisterForm
from app.services.security_service import admin_required
from app.services.attendance_service import AttendanceService
from app.services.report_service import ReportService

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_students = User.query.filter_by(role='student').count()
    total_subjects = Subject.query.filter_by(is_active=True).count()
    pending_medical = MedicalApplication.query.filter_by(status='Pending').count()
    
    # Recent pending applications
    pending_apps = MedicalApplication.query.filter_by(status='Pending').order_by(MedicalApplication.created_at.desc()).limit(10).all()
    
    # Recent audit logs
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(8).all()

    # Shortage calculations
    settings = SystemSetting.get_all_settings()
    threshold = settings.get('required_attendance_threshold', 75.0)
    
    all_student_attendances = SubjectAttendance.query.all()
    shortage_count = 0
    for att in all_student_attendances:
        if att.calculate_final_percentage() < threshold:
            shortage_count += 1

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_subjects=total_subjects,
        pending_medical=pending_medical,
        shortage_count=shortage_count,
        pending_apps=pending_apps,
        recent_logs=recent_logs,
        settings=settings
    )


@admin_bp.route('/medical-requests', methods=['GET', 'POST'])
@login_required
@admin_required
def medical_requests():
    form = MedicalReviewForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        app_id = form.application_id.data
        med_app = MedicalApplication.query.get_or_404(int(app_id))
        
        decision = form.action.data
        approved_count = form.approved_classes.data if decision == 'Approved' else 0
        remarks = form.admin_remarks.data.strip() if form.admin_remarks.data else ''

        med_app.status = decision
        med_app.approved_classes = approved_count
        med_app.admin_remarks = remarks
        med_app.reviewed_by = current_user.id
        med_app.reviewed_at = datetime.now(timezone.utc)

        # Update student's subject attendance balance
        att = SubjectAttendance.query.filter_by(
            student_id=med_app.student_id,
            subject_id=med_app.subject_id
        ).first()

        if att:
            # Recalculate total approved medical classes for this student and subject
            all_approved = MedicalApplication.query.filter_by(
                student_id=med_app.student_id,
                subject_id=med_app.subject_id,
                status='Approved'
            ).all()
            # If current is approved, count it
            total_approved_med = sum(a.approved_classes for a in all_approved)
            if decision == 'Approved' and med_app not in all_approved:
                total_approved_med += approved_count
            elif decision != 'Approved' and med_app in all_approved:
                total_approved_med -= med_app.approved_classes
                
            att.medical_classes = max(0, total_approved_med)

        # Log an official attendance record entry
        if decision == 'Approved':
            rec = AttendanceRecord(
                student_id=med_app.student_id,
                subject_id=med_app.subject_id,
                session_date=med_app.start_date,
                status='Medical',
                remarks=f"Medically approved: {med_app.application_number} ({approved_count} classes)",
                recorded_by=current_user.full_name
            )
            db.session.add(rec)

        db.session.commit()

        # Audit log
        AuditLog.log(
            action=f"MEDICAL_APPLICATION_{decision.upper()}",
            user_id=current_user.id,
            target_type='MedicalApplication',
            target_id=med_app.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Admin {current_user.username} {decision.lower()} application {med_app.application_number} ({approved_count} classes approved). Remarks: {remarks}"
        )

        flash(f"Application {med_app.application_number} has been {decision.lower()} successfully.", 'success')
        return redirect(url_for('admin.medical_requests'))

    # Filtering
    status_filter = request.args.get('status', 'Pending')
    query = MedicalApplication.query
    if status_filter in ('Pending', 'Approved', 'Rejected'):
        query = query.filter_by(status=status_filter)
    
    applications = query.order_by(MedicalApplication.created_at.desc()).all()
    
    return render_template(
        'admin/medical_review.html',
        applications=applications,
        status_filter=status_filter,
        form=form
    )


@admin_bp.route('/subjects', methods=['GET', 'POST'])
@login_required
@admin_required
def subjects():
    form = SubjectForm()
    if form.validate_on_submit():
        existing = Subject.query.filter_by(code=form.code.data.strip().upper()).first()
        if existing:
            flash(f"A subject with code {form.code.data} already exists.", 'danger')
        else:
            sub = Subject(
                code=form.code.data.strip().upper(),
                name=form.name.data.strip(),
                semester=form.semester.data,
                department=form.department.data.strip(),
                credits=form.credits.data,
                faculty_name=form.faculty_name.data.strip(),
                description=form.description.data.strip() if form.description.data else None
            )
            db.session.add(sub)
            db.session.commit()

            # Auto-enroll existing students of that semester
            students = User.query.filter_by(role='student', semester=sub.semester).all()
            for st in students:
                att = SubjectAttendance(student_id=st.id, subject_id=sub.id, total_classes=0, attended_classes=0, medical_classes=0)
                db.session.add(att)
            db.session.commit()

            AuditLog.log(
                action='SUBJECT_CREATED',
                user_id=current_user.id,
                target_type='Subject',
                target_id=sub.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details=f"Created subject {sub.code}: {sub.name}"
            )
            flash(f"Subject '{sub.name}' ({sub.code}) added successfully!", 'success')
            return redirect(url_for('admin.subjects'))

    all_subjects = Subject.query.order_by(Subject.semester, Subject.code).all()
    return render_template('admin/subjects.html', subjects=all_subjects, form=form)


@admin_bp.route('/subjects/toggle/<int:subject_id>', methods=['POST'])
@login_required
@admin_required
def toggle_subject(subject_id):
    sub = Subject.query.get_or_404(subject_id)
    sub.is_active = not sub.is_active
    db.session.commit()
    status_str = "activated" if sub.is_active else "deactivated"
    flash(f"Subject {sub.code} has been {status_str}.", 'info')
    return redirect(url_for('admin.subjects'))


@admin_bp.route('/students', methods=['GET', 'POST'])
@login_required
@admin_required
def students():
    form = StudentRegisterForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            registration_number=form.registration_number.data.strip().upper(),
            email=form.email.data.strip().lower(),
            username=form.username.data.strip().lower(),
            course=form.course.data,
            branch=form.branch.data,
            semester=form.semester.data,
            role='student'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Enroll in subjects
        subjects = Subject.query.filter_by(semester=user.semester, is_active=True).all()
        for sub in subjects:
            att = SubjectAttendance(student_id=user.id, subject_id=sub.id)
            db.session.add(att)
        db.session.commit()

        flash(f"Student {user.full_name} registered successfully!", 'success')
        return redirect(url_for('admin.students'))

    search = request.args.get('q', '').strip()
    query = User.query.filter_by(role='student')
    if search:
        query = query.filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.registration_number.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    student_list = query.order_by(User.full_name).all()
    return render_template('admin/students.html', students=student_list, form=form, search=search)


@admin_bp.route('/attendance', methods=['GET', 'POST'])
@login_required
@admin_required
def attendance_management():
    form = AttendanceOverrideForm()

    if request.method == 'POST' and form.validate_on_submit():
        st_id = int(form.student_id.data)
        sub_id = int(form.subject_id.data)
        total = form.total_classes.data
        attended = form.attended_classes.data
        medical = form.medical_classes.data
        remarks = form.remarks.data

        if attended > total:
            flash("Attended classes cannot exceed total classes conducted.", "danger")
            return redirect(url_for('admin.attendance_management', student_id=st_id))

        att = SubjectAttendance.query.filter_by(student_id=st_id, subject_id=sub_id).first()
        if not att:
            att = SubjectAttendance(student_id=st_id, subject_id=sub_id)
            db.session.add(att)

        old_total = att.total_classes
        old_att = att.attended_classes
        old_med = att.medical_classes

        att.total_classes = total
        att.attended_classes = attended
        att.medical_classes = medical

        db.session.commit()

        AuditLog.log(
            action='ATTENDANCE_OVERRIDE',
            user_id=current_user.id,
            target_type='SubjectAttendance',
            target_id=att.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Admin updated Student ID {st_id}, Subject ID {sub_id}: Total={old_total}->{total}, Attended={old_att}->{attended}, Medical={old_med}->{medical}. Note: {remarks}",
            severity='WARNING'
        )

        flash("Attendance record updated officially.", "success")
        return redirect(url_for('admin.attendance_management', student_id=st_id))

    # Selected student
    selected_student_id = request.args.get('student_id', type=int)
    all_students = User.query.filter_by(role='student').order_by(User.full_name).all()
    
    selected_student = None
    student_attendances = []
    if selected_student_id:
        selected_student = User.query.get(selected_student_id)
        if selected_student:
            student_attendances = SubjectAttendance.query.filter_by(student_id=selected_student.id).all()
    elif all_students:
        selected_student = all_students[0]
        student_attendances = SubjectAttendance.query.filter_by(student_id=selected_student.id).all()

    return render_template(
        'admin/attendance_mgmt.html',
        students=all_students,
        selected_student=selected_student,
        attendances=student_attendances,
        form=form
    )


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    form = SystemSettingsForm()
    current_settings = SystemSetting.get_all_settings()

    if request.method == 'GET':
        form.required_attendance_threshold.data = current_settings.get('required_attendance_threshold', 75.0)
        form.warning_attendance_threshold.data = current_settings.get('warning_attendance_threshold', 65.0)
        form.medical_formula_mode.data = current_settings.get('medical_formula_mode', 'standard_addition')
        form.max_medical_benefit_percent.data = current_settings.get('max_medical_benefit_percent', 15.0)
        form.medical_weight.data = current_settings.get('medical_weight', 1.0)
        form.max_medical_days_allowed.data = current_settings.get('max_medical_days_allowed', 30)
        form.semester_name.data = current_settings.get('semester_name', 'Spring Semester 2026')
        form.university_name.data = current_settings.get('university_name', 'SmartAttend Institute of Science & Technology')

    if form.validate_on_submit():
        SystemSetting.set_setting('required_attendance_threshold', form.required_attendance_threshold.data, 'Required minimum attendance %')
        SystemSetting.set_setting('warning_attendance_threshold', form.warning_attendance_threshold.data, 'Attendance warning trigger threshold %')
        SystemSetting.set_setting('medical_formula_mode', form.medical_formula_mode.data, 'Institutional medical attendance formula algorithm')
        SystemSetting.set_setting('max_medical_benefit_percent', form.max_medical_benefit_percent.data, 'Maximum attendance % boost from medical claims')
        SystemSetting.set_setting('medical_weight', form.medical_weight.data, 'Weight factor for medical hours')
        SystemSetting.set_setting('max_medical_days_allowed', form.max_medical_days_allowed.data, 'Max medically excused days per semester')
        SystemSetting.set_setting('semester_name', form.semester_name.data, 'Current academic semester')
        SystemSetting.set_setting('university_name', form.university_name.data, 'Official institution title')

        AuditLog.log(
            action='SYSTEM_SETTINGS_UPDATED',
            user_id=current_user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Updated attendance formula to: {form.medical_formula_mode.data}, threshold: {form.required_attendance_threshold.data}%",
            severity='WARNING'
        )

        flash('Institutional system settings updated successfully! Attendance percentages recalculate dynamically according to the new formula.', 'success')
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', form=form, settings=current_settings)


@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    severity = request.args.get('severity')
    query = AuditLog.query
    if severity:
        query = query.filter_by(severity=severity)
    
    logs = query.order_by(AuditLog.created_at.desc()).limit(150).all()
    return render_template('admin/audit_logs.html', logs=logs, selected_severity=severity)


@admin_bp.route('/export/csv')
@login_required
@admin_required
def export_csv():
    csv_stream = ReportService.generate_admin_attendance_csv()
    
    AuditLog.log(
        action='ADMIN_EXPORT_CSV',
        user_id=current_user.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details="Admin exported complete attendance CSV dataset"
    )

    return Response(
        csv_stream.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=SmartAttend_Master_Attendance_{date.today().strftime('%Y%m%d')}.csv"}
    )


@admin_bp.route('/export/pdf/<int:student_id>')
@login_required
@admin_required
def export_student_pdf(student_id):
    student = User.query.get_or_404(student_id)
    pdf_buffer = ReportService.generate_student_pdf(student)
    
    AuditLog.log(
        action='ADMIN_EXPORT_STUDENT_PDF',
        user_id=current_user.id,
        target_type='User',
        target_id=student.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details=f"Admin generated PDF report for student {student.registration_number}"
    )

    filename = f"SmartAttend_Report_{student.registration_number or student.username}.pdf"
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
