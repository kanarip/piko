"""
    This stuff connects a command-line client to a server.
"""

import base64
import httplib
import json
import ssl
import urllib

from urlparse import urlparse

import piko

# TODO: Only enable this for development environments.
# pylint: disable=protected-access
ssl._create_default_https_context = ssl._create_unverified_context

# pylint: disable=invalid-name
log = piko.getLogger('piko.client')
conf = piko.getConf()
conf.parse_args()

server_uri = conf.get('piko', 'server_uri')

if server_uri is not None:
    result = urlparse(server_uri)
else:
    result = None

API_PORT = None
API_SSL = None

if hasattr(result, 'scheme') and result.scheme == 'https':
    API_PORT = 443
    API_SSL = True
else:
    API_PORT = 80
    API_SSL = False

if hasattr(result, 'hostname'):
    API_HOSTNAME = result.hostname

if hasattr(result, 'port'):
    API_PORT = result.port

if hasattr(result, 'path'):
    API_BASE = '%s/api/v1' % (result.path.rstrip('/'))

conn = None


def connect():
    """
        Connect to the server-side API.
    """
    # pylint: disable=global-statement
    global conn

    if conn is None:
        # pylint: disable=redefined-variable-type
        if API_SSL:
            conn = httplib.HTTPSConnection(API_HOSTNAME, API_PORT)
        else:
            conn = httplib.HTTPConnection(API_HOSTNAME, API_PORT)

        # pylint: disable=no-member
        if conf.debuglevel > 8:
            conn.set_debuglevel(9)

        conn.connect()

    return conn


def request(method='GET', path='/', get=None, post=None):
    """
        Post or get a request.
    """
    _conn = connect()

    if get is not None:
        _get = "?%s" % (urllib.urlencode(get))
    else:
        _get = ""

    credentials = base64.b64encode(
        b"%s:%s" % (
            conf.get('piko', 'username'),
            conf.get('piko', 'auth_token'),
        )
    ).decode("ascii")

    headers = {
        'Authorization': 'Basic %s' % (credentials),
        'Content-Type': 'application/json'
    }

    log.debug(
        "REQUEST: %s %s\r\n%s",
        method,
        "%s/%s%s" % (API_BASE.rstrip('/'), path.lstrip('/'), _get),
        json.dumps(post, sort_keys=True, indent=4, separators=(',', ': ')),
        level=7
    )

    _conn.request(
        method.upper(),
        "%s/%s%s" % (API_BASE.rstrip('/'), path.lstrip('/'), _get),
        json.dumps(post),
        headers
    )

    response = _conn.getresponse()

    data = response.read()

    try:
        data = json.loads(data)

    # pylint: disable=unused-variable
    except ValueError, errmsg:
        return {'result': False}

    log.debug(
        "RESPONSE: %s %s\r\n%s",
        method,
        "%s/%s%s" % (API_BASE.rstrip('/'), path.lstrip('/'), _get),
        json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')),
        level=7
    )

    return data
