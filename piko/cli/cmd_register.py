import sys

import commands

import piko

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

    print utils.multiline_message(
            "Navigate to %s%s and obtain a token." % (
                    conf.get('piko', 'server_uri').rstrip('/'),
                    '/candlepin/register'
                )
        )

    sys.stdout.flush()

    token = utils.ask_question("Token")

