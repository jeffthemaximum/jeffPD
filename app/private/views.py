from flask import render_template, flash
from flask.ext.login import current_user, login_required
from . import private
from ..models import Teacher, CoachTeacherLink, Coach
from .forms import AddTeachersForm
from .. import db
import pudb


@private.route('/', methods=['GET', 'POST'])
@login_required
def private():
    if current_user.role == 'teacher':
        return render_template('private/teacher.html')
    else:
        form = AddTeachersForm()
        if form.validate_on_submit():
            # teachers is a list of all the teacher id's
            teachers = form.teachers.data
            coach = Coach.query.filter_by(email=current_user.email).first()
            # check if teachers are already coached by coach
            if does_coach_already_coaches_teacher(form, coach):
                for teacher_id in teachers:
                    teacher = Teacher.query.filter_by(id=teacher_id).first()
                    teacher_coach_connection = CoachTeacherLink(coach=coach, teacher=teacher)
                    db.session.add(teacher_coach_connection)
                    db.session.commit()
                flash("You've successfully added teachers you your coaching roster!")
            else:
                flash("You already coach some or all of those teachers. Check your roster and try again.")
        return render_template('private/coach.html', form=form)


def does_coach_already_coaches_teacher(form, coach):
    coaches_teachers = []
    for teacher in coach.teachers:
        coaches_teachers.append(teacher.id)
    teachers = form.teachers.data
    for teacher in teachers:
        if teacher in coaches_teachers:
            return False
    return True


# @private.route('/teacher')
# @login_required
# def teacher():
#     return render_template('private/teacher.html')


# @private.route('/coach')
# @login_required
# def coach():
#     return render_template('private/coach.html')
