from flask import render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from . import private
from ..models import Teacher, CoachTeacherLink, Coach, Log, LogTeacherLink
from .forms import AddTeachersForm, CoachLogForm
from .. import db
import pudb


@private.route('/coach/log', methods=['GET', 'POST'])
@login_required
def coach_log():
    if current_user.type != 'coach':
        return redirect(url_for('main.pd_list'))
    if current_user.role == 'teacher':
        return render_template('private/teacher.html')
    else:
        form = CoachLogForm()
        if form.validate_on_submit():
            # get current coach
            curr_coach = current_user

            # get list of teachers by id from form
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

            # add tags
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
                elif tag_num is 9:
                    log.unbelievable = True
                elif tag_num is 10:
                    log.email_help = True

            db.session.add(log)
            db.session.commit()
            flash("Successfully added log!")
            return redirect(url_for('private.coach_log'))

        return render_template('private/coach/log.html', form=form)


@private.route('/coach')
@login_required
def coach():
    if current_user.type != 'coach':
        return redirect(url_for('main.pd_list'))
    return render_template('private/coach.html')


@private.route('/coach/add', methods=['GET', 'POST'])
@login_required
def add_teachers():
    if current_user.type != 'coach':
        return redirect(url_for('main.pd_list'))
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
    return render_template('private/coach/add.html', form=form)


@private.route('/coach/view-logs')
@login_required
def view_coach_logs():
    if current_user.type != 'coach':
        return redirect(url_for('main.pd_list'))
    coach = Coach.query.filter_by(email=current_user.email).first()
    teachers = Teacher.query.all()
    logs = Log.query.filter_by(coach_id=current_user.id).all()
    return render_template(
        'private/coach/view-logs.html',
        Teacher=Teacher,
        coach=coach,
        teachers=teachers,
        logs=logs)


@private.route('/teacher')
@login_required
def teacher():
    if current_user.type != 'teachers':
        return redirect(url_for('main.pd_list'))
    return render_template('private/teacher.html')


@private.route('/teacher/stats')
@login_required
def teacher_stats():
    if current_user.type != 'teachers':
        return redirect(url_for('main.pd_list'))
    return render_template('private/teacher/stats.html')


@private.route('/teacher/logs')
@login_required
def teacher_logs():
    if current_user.type != 'teachers':
        return redirect(url_for('main.pd_list'))
    # get list of all coaches
    coaches = Coach.query.all()
    # get current teacher
    teacher = Teacher.query.filter_by(email=current_user.email).first()
    return render_template(
        'private/teacher/logs.html',
        Coach=Coach,
        coaches=coaches,
        teacher=teacher)


@private.route('/')
@login_required
def private():
    if current_user.type == 'teachers':
        return redirect(url_for('private.teacher'))
    elif current_user.type == 'coach':
        return redirect(url_for('private.coach'))
    else:
        return redirect(url_for('main.pd_list'))


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
