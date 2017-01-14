#!/bin/env python
"""
    Manage the piko webserver and database and such.
"""

# Standard imports come first.
import json
import os

import commentjson

# These imports require path extensions
# pylint: disable=E0611,F0401
from flask.ext.assets import ManageAssets
from flask.ext.cache import Cache
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

from piko import App
from piko.db import db

#: The base application.
# pylint: disable=C0103
app = App('piko')

#: Holds registered applications.
# pylint: disable=C0103
applications = {}

#: The base path to search for additional applications.
# pylint: disable=C0103
base_path = os.path.join(
    os.path.dirname(__file__),
    'piko',
    'apps'
)

for candidate in os.listdir(base_path):
    # Must be a directory.
    if not os.path.isdir(os.path.join(base_path, candidate)):
        continue

    mod_name = 'piko.apps.' + candidate

    try:
        # Obtain the register function...
        application = __import__(mod_name, fromlist=['register_blueprint'])

        # ...and execute it.
        application.register_blueprint(app)
    except ImportError, errmsg:
        import traceback
        app.logger.error("ImportError: %r" % (errmsg))
        app.logger.error("%s" % (traceback.format_exc()))
    except AttributeError, errmsg:
        import traceback
        app.logger.error("AttributeError: %r" % (errmsg))
        app.logger.error("%s" % (traceback.format_exc()))

migrate = Migrate(app, db)
cache = Cache(app, config=app.config)

manager = Manager(app)

manager.add_command('assets', ManageAssets)
manager.add_command('db', MigrateCommand)

@manager.command
def clear_cache():
    """
        Clear the caches. All of it.
    """
    cache.clear()

@manager.command
def create_db():
    """
        Create the database tables.
    """
    db.create_all()

@manager.command
def drop_db():
    """
        Drop the tables from the database.
    """
    db.drop_all()

@manager.command
def init_translations():
    """
        Initialize translations.
    """
    from subprocess import call

    # Extract messages
    call(
        [
            'pybabel',
            'extract',
            '-F',
            'babel.cfg',
            '-o',
            'piko/translations/messages.pot',
            '.'
        ]
    )

    for lang in app.config.get('LANGUAGES', ['en']):
        call(
            [
                'pybabel',
                'init',
                '-i',
                'piko/translations/messages.pot',
                '-d',
                'piko/translations/',
                '-l',
                lang
            ]
        )

@manager.command
def load_fixtures():
    """
        Destroy the current database contents and load fixtures
        supplied in ./tests/fixtures/ instead.
    """
    import glob
    from flask_fixtures.loaders import JSONLoader
    from flask_fixtures import load_fixtures as flask_load_fixtures

    db.drop_all()
    db.create_all()

    _fx_path = os.path.join(os.path.dirname(__file__), 'tmp', 'fixtures')

    if not os.path.isdir(_fx_path):
        os.mkdir(_fx_path)

    for fixture_dir in app.config.get('FIXTURES_DIRS', ['./tests/fixtures/']):
        for fixture_file in glob.glob(fixture_dir + '/*.json'):
            with open(fixture_file, 'r') as x:
                target_file = os.path.join(
                    _fx_path,
                    os.path.basename(fixture_file)
                )

                contents = commentjson.load(x)

                with open(target_file, 'w') as y:
                    json.dump(contents, y)

            fixtures = JSONLoader().load(target_file)
            flask_load_fixtures(db, fixtures)
            db.session.commit()

@manager.command
def update_translations():
    """
        Update translations.
    """
    from subprocess import call

    # Extract messages
    call(
        [
            'pybabel',
            'extract',
            '-F',
            'babel.cfg',
            '-o',
            'piko/translations/messages.pot',
            '.'
        ]
    )

    # Update existing .po files
    call(
        [
            'pybabel',
            'update',
            '-i',
            'piko/translations/messages.pot',
            '-d',
            'piko/translations/'
        ]
    )

    # Compile the catalogs
    call(
        [
            'pybabel',
            'compile',
            '--use-fuzzy',
            '-d',
            'piko/translations/'
        ]
    )

@manager.command
def test():
    """
        Run tests, but ensure other processes are available as well.
    """
    from subprocess import call
    from subprocess import Popen
    os.environ['PACK_SETTINGS'] = os.path.abspath('./tests/settings.py')
    os.environ['PYTHONPATH'] = ':'.join(
        ['.'] + os.environ.get('PYTHONPATH', '').split(':')
    )

    p1 = Popen(
        [
            '/usr/bin/redis-server',
            '--port',
            '6379',
            '--daemonize',
            'no'
        ]
    )

    p2 = Popen(
        [
            'celery',
            '-A',
            'piko.celery.celery',
            'worker'
        ]
    )

    call(
        [
            'nosetests',
            '-v',
            '--with-coverage',
            '--cover-branches',
            '--cover-erase',
            '--cover-html',
            '--cover-html-dir=tests/coverage',
            '--cover-package=piko',
            'tests/'
        ]
    )

    p2.terminate()
    p2.wait()

    p1.terminate()
    p1.wait()

if __name__ == "__main__":
    manager.run()
