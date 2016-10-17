# -*- coding: utf-8 -*-

import grp
import logging
import logging.handlers
import os
import pwd
import sys
import time

from piko.translate import _

class Logger(logging.Logger):
    """
        The piko version of a logger.

        This class wraps the Python native logging library, adding to the
        loglevel capabilities, a debuglevel capability.
    """
    debuglevel = 0
    fork = False
    loglevel = logging.WARNING

    if hasattr(sys, 'argv'):
        for arg in sys.argv:
            if debuglevel == -1:
                try:
                    debuglevel = int(arg)
                except ValueError, errmsg:
                    continue

                loglevel = logging.DEBUG
                break

            if '-d' == arg:
                debuglevel = -1
                continue

            if '-l' == arg:
                loglevel = -1
                continue

            if loglevel == -1:
                if hasattr(logging,arg.upper()):
                    loglevel = getattr(logging,arg.upper())
                else:
                    loglevel = logging.DEBUG

    def __init__(self, *args, **kw):
        if kw.has_key('name'):
            name = kw['name']
        elif len(args) == 1:
            name = args[0]
        else:
            name = 'piko'

        logging.Logger.__init__(self, name)

        plaintextformatter = logging.Formatter("%(levelname)s: %(message)s")

        self.console_stdout = logging.StreamHandler(sys.stdout)
        self.console_stdout.setFormatter(plaintextformatter)

        self.addHandler(self.console_stdout)

    def debug(self, msg, level=1, *args, **kw):
        self.setLevel(self.loglevel)
        # Work around other applications not using various levels of debugging
        if not self.name.startswith('piko') and not self.debuglevel == 9:
            return

        if level <= self.debuglevel:
            # TODO: Not the way it's supposed to work!
            self.log(logging.DEBUG, '[%d]: %s' % (os.getpid(),msg))

