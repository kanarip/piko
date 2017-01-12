import sys

import commands

import piko

from piko import client
from piko import utils
from piko.translate import _

log = piko.getLogger('piko.cli.register')
conf = piko.getConf()

def __init__():
    commands.register(
            'register',
            execute,
            description=description()
        )

def cli_options():
    pass

def description():
    return _("Register with your favorite piko.")

def execute(*args, **kw):
    """
        Register with your favorite piko.
    """

    # TODO: Require to run as root

    # TODO: Who are we?

    # TODO: Are we any one of a set of valid customers?

    # TODO: Generate this system's uuid

    if conf.get('piko', 'auth_token') is None:
        print utils.multiline_message(
                "Navigate to %s%s and obtain a token." % (
                        conf.get('piko', 'server_uri').rstrip('/'),
                        '/candlepin/register'
                    )
            )

        sys.stdout.flush()

        token = utils.ask_question("Token", password=True)

        conf.command_set('piko', 'auth_token', token)

    result = client.request(
            method = 'GET',
            path = '/candlepin/system/register'
        )

    if result['result']:
        print "OK"
    else:
        print "NO"
