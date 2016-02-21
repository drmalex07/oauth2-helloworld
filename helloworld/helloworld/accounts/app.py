import json
from flask import Flask, request, session, current_app
from flask import url_for, make_response, redirect
from flask import render_template
import sqlalchemy

from helloworld import model
from helloworld.lib.auth.helpers import get_authenticated_user

def make_app(global_config, **app_config):

    app = Flask(__name__)
    app.config.update(app_config)

    # Create database session factory for requests
    
    db_engine = sqlalchemy.create_engine(
        app_config.get('database.url', 'sqlite://'))
    model.Session.configure(bind=db_engine)

    # Setup template context

    @app.context_processor
    def setup_template_vars():
        return dict(user=get_authenticated_user())
    
    # Setup application routes
    
    from .blueprints import who_blueprint
    app.register_blueprint(who_blueprint)
    
    from .blueprints import user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    @app.route('/')
    def index():
        return render_template('index.html')
          
    return app

