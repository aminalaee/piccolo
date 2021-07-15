..  _Engines:

Engines
=======

Engines are what execute the SQL queries. Each supported backend has its own
engine (see  :ref:`EngineTypes`).

It's important that each ``Table`` class knows which engine to use. There are
two ways of doing this - setting it explicitly via the ``db`` argument, or
letting Piccolo find it using ``engine_finder``.

-------------------------------------------------------------------------------

Explicit
--------

This can be useful when writing a simple script which needs to use Piccolo to
connect to a database.

.. code-block:: python

    from piccolo.engine.sqlite import SQLiteEngine
    from piccolo.table import Table
    from piccolo.columns import Varchar


    DB = SQLiteEngine(path='my_db.sqlite')


    # Here we explicitly reference an engine:
    class MyTable(Table, db=DB):
        name = Varchar()

-------------------------------------------------------------------------------

engine_finder
-------------

By default Piccolo uses ``engine_finder``. Piccolo will look for a file called
``piccolo_conf.py`` on the path, and will try and import a ``DB`` variable,
which defines the engine.

You can ask Piccolo to create the ``piccolo_conf.py`` file for you, using the
following command:

.. code-block:: bash

    piccolo project new

Here's an example ``piccolo_conf.py`` file:

.. code-block:: python

    # piccolo_conf.py
    from piccolo.engine.sqlite import SQLiteEngine


    DB = SQLiteEngine(path='my_db.sqlite')

.. hint:: A good place for your piccolo_conf file is at the root of your
    project, where the Python interpreter will be launched.

PICCOLO_CONF environment variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can modify the configuration file location by using the ``PICCOLO_CONF``
environment variable.

In your terminal:

.. code-block:: bash

    export PICCOLO_CONF=piccolo_conf_test

Or at the entypoint for your app, before any other imports:

.. code-block:: python

    import os
    os.environ['PICCOLO_CONF'] = 'piccolo_conf_test'


This is helpful during tests - you can specify a different configuration file
which contains the connection details for a test database. Similarly,
it's useful if you're deploying your code to different environments (e.g.
staging and production). Have two configuration files, and set the environment
variable accordingly.

.. code-block:: python

    # An example piccolo_conf_test.py
    from piccolo.engine.sqlite import SQLiteEngine


    DB = SQLiteEngine(path='my_test_db.sqlite')


If the ``picolo_conf`` file is located in sub-modules (rather than the root of your project) you can specify the path:

.. code-block:: bash

    export PICCOLO_CONF=sub_module.piccolo_conf

-------------------------------------------------------------------------------

.. _EngineTypes:

Engine types
------------

.. hint:: Postgres is the preferred database to use, especially in
 production. It is the most feature complete.


.. toctree::
    :maxdepth: 1

    ./sqlite_engine
    ./postgres_engine
