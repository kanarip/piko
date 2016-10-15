"""
    Interestingly enough, Flask does not everything one wants Flask to do.
"""

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
from flask.ext.themes import setup_themes

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

        self.context_processor(self.context_processor_handler)

        Babel(self)

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

    def register_blueprint(self, *args, **kwargs):
        super(App, self).register_blueprint(*args, **kwargs)

    def abort(code, message=None):
        return abort(404)

    def after_request_handler(self, response):
        """
            Executed after a request has been handled, but the response
            has not yet been sent out.
        """
        g.after_request = time.time()
        diff = g.after_request - g.before_request

        try:
            if (response.response):
                response.response[0] = response.response[0].replace('__EXECUTION_TIME__', str(diff))
        except:
            pass

        return response

    def before_request_handler(self):
        """
            Executed before a request is handled.
        """
        g.before_request = time.time()

        g.user = None
        g.locale = None
        g.timezone = None

        register_l10n(self)

        if not 'uuid' in session:
            session['uuid'] = uuid.uuid4().hex

        if 'account_id' in session and not request.path.startswith('/static/'):

            from piko.db import db
            from piko.db.model import Account

            try:
                account = db.session.query(Account).get(session['account_id'])
            except Exception:
                db.session.rollback()
                account = db.session.query(Account).get(session['account_id'])

            if account == None:
                session.clear()

            else:
                g.user = account.id
                g.locale = account.locale
                g.timezone = account.timezone

    def context_processor_handler(self):
        """
            Register functions to use in the Jinja2 templates.
        """
        return dict(_=_)

    def render_template(self, template, *args, **kwargs):
        try:
            from .themes import render_template
        except ImportError:
            from flask import render_template
        finally:
            return render_template(template, *args, **kwargs)

