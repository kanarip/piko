from datetime import datetime

from piko.db import db

class Change(db.Model):
    """
        This object represents an entry of a ChangeLog-type table.
    """
    __tablename__ = "changes"

    # Yearly
    #__tablename__ = eval('"changes_%s"' % (datetime.strftime(datetime.utcnow(), "%Y")))

    # Monthly
    #__tablename__ = eval('"changes_%s"' % (datetime.strftime(datetime.utcnow(), "%Y_%m")))

    # Daily
    #__tablename__ = eval('"changes_%s"' % (datetime.strftime(datetime.utcnow(), "%Y_%m_%d")))

    # Hourly
    #__tablename__ = eval('"changes_%s"' % (datetime.strftime(datetime.utcnow(), "%Y_%m_%d_%H")))

    # Minutely
    #__tablename__ = eval('"changes_%s"' % (datetime.strftime(datetime.utcnow(), "%Y_%m_%d_%H_%M")))

    # Secondly
    #__tablename__ = eval('"changes_%s"' % (datetime.strftime(datetime.utcnow(), "%Y_%m_%d_%H_%M_%S")))

    id = db.Column(db.Integer, primary_key=True)
    object_name = db.Column(db.String(64))
    object_id = db.Column(db.Integer)
    value_from = db.Column(db.Text, nullable=True)
    value_to = db.Column(db.Text, nullable=True)
    changed = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, object_name, object_id, value_from, value_to):
        self.object_name = object_name
        self.object_id = object_id
        self.value_from = value_from
        self.value_to = value_to
