Graphite-Render documentation
==========================

.. raw:: html

   <p>
   <a class="reference external image-reference" href="https://github.com/csett86/graphite-render"><img alt="GitHub project" src="https://img.shields.io/badge/GitHub-graphite--api-green.svg" style="height: 18px !important; width: auto !important;"></a>

   <a class="reference external image-reference" href="https://pypi.org/p/graphite-render"><img alt="PyPI version" src="https://img.shields.io/pypi/v/graphite-render.svg" style="height: 18px !important; width: auto !important;"></a>
   </p>

Graphite-render is a fork of graphite-api for python3, and would not be possible
with all the great work of its predecessors.

Graphite-api itself is an alternative to Graphite-web, without any built-in
dashboard. Its role is solely to fetch metrics from a time-series database
(whisper, cyanite, etc.) and rendering graphs or JSON data out of these
time series. It is meant to be consumed by any of the numerous Graphite
dashboard applications.

Graphite-Api is a fork of Graphite-web and couldn't have existed without the
fantastic prior work done by the Graphite team.

Why should I use it?
--------------------

Graphite-Render is maintained for python3 only. Other than that is offers
all the things that made graphite-api great:

Graphite-Api offers a number of improvements over Graphite-web that you might
find useful. Namely:

* The Graphite-Render application is completely stateless and doesn't need a SQL
  database. It only needs to talk to a time series database.

* Python 3.8+ is supported.

* The HTTP API accepts JSON data additionnaly to form data and querystring
  parameters.

* The application is extremely simple to :doc:`install <installation>` and
  :doc:`configure <configuration>`.

* The architecture has been drastically simplified and there are many fewer
  moving parts than in graphite-web:

  * No memcache integration -- rendering is live.

  * No support for the Pickle format when rendering.

  * Plugin architecture for :doc:`integrating with time series databases
    <finders>` or :doc:`adding more analysis functions <custom-functions>`.

* The codebase has been thoroughly updated with a focus on test coverage and
  code quality.

.. note::

    Graphite-Render does **not** provide any web/graphical interface. If you
    currently rely on the built-in Graphite composer, Graphite-Render might not
    be for you. However, if you're using a third-party dashboard interface,
    Graphite-Render will do just fine.

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   configuration
   deployment
   api
   functions
   finders
   custom-functions
   releases

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
