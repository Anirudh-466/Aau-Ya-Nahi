from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from app import db, limiter
from app.models.user import User
from app.models.subject import Subject
from app.models.attendance import SubjectAttendance
from app.models.audit import AuditLog
from app.forms.auth_forms import LoginForm, StudentRegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Protect against brute-force attacks
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        identity = form.identity.data.strip()
        password = form.password.data

        # Authenticate by username, email, or registration number
        user = User.query.filter(
            or_(
                User.username.ilike(identity),
                User.email.ilike(identity),
                User.registration_number.ilike(identity)
            )
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember.data)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            # Security Audit Log
            AuditLog.log(
                action='LOGIN_SUCCESS',
                user_id=user.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details=f"Successful login via identity: {identity}"
            )

            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))
        else:
            # Audit failed attempt
            AuditLog.log(
                action='LOGIN_FAILURE',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details=f"Failed login attempt for identity: {identity}",
                severity='WARNING'
            )
            flash('Invalid registration number, email, or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

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

        # Enroll student in active subjects matching semester
        subjects = Subject.query.filter_by(semester=user.semester, is_active=True).all()
        for sub in subjects:
            attendance = SubjectAttendance(
                student_id=user.id,
                subject_id=sub.id,
                total_classes=0,
                attended_classes=0,
                medical_classes=0
            )
            db.session.add(attendance)
        db.session.commit()

        AuditLog.log(
            action='STUDENT_REGISTRATION',
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=f"Student registered: {user.registration_number} ({user.email})"
        )

        flash('Registration successful! You can now log in with your credentials.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    user_id = current_user.id
    username = current_user.username
    logout_user()

    AuditLog.log(
        action='LOGOUT',
        user_id=user_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details=f"User logged out: {username}"
    )

    flash('You have been securely signed out.', 'info')
    return redirect(url_for('auth.login'))
