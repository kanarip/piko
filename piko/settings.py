"""
    Configuration for piko.
"""
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


##
## DO NOT EDIT THESE
##
ASSET_DEBUG = False
DEBUG = False
DEFAULT_THEME = 'default'
ENVIRONMENT = "production"
MINIFY_PAGE = True
SECRET_KEY = os.urandom(24)
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/piko.db' % (
    os.path.join(basepath(), 'tmp')
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
THEME_PATHS = 'piko/themes'

##
## EDIT THESE, WATCH FOR THE STOP SIGN
##

#ASSETS_DEBUG = True

CACHE_DIR = os.path.join(basepath(), 'tmp', 'cache')
CACHE_TYPE = 'filesystem'

CELERY_ACCEPT_CONTENT = ['pickle', 'msgpack']
#CELERY_BROKER_URL = 'redis://172.17.42.1:6379'
CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_IMPORTS = (
    'piko.bcrypt',
    'piko.ldap',
)

#CELERY_RESULT_BACKEND = 'redis://172.17.42.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
CELERY_RESULT_ENGINE_OPTIONS = {'echo': True}
CELERY_TASK_SERIALIZER = 'msgpack'

DEBUG = True

#DEFAULT_THEME = 'demo'

ENVIRONMENT = 'development'

# Fake the country this connection seems to originate from.
#FAKE_COUNTRY = 'NL'
#FAKE_COUNTRY = 'GB'

LANGUAGES = ['en', 'nl']

#OPENEXCHANGERATES_API_KEY = 'getyourown'

#SECRET_KEY = os.urandom(24)

SQLALCHEMY_DATABASE_URI = 'mysql://piko:piko@127.0.0.1/piko'
#SQLALCHEMY_TRACK_MODIFICATIONS = True

##
## THIS IS A POOR REPRESENTATION OF A STOP SIGN
##
MINIFY_PAGE = (ENVIRONMENT != "development" or not DEBUG)

SQLALCHEMY_ECHO = (ENVIRONMENT == "development" and DEBUG)
