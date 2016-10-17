import base64
import httplib
import json
import urllib
from urlparse import urlparse

import piko

log = piko.getLogger('piko.client')
conf = piko.getConf()
conf.parse_args()

server_uri = conf.get('piko', 'server_uri')

if not server_uri == None:
    result = urlparse(server_uri)
else:
    result = None

if hasattr(result, 'scheme') and result.scheme == 'https':
    API_SSL = True
    API_PORT = 443

if hasattr(result, 'hostname'):
    API_HOSTNAME = result.hostname

if hasattr(result, 'port'):
    API_PORT = result.port

if hasattr(result, 'path'):
    API_BASE = '%s/v1' % (result.path)

conn = None

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def connect():
    global conn, API_SSL, API_PORT, API_HOSTNAME, API_BASE

    if conn == None:
        if API_SSL:
            conn = httplib.HTTPSConnection(API_HOSTNAME, API_PORT)
        else:
            conn = httplib.HTTPConnection(API_HOSTNAME, API_PORT)

        if conf.debuglevel > 8:
            conn.set_debuglevel(9)

        conn.connect()

    return conn

def request(method='GET', path='/', get=None, post=None):
    conn = connect()

    if not get == None:
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
            'Authorization' : 'Basic %s' % (credentials),
            'Content-Type': 'application/json'
        }

    log.debug(
            "REQUEST: %s %s\r\n%s" % (
                    method,
                    "%s/%s%s" % (API_BASE.rstrip('/'), path.lstrip('/'), _get),
                    json.dumps(post, sort_keys=True, indent=4, separators=(',', ': '))
                ),
            level=7
        )

    conn.request(method.upper(), "%s/%s%s" % (API_BASE.rstrip('/'), path.lstrip('/'), _get), json.dumps(post), headers)

    response = conn.getresponse()

    data = response.read()

    try:
        data = json.loads(data)
    except ValueError, errmsg:
        return False

    log.debug(
            "RESPONSE: %s %s\r\n%s" % (
                    method,
                    "%s/%s%s" % (API_BASE.rstrip('/'), path.lstrip('/'), _get),
                    json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
                ),
            level=7
        )

    return data
