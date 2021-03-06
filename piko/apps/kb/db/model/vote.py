from piko.db import db

class KBVote(db.Model):
    __tablename__ = 'kb_vote'

    _id = db.Column(db.Integer, primary_key=True)

    account_id = db.Column(
        db.Integer,
        db.ForeignKey('account.uuid', ondelete="CASCADE"),
        index=True
    )

    article_id = db.Column(
        db.Integer,
        db.ForeignKey('kb_article._id', ondelete="CASCADE"),
        index=True
    )

    positive = db.Column(db.Boolean, default=True, index=True)

    account = db.relationship('Account')
    article = db.relationship('KBArticle')
