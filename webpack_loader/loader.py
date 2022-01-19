import time
import os
from io import open

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.module_loading import import_string

from .exceptions import (
    WebpackError,
    WebpackLoaderBadStatsError,
    WebpackLoaderTimeoutError,
    WebpackBundleLookupError
)
from .config import load_config
import logging

logger = logging.getLogger(__name__)

class WebpackLoader(object):
    _assets = {}
    _cache_timestamp = 0

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def _load_assets(self):
        func_name = self.config['ASSETS_LOADER_FUNCTION']
        try:
            func = import_string(func_name)
        except ImportError as ie:
            raise WebpackError(
                "The ASSETS_LOADER_FUNCTION '{0}' specified in the {1} config "
                "could not be imported.".format(func_name, self.name))
        return func(self)

    def _is_cache_expired(self, now):
        cache_ttl = self.config['CACHE_TTL']
        if cache_ttl < 0:
            return False
        if now - self._cache_timestamp > cache_ttl:
            return True
        return False

    def get_assets(self):
        if self.config['CACHE']:
            now = int(time.time())
            if self._is_cache_expired(now) or self.name not in self._assets:
                logger.info('--- fetching webpack-stats: {}'.format(time.ctime()))
                self._assets[self.name] = self._load_assets()
                self._cache_timestamp = now
            return self._assets[self.name]
        return self._load_assets()

    def filter_chunks(self, chunks):
        filtered_chunks = []

        for chunk in chunks:
            ignore = any(regex.match(chunk)
                         for regex in self.config['ignores'])
            if not ignore:
                filtered_chunks.append(chunk)

        return filtered_chunks

    def map_chunk_files_to_url(self, chunks):
        assets = self.get_assets()
        files = assets['assets']

        for chunk in chunks:
            url = self.get_chunk_url(files[chunk])
            yield { 'name': chunk, 'url': url }

    def get_chunk_url(self, chunk_file):
        public_path = chunk_file.get('publicPath')
        if public_path:
            return public_path

        # Use os.path.normpath for Windows paths
        relpath = os.path.normpath(
            os.path.join(self.config['BUNDLE_DIR_NAME'], chunk_file['name'])
        )
        return staticfiles_storage.url(relpath)

    def get_bundle(self, bundle_name):
        assets = self.get_assets()

        # poll when debugging and block request until bundle is compiled
        # or the build times out
        if settings.DEBUG:
            timeout = self.config['TIMEOUT'] or 0
            timed_out = False
            start = time.time()
            while assets['status'] == 'compile' and not timed_out:
                time.sleep(self.config['POLL_INTERVAL'])
                if timeout and (time.time() - timeout > start):
                    timed_out = True
                assets = self.get_assets()

            if timed_out:
                raise WebpackLoaderTimeoutError(
                    "Timed Out. Bundle `{0}` took more than {1} seconds "
                    "to compile.".format(bundle_name, timeout)
                )

        if assets.get('status') == 'done':
            chunks = assets['chunks'].get(bundle_name, None)
            if chunks is None:
                raise WebpackBundleLookupError('Cannot resolve bundle {0}.'.format(bundle_name))

            filtered_chunks = self.filter_chunks(chunks)

            for chunk in filtered_chunks:
                asset = assets['assets'][chunk]
                if asset is None:
                    raise WebpackBundleLookupError('Cannot resolve asset {0}.'.format(chunk))

            return self.map_chunk_files_to_url(filtered_chunks)

        elif assets.get('status') == 'error':
            if 'file' not in assets:
                assets['file'] = ''
            if 'error' not in assets:
                assets['error'] = 'Unknown Error'
            if 'message' not in assets:
                assets['message'] = ''
            error = u"""
            {error} in {file}
            {message}
            """.format(**assets)
            raise WebpackError(error)

        raise WebpackLoaderBadStatsError(
            "The stats file does not contain valid data. Make sure "
            "webpack-bundle-tracker plugin is enabled and try to run "
            "webpack again.")
