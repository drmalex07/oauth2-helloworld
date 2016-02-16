#!/usr/bin/env python

import os
import argparse
import sys
import json
import mimetypes

here = os.path.dirname(os.path.realpath(__file__))

argp = argparse.ArgumentParser()
argp.add_argument("path", metavar='PATH', type=str, nargs='?', default='/')
argp.add_argument("-c", "--config", dest='config_file', 
    default=os.path.join(here, 'config.ini'))
argp.add_argument("-e", "--pyenv", dest='pyenv_dir')
argp.add_argument("-n", "--name", dest='app_name', default='main')
argp.add_argument("-u", "--user", dest='remote_user', type=str);
argp.add_argument("-x", "--method", dest='method', type=str, 
    default='GET', choices=['GET', 'POST']);
argp.add_argument("-d", "--data-file", dest='data_file', type=str, 
    help=u'Post contents of a file');
argp.add_argument("-o", "--output-file", dest='output_file', type=str,
    default='/tmp/result.json',
    help=u'Dump JSON output to a file');

args = argp.parse_args()

config_file = os.path.realpath(args.config_file)

# Activate enviroment if needed

if args.pyenv_dir:
    activate_this = os.path.realpath(
        os.path.join(args.pyenv_dir, 'bin/activate_this.py'))
    execfile(activate_this, dict(__file__=activate_this))

# Import project-specific modules

import paste.deploy
import webtest

# Load WSGI application

app = paste.deploy.loadapp('config:%s#%s' %(config_file, args.app_name))

# Dispatch request to testing application

extra_environ = {}
if args.remote_user:
    extra_environ['REMOTE_USER'] = args.remote_user

headers = {}

testapp = webtest.TestApp(app)

if args.method == 'GET':
    res = testapp.get(args.path, extra_environ=extra_environ)
elif args.method == 'POST':
    if args.data_file:
        data_file = os.path.realpath(args.data_file)
        content_type, encoding = mimetypes.guess_type(data_file)
        data = None
        with open(data_file, 'r') as ifp:
            data = ifp.read()
        headers['Content-Type'] = content_type
        res = testapp.post(args.path, data, headers=headers, extra_environ=extra_environ)
    else:
        res = testapp.post(args.path, extra_environ=extra_environ)

if hasattr(res, 'json'):
    with open(args.output_file, 'w') as ofp:
        ofp.write(json.dumps(res.json))

print res

