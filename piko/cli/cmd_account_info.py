import sys

import commands

import piko

from piko import client
from piko import utils
from piko.translate import _

log = piko.getLogger('piko.cli.account-info')
conf = piko.getConf()

def __init__():
    commands.register(
            'account_info',
            execute,
            description=description()
        )

def cli_options():
    pass

def description():
    return _("Information about your account.")

def execute(*args, **kw):
    """
        Information about your account.
    """

    username = conf.get('piko', 'username')
    auth_token = conf.get('piko', 'auth_token')

    if username is None:
        log.error("You are not anybody; username missing.", fatal=True)

    if auth_token is None:
        log.error("You are not anybody; auth token missing.", fatal=True)

    result = client.request(
            method = 'POST',
            path = '/account-info',
            post = {'username': username, 'auth_token': auth_token}
        )

    if result['result']:
        print "YAY: %r" % (result)
    else:
        print "NAY"
