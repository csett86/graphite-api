import logging
import os
import traceback
import warnings
from importlib import import_module
from logging.config import dictConfig

import structlog
import yaml
from flask import make_response
from structlog.processors import (format_exc_info, JSONRenderer,
                                  KeyValueRenderer)

from . import DEBUG
from .middleware import CORS, TrailingSlash
from .storage import Store

if DEBUG:
    processors = (format_exc_info, KeyValueRenderer())
else:
    processors = (format_exc_info, JSONRenderer())

logger = structlog.get_logger()

def _get_local_timezone_name():
    """Get the local timezone name using standard library zoneinfo."""
    try:
        # Python 3.9+ has zoneinfo in standard library
        from zoneinfo import ZoneInfo
        import time
        
        # Get local timezone name from the system
        tz_name = time.tzname[time.daylight]
        
        # Try to create a ZoneInfo with common timezone name
        # If /etc/localtime exists, try to read it
        if os.path.exists('/etc/localtime'):
            try:
                # Read symlink to get timezone name
                tz_path = os.path.realpath('/etc/localtime')
                if '/zoneinfo/' in tz_path:
                    tz_name = tz_path.split('/zoneinfo/')[-1]
                    # Validate it's a real timezone
                    ZoneInfo(tz_name)
                    return tz_name
            except (OSError, ValueError, KeyError):
                pass
        
        # Fallback to UTC if we can't determine local timezone
        return 'UTC'
    except ImportError:
        # Fallback for Python < 3.9 (though we require 3.8+)
        return 'UTC'


default_conf = {
    'search_index': '/srv/graphite/index',
    'finders': [
        'graphite_render.finders.whisper.WhisperFinder',
    ],
    'functions': [
        'graphite_render.functions.SeriesFunctions',
        'graphite_render.functions.PieFunctions',
    ],
    'whisper': {
        'directories': [
            '/srv/graphite/whisper',
        ],
    },
    'time_zone': _get_local_timezone_name(),
}


# attributes of a classical log record
NON_EXTRA = set(['module', 'filename', 'levelno', 'exc_text', 'pathname',
                 'lineno', 'msg', 'funcName', 'relativeCreated',
                 'levelname', 'msecs', 'threadName', 'name', 'created',
                 'process', 'processName', 'thread'])


class StructlogFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self._bound = structlog.BoundLoggerBase(None, processors, {})

    def format(self, record):
        if not record.name.startswith('graphite_render'):
            kw = dict(((k, v) for k, v in record.__dict__.items()
                       if k not in NON_EXTRA))
            kw['logger'] = record.name
            return self._bound._process_event(
                record.levelname.lower(), record.getMessage(), kw)[0]
        return record.getMessage()


def load_by_path(path):
    module, klass = path.rsplit('.', 1)
    finder = import_module(module)
    return getattr(finder, klass)


def error_handler(e):
    return make_response(traceback.format_exc(), 500,
                         {'Content-Type': 'text/plain'})


def configure(app):
    config_file = os.environ.get('GRAPHITE_API_CONFIG',
                                 '/etc/graphite-render.yaml')
    fallback_config_file = '/etc/graphite-api.yml'
    
    # Try the primary config file
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = yaml.safe_load(f)
            config['path'] = config_file
    # Try the fallback config file
    elif os.path.exists(fallback_config_file):
        with open(fallback_config_file) as f:
            config = yaml.safe_load(f)
            config['path'] = fallback_config_file
        logger.info("using fallback configuration file", path=fallback_config_file)
    # Use default config if neither exists
    else:
        warnings.warn("Unable to find configuration file at {0} or {1}, using "
                      "default config.".format(config_file, fallback_config_file))
        config = {}

    configure_logging(config)

    for key, value in list(default_conf.items()):
        config.setdefault(key, value)

    app.statsd = None
    if 'statsd' in config:
        try:
            from statsd import StatsClient
        except ImportError:
            warnings.warn("'statsd' is provided in the configuration but "
                          "the statsd client is not installed. Please `pip "
                          "install statsd`.")
        else:
            c = config['statsd']
            app.statsd = StatsClient(c['host'], c.get('port', 8125))

    app.cache = None
    if 'cache' in config:
        try:
            from flask_caching import Cache
        except ImportError:
            warnings.warn("'cache' is provided in the configuration but "
                          "Flask-Caching is not installed. Please `pip install "
                          "Flask-Caching`.")
        else:
            cache_conf = {'CACHE_DEFAULT_TIMEOUT': 60,
                          'CACHE_KEY_PREFIX': 'graphite-render:'}
            for key, value in config['cache'].items():
                cache_conf['CACHE_{0}'.format(key.upper())] = value
            app.cache = Cache(app, config=cache_conf)

    loaded_config = {'functions': {}}
    for functions in config['functions']:
        loaded_config['functions'].update(load_by_path(functions))

    if 'carbon' in config:
        if 'hashing_keyfunc' in config['carbon']:
            config['carbon']['hashing_keyfunc'] = load_by_path(
                config['carbon']['hashing_keyfunc'])
        else:
            config['carbon']['hashing_keyfunc'] = lambda x: x
    loaded_config['carbon'] = config.get('carbon', None)

    finders = []
    for finder in config['finders']:
        finders.append(load_by_path(finder)(config))
    loaded_config['store'] = Store(finders)
    app.config['GRAPHITE'] = loaded_config
    app.config['TIME_ZONE'] = config['time_zone']
    logger.info("configured timezone", timezone=app.config['TIME_ZONE'])

    if 'sentry_dsn' in config:
        try:
            from raven.contrib.flask import Sentry
        except ImportError:
            warnings.warn("'sentry_dsn' is provided in the configuration but "
                          "the sentry client is not installed. Please `pip "
                          "install raven[flask]`.")
        else:
            Sentry(app, dsn=config['sentry_dsn'])

    app.wsgi_app = TrailingSlash(CORS(app.wsgi_app,
                                      config.get('allowed_origins')))
    if config.get('render_errors', True):
        app.errorhandler(500)(error_handler)


def configure_logging(config):
    structlog.configure(processors=processors,
                        logger_factory=structlog.stdlib.LoggerFactory(),
                        wrapper_class=structlog.stdlib.BoundLogger,
                        cache_logger_on_first_use=True)
    config.setdefault('logging', {})
    config['logging'].setdefault('version', 1)
    config['logging'].setdefault('handlers', {})
    config['logging'].setdefault('formatters', {})
    config['logging'].setdefault('loggers', {})
    config['logging']['handlers'].setdefault('raw', {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'raw',
    })
    config['logging']['loggers'].setdefault('root', {
        'handlers': ['raw'],
        'level': 'DEBUG',
        'propagate': False,
    })
    config['logging']['loggers'].setdefault('graphite_render', {
        'handlers': ['raw'],
        'level': 'DEBUG',
    })
    config['logging']['formatters']['raw'] = {'()': StructlogFormatter}
    dictConfig(config['logging'])
    if 'path' in config:
        logger.info("loading configuration", path=config['path'])
    else:
        logger.info("loading default configuration")
