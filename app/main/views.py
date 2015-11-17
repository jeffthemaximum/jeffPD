from flask import render_template, flash
from flask.ext.login import current_user
from . import main


@main.route('/')
def index():
    if current_user.is_authenticated():
        return render_template('pd_list.html')
    else:
        return render_template('index.html')


@main.route('/pd_list')
def pd_list():
    if current_user.is_authenticated() is not True:
        flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('pd_list.html')


@main.route('/pd_content/2015_8_27_first_day_google')
# @login_required .. no log in required anymore, not just a flash with a recommendation to sign in.
def pd_one():
    if current_user.is_authenticated() is not True:
        flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('pd_content/2015_8_27_first_day_google.html')


@main.route('/pd_content/2015_9_4_gmail_filters.html')
def pd_two():
    if current_user.is_authenticated() is not True:
        flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('/pd_content/2015_9_4_gmail_filters.html')


@main.route('/pd_content/drive_folders')
def pd_three():
    if current_user.is_authenticated() is not True:
        flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('/pd_content/2015_9_8_drive_folders.html')


@main.route('/pd_content/class_site')
def pd_four():
    if current_user.is_authenticated() is not True:
            flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('/pd_content/2015_10_1_class_website.html')


@main.route('/pd_content/convert_files')
def pd_five():
    if current_user.is_authenticated() is not True:
            flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('/pd_content/2015_10_10_convert_files.html')


@main.route('/pd_content/open_shared_files')
def pd_six():
    if current_user.is_authenticated() is not True:
            flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('/pd_content/2015_10_13_open_shared_files.html')


@main.route('/pd_content/skedula-grades')
def pd_seven():
    if current_user.is_authenticated() is not True:
            flash("Unlock super cool extras features by logging in or registering. You can do this by clicking 'Login' in the header!")
    return render_template('/pd_content/2015_11_19_standards_based_grades_in_skedula.html')
