"""
    Nothing to see here.

    .. automodule:: piko.app
"""
import logging
import threading

from .app import App
from .blueprint import Blueprint

def getLogger(name):
    """
        Return the correct logger class.
    """
    from .logger import Logger

    logging.setLoggerClass(Logger)
    log = logging.getLogger(name=name)
    return log

from .conf import Conf
conf = Conf()

def getConf():
    _data = threading.local()
    if hasattr(_data, 'conf'):
        log.debug(_("Returning thread local configuration"))
        return _data.conf

    return conf

__all__ = [
        'App',
        'Blueprint'
    ]
