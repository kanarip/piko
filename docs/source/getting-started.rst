===============
Getting Started
===============

#.  Install build dependencies on your system:

    .. parsed-literal::

        # :command:`dnf install libffi-devel mysql-devel`

#.  Create a Python virtual environment:

    .. parsed-literal::

        $ :command:`virtualenv venv`

#.  Activate the new Python virtual environment:

    .. parsed-literal::

        $ :command:`source venv/bin/activate`

#.  Install the requirements:

    .. parsed-literal::

        $ :command:`pip install -r requirements.txt`

#.  Run the standalone server:

    .. parsed-literal::

        $ :command:`./standalone.py`

To continue in development:

#.  Create a system configuration file :file:`/etc/piko.conf`:

    .. parsed-literal::

        $ :command:`sudo ln -s $(pwd)/piko.conf /etc/piko.conf`

#.  Create a user configuration file :file:`~/.pikorc`:

    .. parsed-literal::

        $ :command:`ln -s $(pwd)/pikorc.example ~/.pikorc`

#.  Run a Redis server:

    .. parsed-literal::

        $ :command:`redis-server --port 6379 --daemonize no --loglevel debug`

#.  Run a **celery** server:

    .. parsed-literal::

        $ :command:`celery -A piko.celery.celery worker`

