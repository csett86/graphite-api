Deployment
==========

There are several options available, depending on your setup.

Gunicorn + nginx
----------------

First, you need to install Gunicorn. The easiest way is to use ``pip``::

    $ pip install gunicorn

If you have installed Graphite-Render in a virtualenv, install Gunicorn in the
same virtualenv::

    $ /usr/share/python/graphite/bin/pip install gunicorn

Next, create the script that will run Graphite-Render using your process watcher
of choice.

*systemd*

::

    # This is /etc/systemd/system/graphite-render.socket
    [Unit]
    Description=graphite-render socket
    
    [Socket]
    ListenStream=/run/graphite-render.sock
    ListenStream=127.0.0.1:8888
    
    [Install]
    WantedBy=sockets.target

::

    # This is /etc/systemd/system/graphite-render.service
    [Unit]
    Description=Graphite-Render service
    Requires=graphite-render.socket
    
    [Service]
    ExecStart=/usr/bin/gunicorn -w2 graphite_render.app:app
    Restart=on-failure
    #User=graphite
    #Group=graphite
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/bin/kill -s TERM $MAINPID
    PrivateTmp=true
    
    [Install]
    WantedBy=multi-user.target

.. note::

    If you have installed Graphite-Render and Gunicorn in a virtualenv, you
    need to use the full path to Gunicorn. Instead of ``gunicorn``, use
    ``/usr/share/python/graphite/bin/gunicorn`` (assuming your virtualenv is
    at ``/usr/share/python/graphite``).

See the `Gunicorn docs`_ for configuration options and command-line flags.

.. _Gunicorn docs: http://docs.gunicorn.org/en/latest/

Finally, configure the nginx vhost:

.. code-block:: nginx

    # /etc/nginx/sites-available/graphite.conf

    upstream graphite {
        server 127.0.0.1:8888 fail_timeout=0;
    }

    server {
        server_name graph;
        listen 80 default;
        root /srv/www/graphite;

        location / {
            try_files $uri @graphite;
        }

        location @graphite {
            proxy_pass http://graphite;
        }
    }

Enable the vhost and restart nginx::

    $ ln -s /etc/nginx/sites-available/graphite.conf /etc/nginx/sites-enabled
    $ service nginx restart

Apache + mod_wsgi
-----------------

First, you need to install mod_wsgi.

See the `mod_wsgi InstallationInstructions`_ for installation instructions.

.. _mod_wsgi InstallationInstructions: https://code.google.com/p/modwsgi/wiki/InstallationInstructions

Then create the graphite-render.wsgi:

.. code-block:: bash

    # /var/www/wsgi-scripts/graphite-render.wsgi

    from graphite_render.app import app as application

Finally, configure the apache vhost:

.. code-block:: apache

    # /etc/httpd/conf.d/graphite.conf

    LoadModule wsgi_module modules/mod_wsgi.so

    WSGISocketPrefix /var/run/wsgi

    Listen 8013
    <VirtualHost *:8013>

        WSGIDaemonProcess graphite-render processes=5 threads=5 display-name='%{GROUP}' inactivity-timeout=120
        WSGIProcessGroup graphite-render
        WSGIApplicationGroup %{GLOBAL}
        WSGIImportScript /var/www/wsgi-scripts/graphite-render.wsgi process-group=graphite-render application-group=%{GLOBAL}

        WSGIScriptAlias / /var/www/wsgi-scripts/graphite-render.wsgi

        <Directory /var/www/wsgi-scripts/>
            Order deny,allow
            Allow from all
        </Directory>
	</VirtualHost>

Adapt the mod_wsgi configuration to your requirements.

See the `mod_wsgi QuickConfigurationGuide`_ for an overview of configurations and `mod_wsgi ConfigurationDirectives`_ to see all configuration directives

.. _mod_wsgi QuickConfigurationGuide: https://code.google.com/p/modwsgi/wiki/QuickConfigurationGuide

.. _mod_wsgi ConfigurationDirectives: https://code.google.com/p/modwsgi/wiki/ConfigurationDirectives

Restart apache::

    $ service httpd restart


