import json
import flask
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
    
    # Todo

    return app
