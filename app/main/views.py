from flask import render_template, flash, url_for
from flask.ext.login import current_user, login_required
from . import main


@main.route('/')
def index():
    if current_user.is_authenticated():
        return render_template('pd_list.html')
    else:
        return render_template('index.html')

@main.route('/pd_list')
def pd_list():
    if current_user.is_authenticated() != True:
        flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('pd_list.html')

@main.route('/pd_content/2015_8_27_first_day_google')
# @login_required .. no log in required anymore, not just a flash with a recommendation to sign in.
def pd_one():
    if current_user.is_authenticated() != True:
        flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('pd_content/2015_8_27_first_day_google.html')


@main.route('/pd_content/2015_9_4_gmail_filters.html')
def pd_two():
    if current_user.is_authenticated() != True:
        flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('/pd_content/2015_9_4_gmail_filters.html')
