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
