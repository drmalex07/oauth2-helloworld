#!/usr/bin/env python

import os
import argparse
import logging.config

here = os.path.dirname(os.path.realpath(__file__))

argp = argparse.ArgumentParser()
argp.add_argument("-c", "--config", dest='config_file', 
    default=os.path.join(here, 'config.ini'))
argp.add_argument("-e", "--pyenv", dest='pyenv_dir')
argp.add_argument("-n", "--name", dest='app_name', default='main')
argp.add_argument("-s", "--server-name", dest='server_name')
args = argp.parse_args()

config_file = os.path.realpath(args.config_file)

# Activate enviroment if needed

if args.pyenv_dir:
    activate_this = os.path.realpath(
        os.path.join(args.pyenv_dir, 'bin/activate_this.py'))
    execfile(activate_this, dict(__file__=activate_this))

# Import project-specific modules

import paste.deploy

# Setup loggers

logging.config.fileConfig(config_file)

# Load application

config_uri = 'config:%s#%s' %(config_file, args.app_name)
app = paste.deploy.loadapp(config_uri);

# Load server

if not args.server_name:
    args.server_name = args.app_name

config_uri = 'config:%s#%s' %(config_file, args.server_name)
server = paste.deploy.loadserver(config_uri)

# Serve 

server(app)
