'''A Flask blueprint providing actions for a repoze.who-friendlyform login.
'''

from flask import Blueprint
from flask import request
from flask import render_template, url_for, redirect

blueprint = Blueprint('who', __name__, template_folder='templates')

@blueprint.route('/login')
def login():
    from_url = request.args.get('came_from', '/')
    n = request.environ['repoze.who.logins']
    handler = url_for('.handle_login', came_from=from_url, n=n)
    tpl_vars = dict(login_handler=handler, came_from=from_url, login_counter=n)
    return render_template('who/login_form.html', **tpl_vars)

@blueprint.route('/handle-login')
def handle_login():
    # noop: intercepted by repoze.who-friendlyform
    return

@blueprint.route('/logout')
def logout():
    return redirect(url_for('.handle_logout'))

@blueprint.route('/handle-logout')
def handle_logout():
    # noop: intercepted by repoze.who-friendlyform
    return

@blueprint.route('/logged-in')
def after_login():
    '''A hook invoked after every login attempt (successfull or not)'''
    identity = request.environ.get('repoze.who.identity')
    from_url = request.args.get('came_from', '/')
    if identity:
        return redirect(from_url)
    else:
        n = request.environ['repoze.who.logins'] + 1
        login_url = url_for('.login', came_from=from_url, n=n)
        return redirect(login_url)

@blueprint.route('/logged-out')
def after_logout():
    '''A hook invoked after a successfull logout (i.e. "forget" action)'''
    return render_template('who/bye.html')

