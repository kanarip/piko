from sqlalchemy_i18n import Translatable
from sqlalchemy_i18n import translation_base
from sqlalchemy.ext.hybrid import hybrid_property

from piko.db import db

from .vote import KBVote

class KBArticle(Translatable, db.Model):
    __tablename__ = 'kb_article'

    __translatable__ = {
            'locales': ['en', 'nl', 'de', 'da', 'fr']
        }

    locale = "en"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    @hybrid_property
    def votes(self):
        """
            The total number of votes on this article.
        """
        return db.session.query(KBVote).filter_by(article_id=self.id).count()

    @hybrid_property
    def votes_down(self):
        """
            The number of non-positive votes on this article.
        """
        return db.session.query(KBVote).filter_by(article_id=self.id, positive=False).count()

    @hybrid_property
    def votes_up(self):
        """
            The number of positive votes on this article.
        """
        return db.session.query(KBVote).filter_by(article_id=self.id, positive=True).count()

class KBArticleLocale(translation_base(KBArticle)):
    __tablename__ = 'kb_article_i18n'

    translator_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    title = db.Column(db.Unicode(120), nullable=False)
    href = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Unicode(512), nullable=False)
    teaser = db.Column(db.UnicodeText, nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)
