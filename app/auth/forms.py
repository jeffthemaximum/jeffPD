from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, School


class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    email = StringField('Email', validators=[
        Required(),
        Length(1, 64),
        Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    first_name = StringField('First Name', validators=[Required()])
    last_name = StringField('Last Name')
    role = SelectField(
        'Teacher or Coach?',
        choices=[
            ('teacher', 'Teacher'),
            ('coach', 'Coach'),
            ('administrator', 'Administrator')],
        validators=[Required()])
    school = SelectField(
        "What school do you work for?",
        coerce=int,
        validators=[Required()])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # populates the role select field choices
        # returns a list of tuples with roleid, name
        schools = School.query.all()
        self.school.choices = [(school.id, school.name) for school in schools]

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class SelectCoachTypeForm(Form):
    coach_type = SelectField(
        'What subject do you coach?',
        choices=[
            ('tech', 'Tech'),
            ('math', 'Math'),
            ('humanities', 'Humanities'),
            ('special_ed', 'Special Education')],
        validators=[Required()])
    submit = SubmitField('Register')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first() is None:
            raise ValidationError('Unknown email address.')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')
