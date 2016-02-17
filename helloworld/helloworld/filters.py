'''Define filters for Flask-specific WSGI applications.

We define the filters (i.e middleware) below in a way that wrapper application
remains a valid Flask object. 
Basically this boils down to:
    app.wsgi_app = FooMiddleware(app.wsgi_app, **config)
instead of:
    app = FooMiddleware(app, **config)
The later form is also a valid WSGi application, but loses all the extended Flask
functionality (like app.run() for debugging purposes).
''' 

import os

def make_static_filter(global_config, document_root, cache_max_age=None):
    
    from paste.urlparser import make_static
    from paste.cascade import Cascade
    
    document_root = os.path.realpath(document_root)
    if not os.access(document_root, os.X_OK | os.R_OK):
        raise ValueError(
            'The document-root (%s) is not accessible' % (document_root))
    
    def filter(app):
        static_app = make_static(global_config, document_root, cache_max_age)
        app.wsgi_app = Cascade([static_app, app.wsgi_app])
        return app
    return filter

def make_session_filter(global_config, **config):
    
    from beaker.middleware import SessionMiddleware
    
    def filter(app):
        app.wsgi_app = SessionMiddleware(app.wsgi_app, config)
        return app
    return filter

def make_who_filter(global_config, config_file, log_file=None):
    
    from repoze.who.config import make_middleware_with_config
    
    def filter(app):
        app.wsgi_app = make_middleware_with_config(
            app.wsgi_app, global_config, config_file, log_file=log_file)
        return app
    return filter
