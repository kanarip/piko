from sqlalchemy_i18n import Translatable
from sqlalchemy_i18n import translation_base

from piko.db import db

class Product(Translatable, db.Model):
    __tablename__ = 'product'
    __translatable__ = {
            'locales': ['en', 'nl', 'de', 'da', 'fr']
        }

    locale = "en"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), nullable=False)
    bestprice = db.Column(db.Float, nullable=True)
    signup_enabled = db.Column(db.Boolean, default=False)

class ProductLocale(translation_base(Product)):
    __tablename__ = 'product_i18n'

    name = db.Column(db.Unicode(64))
    highlights = db.Column(db.UnicodeText)
    description = db.Column(db.UnicodeText)
