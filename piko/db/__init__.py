"""
    .. TODO:: A module docstring.
"""
import os

# pylint: disable=no-name-in-module
# pylint: disable=import-error
from flask.ext.babel import get_locale
from flask.ext.sqlalchemy import SQLAlchemy

import sqlalchemy_i18n
import sqlalchemy_utils

from piko import App
# pylint: disable=invalid-name
app = App('piko')

sqlalchemy_utils.i18n.get_locale = get_locale

# pylint: disable=invalid-name
db = SQLAlchemy(app)

sqlalchemy_i18n.make_translatable(db.Mapper)

try:
    # pylint: disable=wildcard-import
    from .model import *                                # noqa: F401,F403,W0401

# pylint: disable=broad-except
except Exception, errmsg:
    app.logger.error("An exception occurred: %r" % (errmsg))
    import traceback
    app.logger.error(traceback.format_exc())

#: The base path to search for additional applications.
# pylint: disable=invalid-name
base_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
        'apps'
    )
)

for candidate in os.listdir(base_path):
    # Must be a directory.
    if not os.path.isdir(os.path.join(base_path, candidate)):
        continue

    mod_name = 'piko.apps.' + candidate + '.db'

    try:
        # Obtain the register function...
        __import__(mod_name, fromlist=['*'])

    except ImportError, errmsg:
        import traceback
        app.logger.error("ImportError for %s: %r" % (mod_name, errmsg))
        app.logger.error("%s" % (traceback.format_exc()))

    except AttributeError, errmsg:
        import traceback
        app.logger.error("AttributeError for %s: %r" % (mod_name, errmsg))
        app.logger.error("%s" % (traceback.format_exc()))
