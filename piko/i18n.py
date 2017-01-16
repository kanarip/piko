"""

    ===============
    ``piko.i18n``
    ===============

    Internationalization (*i18n*) functions for |product_name|.

    The functions in this module make it easier for |product_name| to use and
    provide functionality and modify content based on a visitor's country of
    origin, using GeoIP (through :py:mod:`pygeoip`).

    Most of the functions involved return data based on the IP address of the
    visitor. For example, :py:func:`currency_by_ipaddr` returns.
"""


from country_currencies.data import CURRENCIES_BY_COUNTRY_CODE as currencies
import pycountry
import pygeoip

from piko import App
from piko.cache import cache
from piko.utils import empty

# pylint: disable=invalid-name
app = App('piko')

geoip = pygeoip.GeoIP('/usr/share/GeoIP/GeoLiteCountry.dat')


def country_by_ipaddr(address):
    """
        Resolve the country in which an IP address resides.

        This can be an IPv4 or IPv6 address, and uses
        :py:func:`pygeoip.GeoIP.country_code_by_addr`.

        The reason that that function is not used directly, is
        that the remote address may indeed be None, such as
        when tests use :py:func:`flask.app.test_client()`, or
        when a developer runs :command:`./manage.py runserver`,
        and the source IP address ``127.0.0.1`` does not map to
        a country.

        :param address: An IPv4 or IPv6 IP address, or None.
        :type address:  str
        :returns:       2-character country code
        :rtype:         str
    """

    country = None

    if app.config.get("ENVIRONMENT", "production") == "development":
        country = app.config.get("FAKE_COUNTRY", None)

    if address is None:
        country = app.config.get("FAKE_COUNTRY", "CH")

    if country is None:
        country = geoip.country_code_by_addr(address)

    if empty(country):
        country = "CH"

    return country


def currency_by_ipaddr(address):
    """
        Resolve the currency used in the country in which an IP address
        resides.

        This can be an IPv4 or IPv6 address, and uses
        :py:func:`piko.i18n.country_by_ipaddr` and
        :py:func:`piko.i18n.currency_by_country`.

        :param address: An IPv4 or IPv6 IP address, or None.
        :type address:  str
        :returns:       3-character currency code
        :rtype:         str
    """
    country = country_by_ipaddr(address)
    currency = currency_by_country(country)

    return currency


def exchange_rate_by_ipaddr(address):
    """
        Resolve the current exchange rate for the currency used in the country
        in which an IP address resides.

        This can be an IPv4 or IPv6 address, and uses
        :py:func:`piko.i18n.country_by_ipaddr`,
        :py:func:`piko.i18n.currency_by_country` and
        :py:func:`piko.i18n.exchange_rate`

        :param address: An IPv4 or IPv6 IP address, or None.
        :type address:  str
        :returns:       The exchange rate between the base currency and the
                        target currency.
        :rtype:         float
    """

    country = country_by_ipaddr(address)
    currency = currency_by_country(country)
    rate = exchange_rate(currency)

    return rate


@cache.memoize(timeout=86400)
def exchange_rate(currency):
    """
        Provide the current-ish exchange rate for :py:param:`currency`.
    """
    rates_usd = get_currency_exchange_rates()

    if rates_usd is None:
        if currency == "EUR":
            return 0.95

        return 1

    rates_chf = convert_exchange_rates(rates_usd)

    return rates_chf[currency]


@cache.memoize()
def countries():
    """
        Cache-enabled functional parser of :py:attr:`pycountries.countries`.

        Results in an assured list of country's code and name pairs in the
        form of a dictionary, and is cached using
        :py:func:`flask_cache.Cache.memoize`.

        This function takes no arguments.

        .. NOTE::

            Since this dict of countries is intended to be used for currency
            valuations, ``{ "AQ": "Antarctica" }`` needs to be removed from
            the result -- it does not have a currency.
    """

    _countries = {}
    for code, country in [
            (x.alpha2, x.name) for x in pycountry.countries
            if hasattr(x, 'alpha2') and hasattr(x, 'name')
    ]:

        _countries[code] = country

    # Antarctica has a British and an Australian part, but no currency
    del _countries['AQ']

    return _countries


def country_by_code(code):
    """
        Return the country name provided a country code.
    """
    _countries = countries()

    if code in _countries:
        return _countries[code]


@cache.memoize(timeout=86400)
def currency_by_country(code):
    """
        Retrieve the currency used in a country referred to by the code.
    """
    code = code.upper()

    if code == "PS":
        return "ILS"

    if code in currencies:
        result = currencies[code.upper()]
        if len(result) >= 1:
            return result[0]


@cache.memoize(timeout=86400)
def country_code_by_name(search):
    """
        Return a country code for a country's name.
    """
    result = [code for code, name in countries().iteritems() if name == search]
    if len(result) == 0:
        return None
    elif len(result) == 1:
        return result[0]
    else:
        raise Exception


@cache.memoize(timeout=86400)
def get_currency_exchange_rates():
    """
        Obtain the current-ish exchange rates from OpenExchangeRates.
    """
    from openexchangerates import OpenExchangeRatesClient
    api_key = app.config.get('OPENEXCHANGERATES_API_KEY', None)

    if api_key is None:
        return

    client = OpenExchangeRatesClient(api_key)

    # The base is USD, specifying another base results in an
    # access denied error.
    result = client.latest()

    return result['rates']


@cache.memoize(timeout=86400)
def convert_exchange_rates(rates_usd):
    """
        Convert the exchange rates from base USD to base CHF.
    """

    markup = float(1.03)
    markup = float(1.00)

    rates_chf = {}

    rates_usd['USD'] = 1.0

    for currency, rate in rates_usd.iteritems():
        if currency == "CHF":
            rates_chf[currency] = 1
            continue

        rates_chf[currency] = round(
            (markup / float(rates_usd['CHF'])) * float(rate) * markup,
            5
        )

    return rates_chf
