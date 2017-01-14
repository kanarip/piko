from sqlalchemy.ext.hybrid import hybrid_property

from piko.db import db

class KBView(db.Model):
    __tablename__ = 'kb_view'

    _id = db.Column(db.Integer, primary_key=True)

    account_id = db.Column(
        db.Integer,
        db.ForeignKey('account._id', ondelete="CASCADE"),
        index=True
    )

    article_id = db.Column(
        db.Integer,
        db.ForeignKey('kb_article._id', ondelete="CASCADE"),
        index=True
    )

    article = db.relationship('KBArticle')
