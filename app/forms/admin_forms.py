from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, TextAreaField, SubmitField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class SubjectForm(FlaskForm):
    code = StringField('Subject Code', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])
    name = StringField('Subject Name', validators=[
        DataRequired(),
        Length(min=3, max=120)
    ])
    semester = IntegerField('Semester', validators=[
        DataRequired(),
        NumberRange(min=1, max=12)
    ], default=6)
    department = StringField('Department', validators=[
        DataRequired(),
        Length(max=100)
    ], default='Computer Science')
    credits = IntegerField('Credits', validators=[
        DataRequired(),
        NumberRange(min=1, max=10)
    ], default=4)
    faculty_name = StringField('Faculty Name', validators=[
        DataRequired(),
        Length(max=100)
    ])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Subject')


class AttendanceOverrideForm(FlaskForm):
    student_id = HiddenField('Student ID', validators=[DataRequired()])
    subject_id = HiddenField('Subject ID', validators=[DataRequired()])
    total_classes = IntegerField('Total Classes Conducted', validators=[
        DataRequired(),
        NumberRange(min=0, max=500)
    ])
    attended_classes = IntegerField('Classes Attended', validators=[
        DataRequired(),
        NumberRange(min=0, max=500)
    ])
    medical_classes = IntegerField('Approved Medical Classes', validators=[
        NumberRange(min=0, max=500)
    ], default=0)
    remarks = StringField('Administrative Note / Override Reason', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Update Attendance Record')


class MedicalReviewForm(FlaskForm):
    application_id = HiddenField('Application ID', validators=[DataRequired()])
    action = SelectField('Action Decision', choices=[
        ('Approved', 'Approve Application'),
        ('Rejected', 'Reject Application')
    ], validators=[DataRequired()])
    approved_classes = IntegerField('Approved Medical Classes', validators=[
        NumberRange(min=0, max=100)
    ], default=0)
    admin_remarks = TextAreaField('Administrative Remarks / Verification Comments', validators=[
        Optional(),
        Length(max=500)
    ])
    submit = SubmitField('Submit Decision')


class SystemSettingsForm(FlaskForm):
    required_attendance_threshold = FloatField('Required Attendance Threshold (%)', validators=[
        DataRequired(),
        NumberRange(min=50.0, max=100.0)
    ], default=75.0)
    warning_attendance_threshold = FloatField('Warning Attendance Threshold (%)', validators=[
        DataRequired(),
        NumberRange(min=40.0, max=90.0)
    ], default=65.0)
    medical_formula_mode = SelectField('Medical Attendance Calculation Formula', choices=[
        ('standard_addition', 'Standard Addition: (Attended + Medical) / Total * 100'),
        ('exemption_subtraction', 'Duty Exemption: Attended / (Total - Medical) * 100'),
        ('capped_benefit', 'Capped Boost: Regular % + min(Medical %, Max Benefit Cap)'),
        ('weighted_benefit', 'Weighted Factor: (Attended + (Medical * Weight)) / Total * 100')
    ], default='standard_addition')
    max_medical_benefit_percent = FloatField('Max Medical Benefit Cap (%)', validators=[
        NumberRange(min=1.0, max=50.0)
    ], default=15.0)
    medical_weight = FloatField('Medical Weight Multiplier', validators=[
        NumberRange(min=0.1, max=2.0)
    ], default=1.0)
    max_medical_days_allowed = IntegerField('Maximum Medically Approved Days per Semester', validators=[
        NumberRange(min=1, max=90)
    ], default=30)
    semester_name = StringField('Academic Semester Title', validators=[DataRequired(), Length(max=100)])
    university_name = StringField('University / Institution Name', validators=[DataRequired(), Length(max=150)])
    submit = SubmitField('Save System Configuration')
