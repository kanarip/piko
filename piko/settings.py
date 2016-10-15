import os

def basepath():
    """
        return the base path.
    """
    return os.path.abspath(
            os.path.join(
                    os.path.dirname(__file__),
                    '..'
                )
        )

CACHE_DIR = os.path.join(basepath(), 'tmp', 'cache')
CACHE_TYPE = 'filesystem'

DEBUG = True

# Whatever theme you ship yourself, or 'default' or 'demo'
DEFAULT_THEME = 'default'
#DEFAULT_THEME = 'demo'

THEME_PATHS = 'piko/themes'

LANGUAGES = ['en', 'nl']

SECRET_KEY = os.urandom(24)

SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/piko.db' % (os.path.join(basepath(), 'tmp'))
SQLALCHEMY_ECHO = True

