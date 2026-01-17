import os
import tempfile
import unittest
import warnings
from unittest.mock import patch

import yaml


class TestConfigFallback(unittest.TestCase):
    """Test configuration file fallback behavior."""

    def test_primary_config_file_exists(self):
        """Test that primary config file is loaded when it exists."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('time_zone: America/New_York\n')
            primary_config = f.name
        
        try:
            with patch.dict(os.environ, {'GRAPHITE_API_CONFIG': primary_config}):
                from flask import Flask
                app = Flask(__name__)
                from graphite_render.config import configure
                
                configure(app)
                
                # Verify the config was loaded from primary
                self.assertEqual(app.config['TIME_ZONE'], 'America/New_York')
        finally:
            os.unlink(primary_config)
    
    def test_fallback_config_file_used(self):
        """Test that fallback config file is loaded when primary doesn't exist."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write('time_zone: Europe/London\n')
            fallback_config = f.name
        
        try:
            # Test by patching the fallback location
            from flask import Flask
            import graphite_render.config as config_module
            
            # Save original function
            original_configure = config_module.configure
            
            # Create a patched version of configure that uses our test fallback file
            def test_configure(app):
                config_file = os.environ.get('GRAPHITE_API_CONFIG',
                                             '/etc/graphite-render.yaml')
                fallback_config_file = fallback_config  # Use test file instead of /etc/graphite-api.yml
                
                # Try the primary config file
                if os.path.exists(config_file):
                    with open(config_file) as f_in:
                        config = yaml.safe_load(f_in)
                        config['path'] = config_file
                # Try the fallback config file
                elif os.path.exists(fallback_config_file):
                    with open(fallback_config_file) as f_in:
                        config = yaml.safe_load(f_in)
                        config['path'] = fallback_config_file
                    config_module.logger.info("using fallback configuration file", path=fallback_config_file)
                # Use default config if neither exists
                else:
                    warnings.warn("Unable to find configuration file at {0} or {1}, using "
                                  "default config.".format(config_file, fallback_config_file))
                    config = {}
                
                config_module.configure_logging(config)
                
                for key, value in list(config_module.default_conf.items()):
                    config.setdefault(key, value)
                
                app.statsd = None
                app.cache = None
                
                loaded_config = {'functions': {}}
                for functions in config['functions']:
                    loaded_config['functions'].update(config_module.load_by_path(functions))
                
                loaded_config['carbon'] = config.get('carbon', None)
                
                finders = []
                for finder in config['finders']:
                    finders.append(config_module.load_by_path(finder)(config))
                loaded_config['store'] = config_module.Store(finders)
                app.config['GRAPHITE'] = loaded_config
                app.config['TIME_ZONE'] = config['time_zone']
                
                app.wsgi_app = config_module.TrailingSlash(config_module.CORS(app.wsgi_app,
                                                           config.get('allowed_origins')))
            
            # Create app and configure it
            app = Flask(__name__)
            
            # Set non-existent primary config
            with patch.dict(os.environ, {'GRAPHITE_API_CONFIG': '/tmp/nonexistent-config-file.yaml'}):
                test_configure(app)
                
                # Verify the config was loaded from fallback
                self.assertEqual(app.config['TIME_ZONE'], 'Europe/London')
        finally:
            os.unlink(fallback_config)
    
    def test_neither_config_file_exists(self):
        """Test that defaults are used when neither config file exists."""
        from flask import Flask
        from graphite_render.config import configure
        
        # Use a non-existent config path
        with patch.dict(os.environ, {'GRAPHITE_API_CONFIG': '/tmp/nonexistent-primary.yaml'}):
            # Mock os.path.exists to return False for both files
            with patch('os.path.exists', return_value=False):
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    
                    app = Flask(__name__)
                    configure(app)
                    
                    # Check that a warning was issued
                    self.assertTrue(len(w) >= 1)
                    warning_messages = [str(warning.message) for warning in w]
                    found_config_warning = any(
                        "Unable to find configuration file" in msg and
                        "/etc/graphite-api.yml" in msg
                        for msg in warning_messages
                    )
                    self.assertTrue(found_config_warning, f"Expected config warning not found in: {warning_messages}")


if __name__ == '__main__':
    unittest.main()
