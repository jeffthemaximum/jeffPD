from flask import render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from . import private
from ..models import Teacher, CoachTeacherLink, Coach, Log, LogTeacherLink
from ..models import LogTagLink, Tag
from .forms import AddTeachersForm, CoachLogForm, CoachSelectsTags
from .forms import AdministratorSelectsTeachersForm, AdministratorSelectsCoachesForm
from .. import db
import pudb


def search_coach_logs_by_tag(coach_id, tag_id):
    coach_id = int(coach_id)
    coach = Coach.query.filter_by(id=coach_id).first()
    if tag_id == '0':
        logs = coach.logs.order_by(Log.timestamp).all()
        logs = reversed(logs)
    else:
        coach_logs = []
        tag = Tag.query.filter_by(id=tag_id).first()
        for log in tag.logs:
            if log.coach_id == coach_id:
                coach_logs.append(log)
        logs = coach_logs
        logs = reversed(logs)
    return logs


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
            for tag_id in form.tags.data:
                tag = Tag.query.filter_by(id=tag_id).first()
                log_tag = LogTagLink(
                    log=log,
                    tag=tag)
                db.session.add(log_tag)

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


@private.route('/coach/select-search-params', methods=['GET', 'POST'])
@login_required
def coach_selects_view_log_params():
    if current_user.type != 'coach':
        return redirect(url_for('main.pd_list'))

    form = CoachSelectsTags()

    if form.validate_on_submit():
        return redirect(url_for(
            'private.coach_views_logs',
            tag=form.tags.data))
    return render_template(
        'private/coach/select-search-params.html',
        form=form)


@private.route('/coach/view-logs/<tag>')
@login_required
def coach_views_logs(tag):
    if current_user.type != 'coach':
        return redirect(url_for('main.pd_list'))
    coach = Coach.query.filter_by(email=current_user.email).first()
    logs = search_coach_logs_by_tag(coach.id, tag)
    return render_template(
        'private/coach/view-logs.html',
        coach=coach,
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
    # get current teacher
    teacher = Teacher.query.filter_by(email=current_user.email).first()
    return render_template(
        'private/teacher/logs.html',
        Coach=Coach,
        teacher=teacher)


@private.route('/administrator')
@login_required
def administrator():
    if current_user.type != 'administrator':
        return redirect(url_for('main.pd_list'))
    return render_template('private/administrator.html')


@private.route('/administrator/select-coaches', methods=['GET', 'POST'])
@login_required
def adminstrator_selects_coaches():
    if current_user.type != 'administrator':
        return redirect(url_for('main.pd_list'))

    form = AdministratorSelectsCoachesForm()

    if form.validate_on_submit():
        return redirect(url_for(
            'private.administrator_views_coach_logs',
            coach_id=form.coach.data,
            tag = form.tags.data))
    return render_template(
        'private/administrator/select-coaches.html',
        form=form)


@private.route('/administrator/coach-logs/<coach_id>/<tag>')
@login_required
def administrator_views_coach_logs(coach_id, tag):
    if current_user.type != 'administrator':
        return redirect(url_for('main.pd_list'))
    # query db for coach
    coach = Coach.query.filter_by(id=coach_id).first()
    logs = search_coach_logs_by_tag(coach_id, tag)
    return render_template(
        'private/administrator/coach-logs.html',
        coach=coach,
        logs=logs)


@private.route('/administrator/select-teachers', methods=['GET', 'POST'])
@login_required
def adminstrator_selects_teachers():
    if current_user.type != 'administrator':
        return redirect(url_for('main.pd_list'))

    form = AdministratorSelectsTeachersForm()

    if form.validate_on_submit():
        return redirect(url_for(
            'private.administrator_views_teacher_logs',
            teacher_id=form.teacher.data))

    return render_template(
        'private/administrator/select-teachers.html',
        form=form)


@private.route('/administrator/teacher-logs/<teacher_id>')
@login_required
def administrator_views_teacher_logs(teacher_id):
    if current_user.type != 'administrator':
        return redirect(url_for('main.pd_list'))
    # query db for coach
    teacher_id = int(teacher_id)
    teacher = Teacher.query.filter_by(id=teacher_id).first()
    return render_template(
        'private/administrator/teacher-logs.html',
        teacher=teacher)


@private.route('/')
@login_required
def private():
    if current_user.type == 'teachers':
        return redirect(url_for('private.teacher'))
    elif current_user.type == 'coach':
        return redirect(url_for('private.coach'))
    elif current_user.type == 'administrator':
        return redirect(url_for('private.administrator'))
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
