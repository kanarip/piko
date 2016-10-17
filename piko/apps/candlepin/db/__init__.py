from flask.ext.sqlalchemy import SQLAlchemy

from piko import App

app = App('piko')

db = SQLAlchemy(app)

try:
    from .model import *
except Exception, errmsg:
    app.logger.error("Exception: %r" % (errmsg))
    import traceback
    app.logger.error("%s" % (traceback.format_exc()))

