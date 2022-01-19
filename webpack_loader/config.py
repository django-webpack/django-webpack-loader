import re

from django.conf import settings

__all__ = ('load_config', )

DEFAULT_CONFIG = {
    'DEFAULT': {
        'CACHE': not settings.DEBUG,
        'CACHE_TTL': -1,
        'BUNDLE_DIR_NAME': 'webpack_bundles/',
        'STATS_FILE': 'webpack-stats.json',
        # FIXME: Explore usage of fsnotify
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'ASSETS_LOADER_FUNCTION': 'webpack_loader.utils.load_assets_from_filesystem',
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
        'LOADER_CLASS': 'webpack_loader.loader.WebpackLoader',
    }
}

user_specified_entries = getattr(settings, 'WEBPACK_LOADER', {'DEFAULT': {}})

user_config = dict((name, dict(DEFAULT_CONFIG['DEFAULT'], **cfg))
                   for name, cfg in user_specified_entries.items())

for entry in user_config.values():
    entry['ignores'] = [re.compile(I) for I in entry['IGNORE']]


def load_config(name):
    return user_config[name]
