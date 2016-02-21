from functools import wraps
from flask import request, abort

def get_authenticated_user():
    identity = request.environ.get('repoze.who.identity')
    user = identity['user'] if identity else None
    return user

def authenticated(f):
    @wraps(f)
    def handle(*args, **kwargs):
        if not 'repoze.who.identity' in request.environ:
            abort(401)
        else:
            return f(*args, **kwargs)
    return handle

