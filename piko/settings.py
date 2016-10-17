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

#ASSETS_DEBUG = True

CACHE_DIR = os.path.join(basepath(), 'tmp', 'cache')
CACHE_TYPE = 'filesystem'

CELERY_ACCEPT_CONTENT = [ 'pickle', 'msgpack' ]
CELERY_BROKER_URL = 'redis://172.17.42.1:6379'
CELERY_IMPORTS = (
        'pack.bcrypt',
        'pack.ldap',
    )

CELERY_RESULT_BACKEND = 'redis://172.17.42.1:6379'
CELERY_RESULT_ENGINE_OPTIONS = {'echo': True}
CELERY_TASK_SERIALIZER = 'msgpack'

DEBUG = True

# Whatever theme you ship yourself, or 'default' or 'demo'
DEFAULT_THEME = 'default'
#DEFAULT_THEME = 'demo'

#FAKE_COUNTRY = 'NL'

LANGUAGES = ['en', 'nl']

MINIFY_PAGE = True

SECRET_KEY = os.urandom(24)

#SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/piko.db' % (os.path.join(basepath(), 'tmp'))
SQLALCHEMY_DATABASE_URI = 'mysql://piko:piko@127.0.0.1/piko_dev'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = True

THEME_PATHS = 'piko/themes'

