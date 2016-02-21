from flask import Blueprint
from flask import request
from flask import render_template, url_for, redirect

from helloworld.lib.auth.helpers import authenticated

blueprint = Blueprint('user', __name__, template_folder='templates')

@blueprint.route('/dashboard')
@authenticated
def show_dashboard():
    return render_template('user/dashboard.html')

@blueprint.route('/info')
@authenticated
def show_account_info():
    return render_template('user/account.html')

@blueprint.route('edit-account')
@authenticated
def edit_account():
    return render_template('user/edit-account.html')

