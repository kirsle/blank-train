#!/usr/bin/env python

"""WSGI runner script for the Blank Train."""

import sys
import os

# Add the CWD to the path.
sys.path.append(".")

# Use the virtualenv.
activate_this = os.environ['HOME']+'/.virtualenv/train/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

def application(environ, start_response):
    from train.app import create_app
    app = create_app()
    return app(environ, start_response)

# vim:ft=python
