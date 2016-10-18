"""
    Interestingly enough, Flask does not everything one wants Flask to do.
"""

import datetime
import os
import time
import uuid

from flask import abort
from flask import g
from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from flask.ext.assets import Bundle
from flask.ext.assets import Environment

from flask.ext.babel import Babel
from flask.ext.babel import gettext
from flask.ext.htmlmin import HTMLMIN
from flask.ext.themes import setup_themes
from flask.ext.socketio import disconnect

from functools import wraps

from piko.l10n import register_l10n
from piko.translate import _

#: The base path for this application
base_path = os.path.dirname(__file__)

class App(Flask):
    """
        An abstraction class for Flask, that loops-and-hooks everything.
    """

    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.config.from_object('piko.settings')

        if os.environ.has_key('PIKO_SETTINGS'):
            if os.path.isfile(os.environ['PIKO_SETTINGS']):
                self.config.from_envvar('PIKO_SETTINGS')

        self.jinja_env.filters['gettext'] = gettext

        self.after_request(self.after_request_handler)
        self.before_request(self.before_request_handler)
        self.teardown_request(self.teardown_request_handler)

        self.context_processor(self.context_processor_handler)

        setup_themes(self)

        self.assets = Environment(self)

        bundles = {}

        candidates = []

        for candidate in os.listdir(os.path.join(base_path, 'themes')):
            # Must be a directory.
            if not os.path.isdir(os.path.join(base_path, 'themes', candidate)):
                continue

            candidates.append(candidate)

        for theme in candidates:
            theme_mod = __import__('piko.themes.' + theme, fromlist = [ 'register' ])
            bundles = theme_mod.register(self.assets, bundles)

        self.assets.register(bundles)
        HTMLMIN(self)

    def register_blueprint(self, *args, **kwargs):
        super(App, self).register_blueprint(*args, **kwargs)

    def abort(self, code, message=None):
        return abort(code, message)

    def after_request_handler(self, response):
        """
            Executed after a request has been handled, but the response
            has not yet been sent out.
        """
        from piko.i18n import country_by_ipaddr
        from piko.i18n import currency_by_ipaddr

        g.after_request = time.time()

        diff = g.after_request - g.before_request

        country = country_by_ipaddr(request.remote_addr)
        currency = currency_by_ipaddr(request.remote_addr)
        locale = getattr(g, 'locale', None)

        try:
            if (response.response):
                response.response[0] = response.response[0].replace('__EXECUTION_TIME__', str(diff))
                response.response[0] = response.response[0].replace('__GEOIP_COUNTRY__', country)
                response.response[0] = response.response[0].replace('__I18N_CURRENCY__', currency)
                response.response[0] = response.response[0].replace('__L10N_LANGUAGE__', locale)
        except:
            pass

        return response

    def before_request_handler(self):
        """
            Executed before a request is handled.
        """
        g.before_request = time.time()

        if not 'uuid' in session:
            session['uuid'] = uuid.uuid4().hex

        if 'locale' in session:
            g.locale = session['locale']

        if 'account_id' in session and not request.path.startswith('/static/'):

            from piko.db import db
            from piko.db.model import Account

            try:
                account = db.session.query(Account).get(session['account_id'])
            except Exception, errmsg:
                db.session.rollback()
                account = db.session.query(Account).get(session['account_id'])

            if account == None:
                session.clear()

            else:
                g.user = account.id
                g.locale = account.locale
                g.timezone = account.timezone

        register_l10n(self)

    def context_processor_handler(self):
        """
            Register functions to use in the Jinja2 templates.
        """
        return dict(_=_)

    def render_template(self, template, *args, **kwargs):
        kwargs['now'] = datetime.datetime.utcnow()
        try:
            from .themes import render_template
        except ImportError:
            from flask import render_template
        finally:
            return render_template(template, *args, **kwargs)

    def teardown_request_handler(self, exception):
        db = getattr(g, 'db', None)
        if db is not None:
            db.session.close()

