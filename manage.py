#!/bin/env python
import os
import sys

sys.path.insert(0, '.')

from flask.ext.assets import ManageAssets
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from piko import App
from piko.db import db

#: The base application.
app = App('piko')

#: Holds registered applications.
applications = {}

#: The base path to search for additional applications.
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
        application = __import__(mod_name, fromlist = [ 'register_blueprint' ])

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

manager = Manager(app)

manager.add_command('assets', ManageAssets)
manager.add_command('db', MigrateCommand)

@manager.command
def create_db():
    db.create_all()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def init_translations():
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
    import glob
    from flask_fixtures.loaders import JSONLoader
    from flask_fixtures import load_fixtures

    db.drop_all()
    db.create_all()

    for fixture_dir in app.config.get('FIXTURES_DIRS', ['./tests/fixtures/']):
        for fixture_file in glob.glob(fixture_dir + '/*.json'):
            fixtures = JSONLoader().load(fixture_file)
            load_fixtures(db, fixtures)

@manager.command
def update_translations():
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
    from subprocess import call
    from subprocess import Popen
    os.environ['PACK_SETTINGS'] = os.path.abspath('./tests/settings.py')
    os.environ['PYTHONPATH'] = ':'.join([ '.' ] + os.environ.get('PYTHONPATH', '').split(':'))

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
                    'piko.app.celery',
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
