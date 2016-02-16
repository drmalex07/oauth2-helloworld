'''This is an example wsgi script suitable for Apache2's mod_wsgi.

A corresponding vhost configuration would be like:

    WSGIPassAuthorization On
    WSGIDaemonProcess "helloworld-wsgi" user=malex group=malex processes=2 threads=4
    WSGIProcessGroup "helloworld-wsgi"
    WSGIScriptAlias "/helloworld" /home/malex/pyenv/src/helloworld/wsgi.py

'''
#!/usr/bin/env python

import os
import logging.config

here = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(here, 'config.ini')

pyenv_dir = os.path.realpath(os.path.join(here, '../..')
activate_this = os.path.join(pyenv_dir, 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

logging.config.fileConfig(config_file)

from paste.deploy import loadapp
application = loadapp('config:%s#main' %(config_file))

