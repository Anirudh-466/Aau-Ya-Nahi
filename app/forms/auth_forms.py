from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from app.models.user import User

class LoginForm(FlaskForm):
    identity = StringField('Registration No. / Email / Username', validators=[
        DataRequired(message='Please provide your username, email, or registration number.'),
        Length(min=3, max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ])
    remember = BooleanField('Keep me signed in for 30 days')
    submit = SubmitField('Sign In to Dashboard')


class StudentRegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required.'),
        Length(min=2, max=100)
    ])
    registration_number = StringField('Registration / Roll Number', validators=[
        DataRequired(message='Registration number is required.'),
        Length(min=4, max=50)
    ])
    email = StringField('Official Student Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])
    username = StringField('Username', validators=[
        DataRequired(message='Username is required.'),
        Length(min=3, max=40)
    ])
    course = SelectField('Course', choices=[
        ('B.Tech', 'Bachelor of Technology (B.Tech)'),
        ('BCA', 'Bachelor of Computer Applications (BCA)'),
        ('M.Tech', 'Master of Technology (M.Tech)'),
        ('MCA', 'Master of Computer Applications (MCA)'),
        ('B.Sc', 'Bachelor of Science (B.Sc)')
    ], default='B.Tech')
    branch = SelectField('Department / Branch', choices=[
        ('Computer Science & Engineering', 'Computer Science & Engineering (CSE)'),
        ('Information Technology', 'Information Technology (IT)'),
        ('Artificial Intelligence & ML', 'Artificial Intelligence & Data Science (AI/DS)'),
        ('Electronics & Communication', 'Electronics & Communication (ECE)'),
        ('Mechanical Engineering', 'Mechanical Engineering (ME)')
    ], default='Computer Science & Engineering')
    semester = IntegerField('Current Semester', validators=[
        DataRequired(),
        NumberRange(min=1, max=12, message='Semester must be between 1 and 12')
    ], default=6)
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please re-enter your password.'),
        EqualTo('password', message='Passwords must match exactly.')
    ])
    submit = SubmitField('Create Student Account')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError('This username is already taken. Please choose another.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError('An account with this email already exists.')

    def validate_registration_number(self, field):
        if User.query.filter_by(registration_number=field.data.strip().upper()).first():
            raise ValidationError('This registration number is already registered.')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Update Password')
