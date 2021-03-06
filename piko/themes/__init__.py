"""
    Render templates from a theme, and cache them.
"""
from flask import g
from flask import request
from flask import session

# pylint: disable=no-name-in-module,import-error
from flask.ext.themes import render_theme_template as _render_theme_template

from piko import App
from piko.cache import cache

# pylint: disable=invalid-name
app = App('piko')

# pylint: disable=invalid-name
cache_timeout = 0

if app.config.get('ENVIRONMENT', 'production') == 'development':
    if app.config.get('DEBUG', False):
        cache_timeout = 1


@cache.memoize(timeout=cache_timeout)
# pylint: disable=too-many-arguments
# pylint: disable=unused-argument
def render_theme_template(
        theme,
        template,
        locale,
        country,
        currency,
        user,
        _flash,
        **kwargs):

    """
        A cacheable, theme-based, language specific proxy function to
        :py:func:`flaskext.themes.render_theme_template`.

        :param  theme:      The name of the theme to use.
        :param  template:   The template to render.
        :param  locale:       The language to use.
        :param  kwargs:     The context to pass on to the template.
    """

    return _render_theme_template(
        theme,
        template,
        lang=locale,
        country=country,
        currency=currency,
        **kwargs
    )


def render_template(template, country=None, currency=None, **kwargs):
    """
        A theme-based template renderer.

        This function calls :py:func:`piko.web.webapp.render_theme_template`
        with the language the user prefers.

        :param  template:   The template to render.
        :param  country:    Positional argument to facilitate caching.
                            Inserted if not already set.
        :param  currency:   Positional argument to facilitate caching.
                            Inserted if not already set.
    """
    from piko.i18n import country_by_ipaddr
    from piko.i18n import currency_by_ipaddr
    from piko.i18n import exchange_rate

    if country is None:
        country = country_by_ipaddr(request.remote_addr)

    if currency is None:
        currency = currency_by_ipaddr(request.remote_addr)

    exchange_rate = exchange_rate(currency)

    theme = session.get('theme', app.config.get('DEFAULT_THEME', 'default'))
    user = session.get('uuid', None)

    # flashes is a list of tuples (category, message)
    # We need to pass this along to asure the templates are cached correctly
    flashes = session.get('_flashes', [])
    _flash = ""

    for c, m in flashes:
        _flash += "%r/%r" % (c, m)

    locale = g.get('locale', 'en')

    return render_theme_template(
        theme,
        template,
        locale,
        country,
        currency,
        user,
        _flash,
        exchange_rate=exchange_rate,
        **kwargs
    )
