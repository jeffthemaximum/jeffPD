from flask import render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from . import private
from ..models import Teacher, CoachTeacherLink, Coach, Log, LogTeacherLink
from ..models import LogTagLink, Tag
from .forms import AddTeachersForm, CoachLogForm, CoachSelectsTags
from .forms import AdministratorSelectsTeachersForm
from .forms import AdministratorSelectsCoachesForm
from .. import db
import pudb


def search_by_tag(coach, tag_id):
    coach_logs = []
    tag = Tag.query.filter_by(id=tag_id).first()
    for log in tag.logs:
        if log.coach_id == coach.id:
            coach_logs.append(log)
    logs = coach_logs
    logs = reversed(logs)
    return logs


def search_by_completed(coach, completed):
    completed = True if completed == '1' else False
    logs = Log.query.filter_by(
        coach_id=coach.id).filter_by(completed=completed).all()
    return logs


def search_by_tag_and_completed(coach, tag_id, completed):
    return_logs = []
    # filter by tag
    logs = search_by_tag(coach, tag_id)
    # filter by completed
    completed = True if completed == '1' else False
    for log in logs:
        if log.completed == completed:
            return_logs.append(log)
    return return_logs


def search_all_coach_logs(coach):
    logs = coach.logs.order_by(Log.timestamp).all()
    logs = reversed(logs)
    return logs


def search_coach_logs(coach_id, tag_id, completed):
    coach_id = int(coach_id)
    coach = Coach.query.filter_by(id=coach_id).first()
    if tag_id != '0' and completed != '0':
        logs = search_by_tag_and_completed(coach, tag_id, completed)
    elif tag_id != '0':
        logs = search_by_tag(coach, tag_id)
    elif completed != '0':
        logs = search_by_completed(coach, completed)
    else:
        logs = search_all_coach_logs(coach)
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
                coach_id=curr_coach.id,
                completed=form.completed.data,
                time=form.time.data)

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
            tag=form.tags.data,
            completed=form.completed.data))
    return render_template(
        'private/coach/select-search-params.html',
        form=form)


@private.route('/coach/view-logs/<tag>/<completed>')
@login_required
def coach_views_logs(tag, completed):
    if current_user.type != 'coach':
        return redirect(url_for('main.pd_list'))
    coach = Coach.query.filter_by(email=current_user.email).first()
    logs = search_coach_logs(coach.id, tag, completed)
    return render_template(
        'private/coach/view-logs.html',
        coach=coach,
        logs=logs)


def get_ids_for_tags(tags):
    tag_ids = []
    for tag in tags:
        tag_ids.append(tag.id)
    return tag_ids


def get_log_tags(log_id):
    logtl = LogTagLink.query.filter_by(log_id=log_id).all()
    tags = []
    for logt in logtl:
        tags.append(Tag.query.filter_by(id=logt.tag_id).first())
    return tags


def get_log_teacher_ids(log):
    teacher_ids = []
    for teacher in log.teachers:
        teacher_ids.append(teacher.id)
    return teacher_ids


def remove_teachers_from_log(teachers, log):
    # need to iterate across logtl and remove all logtl's with log_id = log.id
    log_id = log.id
    for teacher in log.teachers:
        logtl = LogTeacherLink.query.filter_by(log_id=log_id).first()
        db.session.delete(logtl)
        db.session.commit()
    return True


def add_teachers_to_log(teachers_by_id, log):
    for teacher in teachers_by_id:
        teacher = Teacher.query.filter_by(id=teacher).first()
        teacher_log = LogTeacherLink(
            log=log,
            teacher=teacher)
        db.session.add(teacher_log)
        db.session.commit()
    return True


def remove_tags_from_log(tags, log):
    log_id = log.id
    for tag in log.tags:
        logtaglink = LogTagLink.query.filter_by(log_id=log_id).first()
        db.session.delete(logtaglink)
        db.session.commit()
    return True


def add_tags_to_log(tags_by_id, log):
    for tag in tags_by_id:
        tag = Tag.query.filter_by(id=tag).first()
        tag_log = LogTagLink(
            log=log,
            tag=tag)
        db.session.add(tag_log)
    return True


@private.route('/coach/edit-log/<log_id>', methods=['GET', 'POST'])
@login_required
def coach_edits_log(log_id):
    if current_user.type != 'coach':
        return redirect(url_for('main.pd_list'))
    log = Log.query.filter_by(id=log_id).first()
    # get list of teacher id's
    teacher_ids = get_log_teacher_ids(log)
    # get list of tag id's
    tags = get_log_tags(log_id)
    tag_ids = get_ids_for_tags(tags)
    # prepopulate form with tags and teachers
    form = CoachLogForm(
        teachers=teacher_ids,
        tags=tag_ids)
    if form.validate_on_submit():

        # get current coach
        # curr_coach = current_user

        # update log
        log.body = form.body.data
        log.next = form.next.data
        log.completed = form.completed.data
        log.time = form.time.data

        # get list of teachers by id from form
        teachers_by_id = form.teachers.data

        # instantiate list of teachers
        teachers = []

        # add teachers to list
        for teacher in teachers_by_id:
            teachers.append(Teacher.query.filter_by(id=teacher).first())

        teachers.sort()
        log.teachers.sort()
        # check if form teachers != log.teachers
        if (teachers != log.teachers):
            # disconnect old teachers from log
            remove_teachers_from_log(teachers, log)

            # add new teachers
            add_teachers_to_log(teachers_by_id, log)

        # get list of tags by id from form
        tags_by_id = form.tags.data

        # instantiae list of tags
        tags = []

        # add tags to list
        for tag in tags_by_id:
            tags.append(Tag.query.filter_by(id=tag).first())

        tags.sort()
        log.tags.sort()
        # check if form tags != log.tags
        if (tags != log.tags):

            # disconnect old tags from log
            remove_tags_from_log(log.tags, log)

            # add new tags
            add_tags_to_log(tags_by_id, log)

        db.session.add(log)
        db.session.commit()
        flash("Successfully updated log!")
        return redirect(url_for('private.coach'))
    # form.teachers.data = log.teachers
    form.body.data = log.body
    form.next.data = log.next
    form.completed.data = log.completed
    form.time.data = log.time
    # form.tags.data = get_log_tags(log_id)
    return render_template(
        'private/coach/edit-log.html',
        form=form,
        log=log)


@private.route('/coach/delete-log/<log_id>', methods=['GET', 'POST'])
@login_required
def coach_deletes_log(log_id):
    # need to check if log belongs to coach here!!!!
    log = Log.query.filter_by(id=log_id).first()
    remove_teachers_from_log(log.teachers, log)
    remove_tags_from_log(log.tags, log)
    # logteacherlink = LogTeacherLink.query.filter_by(log=log).first()
    # db.session.delete(logteacherlink)
    # db.session.commit()
    # logtaglink = LogTagLink.query.filter_by(log=log).first()
    # db.session.delete(logtaglink)
    # db.session.commit()
    db.session.delete(log)
    db.session.commit()
    flash("Successfully deleted log!")
    return redirect(url_for('private.coach'))


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
            tag=form.tags.data))
    return render_template(
        'private/administrator/select-coaches.html',
        form=form)


@private.route('/administrator/coach-logs/<coach_id>/<tag>')
@login_required
def administrator_views_coach_logs(coach_id, tag):
    pass
    # if current_user.type != 'administrator':
    #     return redirect(url_for('main.pd_list'))
    # # query db for coach
    # coach = Coach.query.filter_by(id=coach_id).first()
    # logs = search_coach_logs_by_tag(coach_id, tag)
    # return render_template(
    #     'private/administrator/coach-logs.html',
    #     coach=coach,
    #     logs=logs)


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
