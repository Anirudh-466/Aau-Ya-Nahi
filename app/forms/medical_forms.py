from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, DateField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError
from datetime import date

class MedicalApplicationForm(FlaskForm):
    subject_id = SelectField('Subject', coerce=int, validators=[
        DataRequired(message='Please select a subject.')
    ])
    start_date = DateField('Medical Leave Start Date', validators=[
        DataRequired(message='Start date is required.')
    ], default=date.today)
    end_date = DateField('Medical Leave End Date', validators=[
        DataRequired(message='End date is required.')
    ], default=date.today)
    requested_classes = IntegerField('Classes Missed During Illness', validators=[
        DataRequired(message='Please specify number of classes missed.'),
        NumberRange(min=1, max=100, message='Classes must be between 1 and 100.')
    ], default=1)
    certificate = FileField('Medical Certificate (PDF, PNG, JPG)', validators=[
        FileRequired(message='Please upload a signed medical certificate / hospital slip.'),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Only PDF, JPG, and PNG documents are allowed.')
    ])
    reason = TextAreaField('Reason for Medical Leave & Diagnosis', validators=[
        DataRequired(message='Please describe the medical reason.'),
        Length(min=10, max=1000, message='Reason must be between 10 and 1000 characters.')
    ])
    submit = SubmitField('Submit Medical Attendance Request')

    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError('End date cannot precede the start date.')
        if field.data and field.data > date.today():
            raise ValidationError('Medical leave dates cannot be in the future.')
