import sys

import commands

import piko

from piko import utils
from piko.translate import _

log = piko.getLogger('piko.cli.register')
conf = piko.getConf()

def __init__():
    commands.register(
            'dump_config',
            execute,
            description=description()
        )

def cli_options():
    pass

def description():
    return _("Dump your effective piko configuration.")

def execute(*args, **kw):
    """
        Dump your effective piko configuration.
    """
    skips = [
            'cfg_parser',
            'cli_args',
            'cli_keywords',
            'cli_parser',
        ]

    for key, value in conf.__dict__.iteritems():
        if key in skips:
            continue

        print "%s = %r" % (key, value)

    for section in conf.cfg_parser.sections():
        for key, value in conf.cfg_parser.items(section):
            print "%s.%s = %r" % (section, key, value)
