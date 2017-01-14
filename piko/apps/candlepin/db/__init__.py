"""
    candlepin.db
    ============

    Entry-point for all database actions related to candlepin.
"""
# pylint: disable=no-name-in-module
# pylint: disable=import-error
from flask.ext.sqlalchemy import SQLAlchemy

from piko import App

# pylint: disable=invalid-name
app = App('piko')

# pylint: disable=invalid-name
db = SQLAlchemy(app)

try:
    # pylint: disable=wildcard-import
    from .model import *

# pylint: disable=broad-except
except Exception, errmsg:
    import traceback
    app.logger.error("Exception: %r" % (errmsg))
    app.logger.error("%s" % (traceback.format_exc()))
