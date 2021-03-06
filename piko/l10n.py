"""
    Localization functions for |product_name|.
"""

from flask import g
from flask import request
from flask import session

# pylint: disable=no-name-in-module
# pylint: disable=import-error
from flask.ext.babel import Babel
from flask.ext.babel import get_locale as get_babel_locale
from flask.ext.babel import get_timezone as get_babel_timezone
from flask.ext.babel import gettext


def register_l10n(app):
    """
        Register the localization functions with an
        :py:class:`App <piko.app.App>`
    """
    babel = Babel(app)

    from piko.cache import cache

    @babel.localeselector
    # pylint: disable=unused-variable
    def get_locale():
        """
            Let babel select the correct locale.
        """
        try:
            translations = get_translations()

        # pylint: disable=unused-variable
        except ValueError, errmsg:
            try:
                cache.delete_memoized(get_translations)
            except ValueError, errmsg:
                cache.clear()
        finally:
            translations = get_translations()

        result = request.accept_languages.best_match(translations)

        if result is None:
            result = 'en'

        g.locale = result

        session['locale'] = g.get('locale')

        return g.get('locale')

    @babel.timezoneselector
    # pylint: disable=unused-variable
    def get_timezone():
        """
            Let babel use the correct timezone.
        """
        timezone = getattr(g, 'timezone', None)

        if timezone is not None:
            return timezone

        g.timezone = "UTC"

        return g.timezone

    @cache.memoize()
    def get_translations():
        """
            Get a list of translations in a form we understand.
        """
        translations = [x.language for x in babel.list_translations()]
        return translations


__all__ = [
    'get_babel_locale',
    'get_babel_timezone',
    'gettext',
    'register_l10n'
]
