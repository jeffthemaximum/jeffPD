from flask.ext.wtf import Form
from wtforms import SelectMultipleField, SubmitField, widgets
from ..models import Teacher


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddTeachersForm(Form):
    # choices = [(teacher.id, teacher.name) for teacher in Teacher.query.order_by(Teacher.email).all()]
    teachers = MultiCheckboxField(
        'Select all the teachers you coach:',
        coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(AddTeachersForm, self).__init__(*args, **kwargs)
        # populates the role select field choices
        # returns a list of tuples with roleid, name
        self.teachers.choices = [(teacher.id, teacher.email)
                             for teacher in Teacher.query.order_by(Teacher.email).all()]
