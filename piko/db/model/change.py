"""
    .. TODO:: A module docstring.
"""
from datetime import datetime

from piko.db import db


# pylint: disable=too-few-public-methods
class Change(db.Model):
    """
        This object represents an entry of a ChangeLog-type table.
    """
    # __tablename__ = "changes"

    # Yearly
    # pylint: disable=eval-used
    # __tablename__ = eval(
    #     '"changes_%s"' % (datetime.strftime(datetime.utcnow(), "%Y"))
    # )

    # Monthly
    # pylint: disable=eval-used
    # __tablename__ = eval(
    #     '"changes_%s"' % (datetime.strftime(datetime.utcnow(), "%Y_%m"))
    # )

    # Daily
    # pylint: disable=eval-used
    __tablename__ = eval(
        '"changes_%s"' % (datetime.strftime(datetime.utcnow(), "%Y_%m_%d"))
    )

    # Hourly
    # pylint: disable=eval-used
    # __tablename__ = eval(
    #     '"changes_%s"' % (
    #         datetime.strftime(datetime.utcnow(), "%Y_%m_%d_%H")
    #     )
    # )

    # Minutely
    # pylint: disable=eval-used
    # __tablename__ = eval(
    #     '"changes_%s"' % (
    #         datetime.strftime(datetime.utcnow(), "%Y_%m_%d_%H_%M")
    #     )
    # )

    # Secondly
    # pylint: disable=eval-used
    # __tablename__ = eval(
    #     '"changes_%s"' % (
    #         datetime.strftime(datetime.utcnow(), "%Y_%m_%d_%H_%M_%S")
    #     )
    # )

    uuid = db.Column(db.Integer, primary_key=True)
    object_name = db.Column(db.String(64))
    object_id = db.Column(db.Integer)
    attribute_name = db.Column(db.String(64))
    value_from = db.Column(db.Text, nullable=True)
    value_to = db.Column(db.Text, nullable=True)
    changed = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        db.create_all()
        super(Change, self).__init__(*args, **kwargs)
