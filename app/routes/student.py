from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from app import db
from app.models.subject import Subject
from app.models.attendance import SubjectAttendance, AttendanceRecord
from app.models.medical import MedicalApplication
from app.models.system_setting import SystemSetting
from app.models.audit import AuditLog
from app.forms.medical_forms import MedicalApplicationForm
from app.forms.profile_forms import ProfileForm
from app.forms.auth_forms import PasswordChangeForm
from app.services.security_service import student_required, save_secure_file
from app.services.attendance_service import AttendanceService
from app.services.report_service import ReportService

student_bp = Blueprint('student', __name__)

@student_bp.route('/')
@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    data = AttendanceService.get_student_dashboard_data(current_user.id)
    
    # Recent medical applications for the side panel status feed
    recent_medical_apps = MedicalApplication.query.filter_by(
        student_id=current_user.id
    ).order_by(MedicalApplication.created_at.desc()).limit(5).all()

    # Form instance for inline modal "Add Medical Record"
    med_form = MedicalApplicationForm()
    # Populate subjects dropdown
    student_subjects = SubjectAttendance.query.filter_by(student_id=current_user.id).all()
    med_form.subject_id.choices = [(s.subject.id, f"{s.subject.code} - {s.subject.name}") for s in student_subjects if s.subject]

    return render_template(
        'student/dashboard.html',
        student=current_user,
        data=data,
        recent_medical_apps=recent_medical_apps,
        med_form=med_form
    )


@student_bp.route('/my-attendance')
@login_required
@student_required
def my_attendance():
    data = AttendanceService.get_student_dashboard_data(current_user.id)
    
    # Chronological history logs
    subject_id = request.args.get('subject_id', type=int)
    query = AttendanceRecord.query.filter_by(student_id=current_user.id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    
    records = query.order_by(AttendanceRecord.session_date.desc()).limit(100).all()
    all_subjects = SubjectAttendance.query.filter_by(student_id=current_user.id).all()

    return render_template(
        'student/my_attendance.html',
        student=current_user,
        data=data,
        records=records,
        all_subjects=all_subjects,
        selected_subject_id=subject_id
    )


@student_bp.route('/medical-attendance', methods=['GET', 'POST'])
@login_required
@student_required
def medical_attendance():
    form = MedicalApplicationForm()
    # Populate subjects dropdown
    student_subjects = SubjectAttendance.query.filter_by(student_id=current_user.id).all()
    form.subject_id.choices = [(s.subject.id, f"{s.subject.code} - {s.subject.name}") for s in student_subjects if s.subject]

    if form.validate_on_submit():
        # Secure file saving
        cert_file = form.certificate.data
        upload_folder = current_app.config['MEDICAL_UPLOAD_FOLDER']
        
        stored_filename, original_name, file_size, mimetype = save_secure_file(
            cert_file,
            target_folder=upload_folder,
            prefix=f"med_{current_user.id}"
        )

        app_num = MedicalApplication.generate_app_number()
        med_app = MedicalApplication(
            application_number=app_num,
            student_id=current_user.id,
            subject_id=form.subject_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            requested_classes=form.requested_classes.data,
            approved_classes=0, # Must be verified by admin
            reason=form.reason.data.strip(),
            certificate_filename=stored_filename,
            certificate_original_name=original_name,
            certificate_mimetype=mimetype,
            certificate_size=file_size,
            status='Pending',
            is_locked=True
        )
        db.session.add(med_app)
        db.session.commit()

        AuditLog.log(
            action='MEDICAL_APPLICATION_SUBMITTED',
            user_id=current_user.id,
            target_type='MedicalApplication',
            target_id=med_app.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Medical claim submitted: {app_num} for subject ID {med_app.subject_id} ({med_app.requested_classes} classes)"
        )

        flash(f'Medical attendance application {app_num} submitted successfully! Our administrative team will verify your certificate.', 'success')
        return redirect(url_for('student.medical_attendance'))

    # All student medical applications
    applications = MedicalApplication.query.filter_by(
        student_id=current_user.id
    ).order_by(MedicalApplication.created_at.desc()).all()

    data = AttendanceService.get_student_dashboard_data(current_user.id)

    return render_template(
        'student/medical.html',
        student=current_user,
        form=form,
        applications=applications,
        data=data
    )


@student_bp.route('/calculator')
@login_required
@student_required
def calculator():
    data = AttendanceService.get_student_dashboard_data(current_user.id)
    return render_template(
        'student/calculator.html',
        student=current_user,
        data=data
    )


@student_bp.route('/subject/<int:subject_id>')
@login_required
@student_required
def subject_detail(subject_id):
    att = SubjectAttendance.query.filter_by(student_id=current_user.id, subject_id=subject_id).first_or_404()
    settings = SystemSetting.get_all_settings()
    sub_dict = att.to_dict(
        formula_mode=settings.get('medical_formula_mode', 'standard_addition'),
        max_benefit=settings.get('max_medical_benefit_percent', 15.0),
        weight=settings.get('medical_weight', 1.0),
        threshold=settings.get('required_attendance_threshold', 75.0),
        warning_threshold=settings.get('warning_attendance_threshold', 65.0)
    )

    records = AttendanceRecord.query.filter_by(
        student_id=current_user.id, subject_id=subject_id
    ).order_by(AttendanceRecord.session_date.desc()).all()

    medical_apps = MedicalApplication.query.filter_by(
        student_id=current_user.id, subject_id=subject_id
    ).order_by(MedicalApplication.created_at.desc()).all()

    calc_projection = AttendanceService.run_smart_calculator(
        total=att.total_classes,
        attended=att.attended_classes,
        medical=att.medical_classes,
        target_pct=settings.get('required_attendance_threshold', 75.0)
    )

    return render_template(
        'student/subject_detail.html',
        student=current_user,
        attendance=att,
        subject_info=sub_dict,
        records=records,
        medical_apps=medical_apps,
        calc=calc_projection
    )


@student_bp.route('/reports')
@login_required
@student_required
def reports():
    data = AttendanceService.get_student_dashboard_data(current_user.id)
    return render_template('student/reports.html', student=current_user, data=data)


@student_bp.route('/reports/download-pdf')
@login_required
@student_required
def download_pdf_report():
    pdf_buffer = ReportService.generate_student_pdf(current_user)
    
    AuditLog.log(
        action='STUDENT_PDF_REPORT_DOWNLOAD',
        user_id=current_user.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details=f"Student {current_user.registration_number} downloaded their official attendance PDF"
    )

    filename = f"SmartAttend_Report_{current_user.registration_number or current_user.username}.pdf"
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    profile_form = ProfileForm(obj=current_user)
    password_form = PasswordChangeForm()

    if 'submit_profile' in request.form and profile_form.validate_on_submit():
        current_user.full_name = profile_form.full_name.data.strip()
        current_user.email = profile_form.email.data.strip().lower()
        current_user.phone = profile_form.phone.data.strip() if profile_form.phone.data else None

        # Avatar upload
        if profile_form.avatar.data:
            stored_name, _, _, _ = save_secure_file(
                profile_form.avatar.data,
                target_folder=current_app.config['AVATAR_UPLOAD_FOLDER'],
                prefix=f"avatar_{current_user.id}"
            )
            current_user.profile_photo = stored_name

        db.session.commit()
        flash('Profile information updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    if 'submit_password' in request.form and password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash('Current password entered is incorrect.', 'danger')
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            AuditLog.log(
                action='PASSWORD_CHANGED',
                user_id=current_user.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details="Student password successfully changed"
            )
            flash('Your password has been changed securely!', 'success')
            return redirect(url_for('student.profile'))

    data = AttendanceService.get_student_dashboard_data(current_user.id)
    return render_template(
        'student/profile.html',
        student=current_user,
        profile_form=profile_form,
        password_form=password_form,
        data=data
    )
