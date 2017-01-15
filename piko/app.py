"""
    Interestingly enough, Flask does not everything one wants Flask to do.
"""

import datetime
import os
import time
from uuid import uuid4

from flask import abort
from flask import g
from flask import Flask
from flask import request
from flask import session

# pylint: disable=E0611,F0401
from flask.ext.assets import Environment

from flask.ext.babel import gettext
from flask.ext.htmlmin import HTMLMIN
from flask.ext.themes import setup_themes

from piko.l10n import register_l10n
from piko.translate import _

#: The base path for this application
# pylint: disable=C0103
base_path = os.path.dirname(__file__)


class App(Flask):
    """
        An abstraction class for :py:class:`flask.Flask`, that loops-and-hooks
        everything.
    """

    def __init__(self, *args, **kwargs):

        # Initialize the :py:class:`~Flask` instance
        super(App, self).__init__(*args, **kwargs)

        # Load system settings
        self.config.from_object('piko.settings')

        # Load specified settings.
        if 'PIKO_SETTINGS' in os.environ:
            if os.path.isfile(os.environ['PIKO_SETTINGS']):
                self.config.from_envvar('PIKO_SETTINGS')

        # Set debug. Why? Good question.
        self.debug = self.config.get('DEBUG', False)

        # pylint: disable=E1101
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
            theme_mod = __import__(
                'piko.themes.' + theme,
                fromlist=['register']
            )

            bundles = theme_mod.register(self.assets, bundles)

        self.assets.register(bundles)
        HTMLMIN(self)

    def register_blueprint(self, *args, **kwargs):
        super(App, self).register_blueprint(*args, **kwargs)

    # pylint: disable=no-self-use
    def abort(self, code, message=None):
        """
            Return a :py:class:`flask.Flask`
            :py:class:`flask.wrappers.Response` that ultimately is a
            :py:class:`werkzeug.exceptions.Aborter` instance.
        """
        return abort(code, message)

    def after_request_handler(self, response):
        """
            Executed after a request has been handled, but the response
            has not yet been sent out.
        """
        response.headers['Server'] = 'Joking/Surely 4.20'

        if request.path.startswith('/static/'):
            return response

        if self.config.get('ENVIRONMENT', 'production') == 'production':
            return response

        if not self.config.get('DEBUG', False):
            return response

        from piko.i18n import country_by_ipaddr
        from piko.i18n import currency_by_ipaddr
        from piko.i18n import exchange_rate

        g.after_request = time.time()

        diff = g.after_request - g.before_request

        country = country_by_ipaddr(request.remote_addr)
        currency = currency_by_ipaddr(request.remote_addr)
        currency_usd_exchange_rate = exchange_rate('USD')
        currency_chf_exchange_rate = exchange_rate(currency)
        locale = getattr(g, 'locale', 'en')

        response.direct_passthrough = False

        try:

            _data = response.get_data(as_text=True)

            _data = _data.replace('__EXECUTION_TIME__', str(diff))
            _data = _data.replace('__GEOIP_COUNTRY__', country)
            _data = _data.replace('__I18N_CURRENCY__', currency)

            _data = _data.replace(
                '__I18N_USDRATE__',
                str(currency_usd_exchange_rate)
            )

            _data = _data.replace(
                '__I18N_CHFRATE__',
                str(currency_chf_exchange_rate)
            )

            _data = _data.replace('__L10N_LANGUAGE__', locale)
            _data = _data.replace('__APP_NAME__', self.__class__.__name__)
            _data = _data.replace('__USER_ID__', (str)(g.get('user', "None")))

            response.set_data(_data)

        # pylint: disable=broad-except
        except Exception, errmsg:
            import traceback
            # pylint: disable=superfluous-parens
            print("Exception: %s" % (errmsg))
            print("%s" % (traceback.format_exc()))

        return response

    def before_request_handler(self):
        """
            Executed before a request is handled.
        """
        if request.path.startswith('/static/'):
            return None

        g.before_request = time.time()

        g.environment = self.config.get('ENVIRONMENT', 'production')
        g.debug = self.config.get('DEBUG', False)

        # This effectively initializes a session.
        if 'uuid' not in session:
            session['uuid'] = uuid4().hex

        if 'locale' in session:
            g.locale = session['locale']

        if session.get('person_id', False):
            from piko.db import db
            from piko.db.model import Person
            uuid = session.get('person_id')
            person = db.session.query(Person).filter_by(uuid=uuid).first()

            if person is not None:
                g.user = person.uuid
                g.locale = person.locale
                g.timezone = person.timezone

        register_l10n(self)

    def context_processor_handler(self):
        """
            Register functions to use in the Jinja2 templates.
        """
        return dict(_=_)

    def render_template(self, template, *args, **kwargs):
        """
            Render a template, but pull out some of the keywords and insert
            some of the user- and session-specific foo -- so that it can be
            cached appropriately.
        """
        kwargs['now'] = datetime.datetime.utcnow()

        try:
            from .themes import render_template
        except ImportError:
            from flask import render_template

        return render_template(template, *args, **kwargs)

    def teardown_request_handler(self, exception):
        """
            What do we do when we we tear down the request?

            :param exception:   An :py:class:`Exception`
            :returns:           None
        """
        if exception is not None:
            import traceback
            # pylint: disable=superfluous-parens
            print("Exception: %s" % (exception))
            print("%s" % (traceback.format_exc()))

        from piko.db import db
        db.session.close()
