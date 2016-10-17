from flask import g
from flask import request
from flask import session

from flask.ext.babel import Babel
from flask.ext.babel import get_locale as get_babel_locale
from flask.ext.babel import get_timezone as get_babel_timezone
from flask.ext.babel import gettext


def register_l10n(app):

    babel = Babel(app)

    from piko.cache import cache

    @babel.localeselector
    def get_locale():
        locale = getattr(g, 'locale', None)

        #if locale is not None:
        #    return locale

        try:
            translations = get_translations()
        except ValueError, errmsg:
            try:
                cache.delete_memoized(get_translations)
            except ValueError, errmsg:
                cache.clear()
        finally:
            translations = get_translations()

        result = request.accept_languages.best_match(translations)

        if result == None:
            result = 'en'
        else:
            g.locale = result

        session['locale'] = g.get('locale')

        return g.locale

    @babel.timezoneselector
    def get_timezone():
        timezone = getattr(g, 'timezone', None)

        if not timezone == None:
            return timezone

        g.timezone = "UTC"

        return g.timezone

    @cache.memoize()
    def get_translations():
        translations = [x.language for x in babel.list_translations()]
        return translations

__all__ = [
        'get_babel_locale',
        'get_babel_timezone',
        'gettext',
        'register_l10n'
    ]
