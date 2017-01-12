import sys

import commands

import piko

from piko import utils
from piko.translate import _

log = piko.getLogger('piko.cli.register')
conf = piko.getConf()

def __init__():
    commands.register(
            'set',
            execute,
            description=description()
        )

def cli_options():
    pass

def description():
    return _("Set an item in the piko configuration.")

def execute(*args, **kw):
    """
        Set an item in the piko configuration.
    """

    conf.command_set(sys.argv[1], sys.argv[2], sys.argv[3])
