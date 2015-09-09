from flask.ext.wtf import Form
from wtforms import SelectMultipleField, SubmitField, widgets, TextAreaField, SelectField
from wtforms.validators import Required
from ..models import Teacher, Coach, Tag
from flask.ext.login import current_user
import pudb


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddTeachersForm(Form):
    teachers = SelectMultipleField(
        'Select all the teachers you coach:',
        coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(AddTeachersForm, self).__init__(*args, **kwargs)
        # populates the role select field choices
        # returns a list of tuples with roleid, name
        query = Teacher.query.filter_by(school=current_user.school).order_by(Teacher.email).all()
        choices = [(teacher.id, teacher.email) for teacher in query]
        self.teachers.choices = choices


class CoachLogForm(Form):
    teachers = SelectMultipleField(
        'Which teacher(s) did you coach?',
        coerce=int)
    body = TextAreaField('What\'d you do?')
    next = TextAreaField('Whatchu gonna do next?')
    tags = SelectMultipleField(
        'Tags',
        coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(CoachLogForm, self).__init__(*args, **kwargs)
        # populates the role select field choices
        # returns a list of tuples with roleid, name
        curr_coach = current_user
        teachers = curr_coach.teachers
        tags = Tag.query.all()
        self.teachers.choices = [(teacher.id, teacher.email) for teacher in teachers]
        self.tags.choices = [(tag.id, tag.name) for tag in tags]


class AdministratorSelectsCoachesForm(Form):
    coach = SelectField(
        "Which coach\'s logs do you wanna see?",
        coerce=int,
        validators=[Required()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(AdministratorSelectsCoachesForm, self).__init__(*args, **kwargs)
        # populates the role select field choices
        # returns a list of tuples with roleid, name
        coaches = Coach.query.filter_by(school=current_user.school).order_by(Teacher.email).all()
        self.coach.choices = [(coach.id, coach.email) for coach in coaches]


class AdministratorSelectsTeachersForm(Form):
    teacher = SelectField(
        "Which teacher\'s logs do you wanna see?",
        coerce=int,
        validators=[Required()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(AdministratorSelectsTeachersForm, self).__init__(*args, **kwargs)
        # populates the role select field choices
        # returns a list of tuples with roleid, name
        teachers = Teacher.query.filter_by(school=current_user.school).order_by(Teacher.email).all()
        self.teacher.choices = [(teacher.id, teacher.email) for teacher in teachers]
