from functools import wraps
from flask import request, abort

def authenticated(f):
    @wraps(f)
    def handle(*args, **kwargs):
        if not 'repoze.who.identity' in request.environ:
            abort(401)
        else:
            return f(*args, **kwargs)
    return handle

