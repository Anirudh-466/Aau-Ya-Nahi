from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    email = StringField('Email Address', validators=[
        DataRequired(),
        Email()
    ])
    phone = StringField('Contact Phone Number', validators=[
        Optional(),
        Length(max=20)
    ])
    avatar = FileField('Profile Photo', validators=[
        Optional(),
        FileAllowed(['png', 'jpg', 'jpeg'], 'Images only (PNG, JPG, JPEG)')
    ])
    submit = SubmitField('Update Profile')
