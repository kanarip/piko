from flask import abort
from flask import g
from flask import request
from flask import session

from flask.ext.themes import render_theme_template as _render_theme_template
from flask.ext.themes import get_themes_list
from flask.ext.themes import setup_themes

from piko import App
app = App('piko')

def render_theme_template(theme, template, locale, country, currency, user, _flash, **kwargs):
    """
        A cacheable, theme-based, language specific proxy function to
        :py:func:`flaskext.themes.render_theme_template`.

        :param  theme:      The name of the theme to use.
        :param  template:   The template to render.
        :param  locale:       The language to use.
        :param  kwargs:     The context to pass on to the template.
    """

    apps = [
            {
                    "href": "/",
                    "title": "Home"
                },
            {
                    "href": "/login",
                    "title": "Login"
                }
        ]

    return _render_theme_template(theme, template, lang=locale, country=country, currency=currency, apps=apps, **kwargs)

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

    if country == None:
        country = country_by_ipaddr(request.remote_addr)

    if currency == None:
        currency = currency_by_ipaddr(request.remote_addr)

    config_theme = app.config.get('DEFAULT_THEME')

    theme = session.get('theme', app.config.get('DEFAULT_THEME', 'default'))
    user = session.get('uuid', None)

    # flashes is a list of tuples (category, message)
    # We need to pass this along to asure the templates are cached correctly
    flashes = session.get('_flashes', [])
    _flash = ""

    for c,m in flashes:
        _flash += "%r/%r" % (c,m)

    if not hasattr(g, 'locale'):
        locale = 'en'
    else:
        locale = g.get('locale', 'en')

    return render_theme_template(theme, template, locale, country, currency, user, _flash, **kwargs)


