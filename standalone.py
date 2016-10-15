#!/usr/bin/env python

import os

from piko import App

app = App('piko')

#: Holds registered applications.
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

if __name__ == "__main__":
    app.run()
