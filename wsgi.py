#!/bin/env python

import os
import sys

sys.path.insert(0, '.')

from flask.ext.assets import ManageAssets
from flask.ext.babel import Babel
from flask.ext.cache import Cache
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.socketio import SocketIO

from gevent import monkey

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from piko import App
from piko.db import db

#: The base application.
app = App('piko')

socketio = SocketIO(app, async_mode='gevent')
monkey.patch_all()

#: Holds the registered applications
applications = {}

#: The base path to search for additional applications.
base_path = os.path.join(
        os.path.dirname(__file__),
        'piko',
        'apps'
    )

for candidate in os.listdir(base_path):
    # Must be a directory.
    if not os.path.isdir(os.path.join(base_path, candidate)):
        continue

    mod_name = 'piko.apps.' + candidate

    try:
        # Obtain the register function...
        application = __import__(mod_name, fromlist = [ 'register_blueprint' ])

        # ...and execute it.
        application.register_blueprint(app)
    except ImportError, errmsg:
        import traceback
        app.logger.error("ImportError: %r" % (errmsg))
        app.logger.error("%s" % (traceback.format_exc()))
    except AttributeError, errmsg:
        import traceback
        app.logger.error("AttributeError: %r" % (errmsg))
        app.logger.error("%s" % (traceback.format_exc()))

migrate = Migrate(app, db)
cache = Cache(app, config = app.config)

for name, blueprint in app.blueprints.iteritems():
    blueprint.socketio = socketio

if __name__ == "__main__":
    socketio.run(app, debug=True)
    #app.run(debug=True)
