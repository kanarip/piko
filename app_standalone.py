#!/usr/bin/env python
"""
    Run a standalone server using :py:class:`flask.Flask`.
"""
import os

from piko import App

# pylint: disable=invalid-name
app = App('piko')

#: Holds registered applications.
# pylint: disable=invalid-name
applications = {}

#: The base path to search for additional applications.
# pylint: disable=invalid-name
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
        application = __import__(mod_name, fromlist=['register'])

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

if __name__ == "__main__":
    debug = app.config.get('DEBUG', False)
    app.run(debug=debug)
