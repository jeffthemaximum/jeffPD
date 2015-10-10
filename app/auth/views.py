from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from .. import db
from ..models import User, Teacher, Coach, Administrator
from ..email import send_email
from .forms import LoginForm, RegistrationForm, PasswordResetForm, \
    PasswordResetRequestForm, SelectCoachTypeForm


admin_email = 'frey.maxim@gmail.com'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/extra_questions/<coach_id>', methods=['GET', 'POST'])
def extra_questions(coach_id):
    form = SelectCoachTypeForm()
    coach = Coach.query.filter_by(id=coach_id).first()
    if form.validate_on_submit():
        coach.coach_type = form.coach_type.data
        db.session.add(coach)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/extra_questions.html', form=form, coach=coach)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # if registrant selects 'teacher' role, create new teacher
        if form.role.data == 'teacher':
            teacher = Teacher(
                email=form.email.data.lower(),
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data.capitalize(),
                last_name=form.last_name.data.capitalize(),
                school_id=form.school.data)
            db.session.add(teacher)
            user = teacher
            send_email(
                admin_email,
                "New User at JeffPD",
                'mail/new_user',
                user=user)
            db.session.commit()
            flash('You can now login.')
            return redirect(url_for('auth.login'))
        # if registrant selects coach role, create new coach
        elif form.role.data == 'coach':
            coach = Coach(
                email=form.email.data.lower(),
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data.capitalize(),
                last_name=form.last_name.data.capitalize(),
                school_id=form.school.data)
            db.session.add(coach)
            db.session.commit()
            user = coach
            send_email(
                admin_email,
                "New User at JeffPD",
                'mail/new_user',
                user=user)
            flash('Just a couple more questions.')
            return redirect(url_for(
                'auth.extra_questions',
                 coach_id=coach.id))
        else:
            admin = Administrator(
                email=form.email.data.lower(),
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data.capitalize(),
                last_name=form.last_name.data.capitalize(),
                school_id=form.school.data)
            db.session.add(admin)
            user = admin
            send_email(
                admin_email,
                "New User at JeffPD",
                'mail/new_user',
                user=user)
            db.session.commit()
            flash('You can now login.')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
