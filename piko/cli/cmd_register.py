import sys

import commands

import piko

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
    my_option_group = conf.add_cli_parser_option_group(_("CLI Options"))
    my_option_group.add_option(
                '-u', '--user',
                action  = "store",
                type    = str,
                default = None,
                metavar = "USERNAME",
                help    = _("Your username.")
            )


def description():
    return _("Register with your favorite piko.")

def execute(*args, **kw):
    """
        Register with your favorite piko.
    """
    assert(conf.user)

    from piko.client import request

    payload = {
            "name": conf.name
        }

    content = request(method='POST', path='/register', post=payload)

