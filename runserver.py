#!/usr/bin/env python
from __future__ import unicode_literals, absolute_import

import argparse
from train.app import create_app

parser = argparse.ArgumentParser(description="[____] Train")
parser.add_argument(
    "--port", "-p",
    type=int,
    help="Port to listen on",
    default=2006,
)
args = parser.parse_args()

if __name__ == '__main__':
    flask_options = dict(
        host='0.0.0.0',
        debug=True,
        port=args.port,
        threaded=True,
    )

    app = create_app()
    app.run(**flask_options)
