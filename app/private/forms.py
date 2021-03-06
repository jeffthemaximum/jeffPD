from flask.ext.wtf import Form
from wtforms import SelectMultipleField, SubmitField, widgets, TextAreaField
from wtforms import SelectField, BooleanField, IntegerField
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
        query = Teacher.query.filter_by(
            school=current_user.school).order_by(Teacher.email).all()
        choices = [(teacher.id, teacher.email) for teacher in query]
        self.teachers.choices = choices


class CoachLogForm(Form):
    teachers = SelectMultipleField(
        'Which teacher(s) did you coach?',
        coerce=int)
    body = TextAreaField('What\'d you do?')
    next = TextAreaField('Whatchu gonna do next?')
    completed = BooleanField(
        'Check if coaching is completed. Leave blank if still in progress.')
    tags = SelectMultipleField(
        'Tags',
        coerce=int)
    time = IntegerField('For how many minutes did you work on this?')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(CoachLogForm, self).__init__(*args, **kwargs)
        # populates the role select field choices
        # returns a list of tuples with roleid, name
        curr_coach = current_user
        teachers = curr_coach.teachers
        teachers = sorted(teachers, key=lambda teacher: teacher.email)
        tags = Tag.query.all()
        query_params = [(teacher.id, teacher.email) for teacher in teachers]
        self.teachers.choices = query_params
        self.tags.choices = [(tag.id, tag.name) for tag in tags]


class CoachSelectsTags(Form):
    tags = SelectField(
        'Search by Tag. Leave blank to view all logs.',
        coerce=int,
        default=(0, ''))
    completed = SelectField(
        u'Search by complete. Leave blank to view all logs.',
        choices=[(0, ''), (1, 'Done'), (2, 'In Progress')],
        coerce=int,
        default=(0, ''))
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(CoachSelectsTags, self).__init__(*args, **kwargs)
        # populates the role select field choices
        tags = Tag.query.order_by(Tag.id).all()
        self.tags.choices = [(tag.id, tag.name) for tag in tags]


class CoachSearchesToDos(Form):
    tags = SelectField(
        'Search by Tag. Leave blank to view all logs.',
        coerce=int,
        default=(0, ''))
    # add choice for initializing coach
    # add date range
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(CoachSearchesToDos, self).__init__(*args, **kwargs)
        # populates the role select field choices
        tags = Tag.query.order_by(Tag.id).all()
        self.tags.choices = [(tag.id, tag.name) for tag in tags]


class AdministratorSelectsCoachesForm(Form):
    coach = SelectField(
        "Which coach\'s logs do you wanna see?",
        coerce=int,
        validators=[Required()])
    completed = SelectField(
        u'Search by complete. Leave blank to view all logs.',
        choices=[(0, ''), (1, 'Done'), (2, 'In Progress')],
        coerce=int,
        default=(0, ''))
    tags = SelectField(
        'Search by Tag. Leave blank to view all logs.',
        coerce=int,
        default=(0, ''))

    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(AdministratorSelectsCoachesForm, self).__init__(*args, **kwargs)
        # populates the role select field choices
        # returns a list of tuples with roleid, name
        coaches = Coach.query.filter_by(
            school=current_user.school).order_by(Teacher.email).all()
        self.coach.choices = [(coach.id, coach.email) for coach in coaches]
        tags = Tag.query.order_by(Tag.id).all()
        self.tags.choices = [(tag.id, tag.name) for tag in tags]


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
        teachers = Teacher.query.filter_by(
            school=current_user.school).order_by(Teacher.email).all()
        query_params = [(teacher.id, teacher.email) for teacher in teachers]
        self.teacher.choices = query_params
