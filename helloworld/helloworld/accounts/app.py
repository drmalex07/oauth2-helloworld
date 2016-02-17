import json
import flask
import urllib
import logging
from urllib import urlencode
from flask import url_for, request, make_response, redirect
from flask import render_template
import sqlalchemy

from helloworld.lib.auth.helpers import authenticated
from helloworld import model

def make_app(global_config, **app_config):

    app = flask.Flask(__name__)

    log = logging.getLogger(__name__)

    # Create database session factory for requests
    
    db_engine = sqlalchemy.create_engine(
        app_config.get('database.url', 'sqlite://'))
    model.Session.configure(bind=db_engine)

    # Setup application routes

    @app.route('/')
    def index():
        session = request.environ['beaker.session']
        session['foo'] = 'Bar'
        session.save()
        return render_template('index.html')
      
    @app.route('/user')
    @app.route('/user/welcome')
    @authenticated
    def user_welcome():
        identity = request.environ.get('repoze.who.identity')
        return render_template('user/welcome.html',
            user=identity['repoze.who.userid'])

    @app.route('/login')
    def login():
        from_url = request.args.get('came_from', '/')
        n = request.environ['repoze.who.logins']
        handler = '/handle_login?' + urlencode({'came_from': from_url, 'n':  n})
        tpl_vars = dict(login_handler=handler, came_from=from_url, login_counter=n)
        return render_template('login_form.html', **tpl_vars)

    @app.route('/logout')
    def logout():
        return redirect('/handle_logout')

    @app.route('/logged-in')
    def after_login():
        '''A hook invoked after every login attempt (successfull or not)
        '''
        identity = request.environ.get('repoze.who.identity')
        from_url = request.args.get('came_from', '/')
        if identity:
            return redirect(from_url)
        else:
            n = request.environ['repoze.who.logins'] + 1
            login_url = url_for('.login', came_from=from_url, n=n)
            return redirect(login_url)

    @app.route('/logged-out')
    def after_logout():
        '''A hook invoked after a successfull logout (i.e. "forget" action)
        '''
        return render_template('bye.html')
    
    # Done
    return app

