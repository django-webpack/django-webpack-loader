import re
import json
import time

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


__all__ = ('get_assets', 'get_config', 'get_bundle',)


DEFAULT_CONFIG = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'webpack_bundles/',
        'STATS_FILE': 'webpack-stats.json',
        # FIXME: Explore usage of fsnotify
        'POLL_INTERVAL': 0.1,
        'IGNORE': ['.+\.hot-update.js', '.+\.map']
    }
}


user_config = getattr(settings, 'WEBPACK_LOADER', DEFAULT_CONFIG)

user_config = {
    name: dict(DEFAULT_CONFIG['DEFAULT'], **cfg)
    for name, cfg in user_config.items()
}

for entry in user_config.values():
    entry['ignores'] = [re.compile(I) for I in entry['IGNORE']]


class WebpackError(BaseException):
    pass


class WebpackLoaderBadStatsError(BaseException):
    pass


def get_config(config_name):
    return user_config[config_name]


def get_assets(config):
    try:
        return json.loads(open(config['STATS_FILE']).read())
    except IOError:
        raise IOError(
            'Error reading {}. Are you sure webpack has generated the file '
            'and the path is correct?'.format(config['STATS_FILE']))


def filter_files(files, config):
    for F in files:
        filename = F['name']
        ignore = any(regex.match(filename) for regex in config['ignores'])
        if not ignore:
            relpath = '{}{}'.format(config['BUNDLE_DIR_NAME'], filename)
            F['url'] = staticfiles_storage.url(relpath)
            yield F


def get_bundle(bundle_name, config):
    assets = get_assets(config)

    if settings.DEBUG:
        # poll when debugging and block request until bundle is compiled
        # TODO: support timeouts
        while assets['status'] == 'compiling':
            time.sleep(config['POLL_INTERVAL'])
            assets = get_assets(config)

    if assets.get('status') == 'done':
        files = assets['chunks'][bundle_name]
        return filter_files(files, config)

    elif assets.get('status') == 'error':
        if 'file' not in assets:
            assets['file'] = ''
        error = """
        {error} in {file}
        {message}
        """.format(**assets)
        raise WebpackError(error)

    raise WebpackLoaderBadStatsError(
        "The stats file does not contain valid data. Make sure "
        "webpack-bundle-tracker plugin is enabled and try to run "
        "webpack again.")
