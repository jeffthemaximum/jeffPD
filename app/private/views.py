from flask import render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from . import private
from ..models import Teacher, CoachTeacherLink, Coach, Log, LogTeacherLink
from .forms import AddTeachersForm, CoachLogForm
from .. import db
import pudb


@private.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    if current_user.role == 'teacher':
        return render_template('private/teacher.html')
    else:
        form = CoachLogForm()
        if form.validate_on_submit():
            # get current coach
            curr_coach = current_user

            # get teachers
            teachers_by_id = form.teachers.data

            # instantiate list of teachers
            teachers = []

            # add teachers to list
            for teacher in teachers_by_id:
                teachers.append(Teacher.query.filter_by(id=teacher).first())

            # create log
            log = Log(
                body=form.body.data,
                next=form.next.data,
                coach_id=curr_coach.id)

            # connect teachers to log
            for teacher in teachers:
                teacher_log = LogTeacherLink(
                    log=log,
                    teacher=teacher)
                db.session.add(teacher_log)

            # # add the tags
            # log_tag_list = {
            #     0: log.hardware,
            #     1: log.coteach,
            #     2: log.coplan,
            #     3: log.jeffpd_publication,
            #     4: log.google_maintenance,
            #     5: log.teacher_chromebook_help,
            #     6: log.contact_nit,
            #     7: log.general_teacher_tech_help,
            #     8: log.google_resources
            # }
            # iterate over tags from form
            for tag_num in form.tags.data:
                if tag_num is 0:
                    log.hardware = True
                elif tag_num is 1:
                    log.coteach = True
                elif tag_num is 2:
                    log.coplan = True
                elif tag_num is 3:
                    log.jeffpd_publication = True
                elif tag_num is 4:
                    log.google_maintenance = True
                elif tag_num is 5:
                    log.teacher_chromebook_help = True
                elif tag_num is 6:
                    log.contact_nit = True
                elif tag_num is 7:
                    log.general_teacher_tech_help = True
                elif tag_num is 8:
                    log.google_resources = True

            db.session.add(log)
            db.session.commit()
            flash("Successfully added log!")
            return redirect(url_for('private.log'))

        return render_template('private/log.html', form=form)


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
                    teacher_coach_connection = CoachTeacherLink(
                        coach=coach,
                        teacher=teacher)
                    db.session.add(teacher_coach_connection)
                    db.session.commit()
                flash(
                    "You've successfully added teachers to your coaching roster!")
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
