============
Installation
============

Python package
==============

Prerequisites
-------------

Installing Graphite-Render requires:

* Python 3 (3.9 and above).

* Pip, the Python package manager. On debian/ubuntu, install ``python-pip``.

* **For image rendering (PNG/SVG/PDF graphs):** Cairo. On debian/ubuntu, install the ``libcairo2`` package.

Global installation
-------------------

To install Graphite-Render globally on your system, run as root::

    $ pip install graphite-render

For image rendering support (PNG/SVG/PDF graphs), install with the cairo extra::

    $ pip install graphite-render[cairo]

Isolated installation (virtualenv)
----------------------------------

If you want to isolate Graphite-Render from the system-wide python environment,
you can install it in a virtualenv.

::

    $ virtualenv /usr/share/python/graphite
    $ /usr/share/python/graphite/bin/pip install graphite-render[cairo]

.. _extras:

Extra dependencies
------------------

When you install ``graphite-render``, all the dependencies for running a Graphite
server that uses Whisper as a storage backend are installed. You can specify
extra dependencies:

* For image rendering (PNG/SVG/PDF): ``pip install graphite-render[cairo]``.
  You'll also need Cairo installed on your system (``libcairo2`` on debian/ubuntu).

* For `Sentry`_ integration: ``pip install graphite-render[sentry]``.

* For `Cyanite`_ integration: ``pip install graphite-render[cyanite]``.

* For Cache support: ``pip install graphite-render[cache]``. You'll also need the
  driver for the type of caching you want to use (Redis, Memcache, etc.). See
  the `Flask-Cache docs`_ for supported cache types.


.. _Sentry: https://docs.getsentry.com
.. _Cyanite: https://github.com/brutasse/graphite-cyanite
.. _Flask-Cache docs: http://pythonhosted.org/Flask-Cache/#configuring-flask-cache

You can also combine several extra dependencies::

    $ pip install graphite-render[cairo,sentry,cyanite]
