"""
    Caching functions for :py:mod:`piko`.
"""

from flask.ext.cache import Cache

from piko import App
app = App('piko')

cache = Cache(
        app,
        config = app.config
    )
