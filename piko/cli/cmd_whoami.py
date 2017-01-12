import sys

import commands

import piko

from piko import client
from piko import utils
from piko.translate import _

log = piko.getLogger('piko.cli.whoami')
conf = piko.getConf()

def __init__():
    commands.register(
            'whoami',
            execute,
            description=description()
        )

def cli_options():
    pass

def description():
    return _("Check whether the server believes you are you.")

def execute(*args, **kw):
    """
        Check whether the server believes you are you.
    """

    username = conf.get('piko', 'username')
    auth_token = conf.get('piko', 'auth_token')

    if username is None:
        log.error("You are not anybody; username missing.", fatal=True)

    if auth_token is None:
        log.error("You are not anybody; auth token missing.", fatal=True)

    result = client.request(
            method = 'POST',
            path = '/whoami',
            post = {'username': username, 'auth_token': auth_token}
        )

    if result['result']:
        print "YAY: %s" % (result['username'])
    else:
        print "NAY"
