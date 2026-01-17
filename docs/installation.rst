============
Installation
============

Debian / Ubuntu: native package
===============================

If you run Debian 8 or Ubuntu 14.04 LTS, you can use one of the available
packages which provides a self-contained build of graphite-render. Builds are
available on the `releases`_ page.

.. _releases: https://github.com/brutasse/graphite-render/releases

Once installed, Graphite-api should be running as a service and available on
port 8888. The package contains all the :ref:`optional dependencies <extras>`.

Python package
==============

Prerequisites
-------------

Installing Graphite-Render requires:

* Python 2 (2.6 and above) or 3 (3.3 and above), with development files. On
  debian/ubuntu, you'll want to install ``python-dev``.

* ``gcc``. On debian/ubuntu, install ``build-essential``.

* Cairo, including development files. On debian/ubuntu, install the
  ``libcairo2-dev`` package.

* ``libffi`` with development files, ``libffi-dev`` on debian/ubuntu.

* Pip, the Python package manager. On debian/ubuntu, install ``python-pip``.

Global installation
-------------------

To install Graphite-Render globally on your system, run as root::

    $ pip install graphite-render

Isolated installation (virtualenv)
----------------------------------

If you want to isolate Graphite-Render from the system-wide python environment,
you can install it in a virtualenv.

::

    $ virtualenv /usr/share/python/graphite
    $ /usr/share/python/graphite/bin/pip install graphite-render

.. _extras:

Extra dependencies
------------------

When you install ``graphite-render``, all the dependencies for running a Graphite
server that uses Whisper as a storage backend are installed. You can specify
extra dependencies:

* For `Sentry`_ integration: ``pip install graphite-render[sentry]``.

* For `Cyanite`_ integration: ``pip install graphite-render[cyanite]``.

* For Cache support: ``pip install graphite-render[cache]``. You'll also need the
  driver for the type of caching you want to use (Redis, Memcache, etc.). See
  the `Flask-Cache docs`_ for supported cache types.


.. _Sentry: https://docs.getsentry.com
.. _Cyanite: https://github.com/brutasse/graphite-cyanite
.. _Flask-Cache docs: http://pythonhosted.org/Flask-Cache/#configuring-flask-cache

You can also combine several extra dependencies::

    $ pip install graphite-render[sentry,cyanite]
