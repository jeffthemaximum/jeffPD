from flask.ext.wtf import Form
from wtforms import SelectMultipleField, SubmitField, widgets, TextAreaField
from ..models import Teacher
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
        query = Teacher.query.order_by(Teacher.email).all()
        choices = [(teacher.id, teacher.email) for teacher in query]
        self.teachers.choices = choices


class CoachLogForm(Form):
    teachers = SelectMultipleField(
        'Which teacher(s) did you coach?',
        coerce=int)
    body = TextAreaField('What\'d you do?')
    next = TextAreaField('Whatchu gonna do next?')
    my_choices = [
        (0, 'Hardware'),
        (1, 'CoTeach'),
        (2, 'CoPlan'),
        (3, 'JeffPD Publication'),
        (4, 'Google Maintenance'),
        (5, 'Teacher Chromebook Help'),
        (6, 'Contact NIT'),
        (7, 'General Teacher Tech Help'),
        (8, 'Google Resource Creation/Maintenance'),
        (9, 'Unbelievable')]
    tags = SelectMultipleField(
        'Tags',
        choices=my_choices,
        coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(CoachLogForm, self).__init__(*args, **kwargs)
        # populates the role select field choices
        # returns a list of tuples with roleid, name
        curr_coach = current_user
        teachers = curr_coach.teachers
        self.teachers.choices = [(teacher.id, teacher.email) for teacher in teachers]
