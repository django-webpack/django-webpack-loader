import re
import json
import time

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


__all__ = ('get_bundle',)


config = {
    'BUNDLE_DIR_NAME': 'webpack_bundles/',
    'STATS_FILE': 'webpack-stats.json',
    # FIXME: Explore usage of fsnotify
    'POLL_INTERVAL': 0.1,
    'IGNORE': ['.+\.hot-update.js', '.+\.map']
}

config.update(getattr(settings, 'WEBPACK_LOADER', {}))
ignores = [re.compile(I) for I in config['IGNORE']]


class WebpackException(BaseException):
    pass


def get_assets():
    try:
        return json.loads(open(config['STATS_FILE']).read())
    except IOError:
        raise IOError('Error reading {}. Are you sure webpack has generated '
                      'the file and the path is correct?'.format(config['STATS_FILE']))


def filter_files(files):
    for F in files:
        filename = F['name']
        ignore = any(regex.match(filename) for regex in ignores)
        if not ignore:
            relpath = '{}{}'.format(config['BUNDLE_DIR_NAME'], filename)
            F['url'] = staticfiles_storage.url(relpath)
            yield F


def get_bundle(bundle_name):
    assets = get_assets()

    if settings.DEBUG:
        # poll when debugging and block request until bundle is compiled
        # TODO: support timeouts
        while assets['status'] == 'compiling':
            time.sleep(config['POLL_INTERVAL'])
            assets = get_assets()

    if assets.get('status') == 'done':
        files = assets['chunks'][bundle_name]
        return filter_files(files)

    elif assets.get('status') == 'error':
        if 'file' not in assets:
            assets['file'] = ''
        error = """
        {error} in {file}
        {message}
        """.format(**assets)
        raise WebpackException(error)
