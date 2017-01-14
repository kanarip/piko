# -*- coding: utf-8 -*-
"""
    .. TODO:: A module docstring.
"""

import logging
import logging.handlers
import os
import sys


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

            if arg == '-d':
                debuglevel = -1
                continue

            if arg == '-l':
                loglevel = -1
                continue

            if loglevel == -1:
                if hasattr(logging, arg.upper()):
                    loglevel = getattr(logging, arg.upper())
                else:
                    loglevel = logging.DEBUG

    def __init__(self, *args, **kwargs):
        if 'name' in kwargs:
            name = kwargs['name']
        elif len(args) == 1:
            name = args[0]
        else:
            name = 'piko'

        logging.Logger.__init__(self, name)

        plaintextformatter = logging.Formatter("%(levelname)s: %(message)s")

        self.console_stdout = logging.StreamHandler(sys.stdout)
        self.console_stdout.setFormatter(plaintextformatter)

        self.addHandler(self.console_stdout)

    def error(self, msg, fatal=False, *args, **kwargs):
        super(Logger, self).error(msg, *args, **kwargs)

        if fatal:
            sys.exit(1)

    def debug(self, msg, level=1, *args, **kwargs):
        self.setLevel(self.loglevel)
        # Work around other applications not using various levels of debugging
        if not self.name.startswith('piko') and not self.debuglevel == 9:
            return

        if level <= self.debuglevel:
            self.log(logging.DEBUG, '[%d]: %s', os.getpid(), msg)
