import os

from flask import Flask
from flask.ext.babel import get_locale
from flask.ext.sqlalchemy import SQLAlchemy

import sqlalchemy_i18n
import sqlalchemy_utils

sqlalchemy_utils.i18n.get_locale = get_locale

from piko import App
app = App('piko')

db = SQLAlchemy(app)

sqlalchemy_i18n.make_translatable(db.Mapper)

try:
    from .model import *
except:
    pass

