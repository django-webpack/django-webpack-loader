import json
import time
from io import open

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

from .exceptions import (
    WebpackError,
    WebpackLoaderBadStatsError,
    WebpackLoaderTimeoutError,
    WebpackBundleLookupError
)
from .config import load_config


class WebpackLoader(object):
    _assets = {}

    def __init__(self, name='DEFAULT'):
        self.name = name
        self.config = load_config(self.name)

    def _load_assets(self):
        try:
            with open(self.config['STATS_FILE'], encoding="utf-8") as f:
                return json.load(f)
        except IOError:
            raise IOError(
                'Error reading {0}. Are you sure webpack has generated '
                'the file and the path is correct?'.format(
                    self.config['STATS_FILE']))

    def get_assets(self):
        if self.config['CACHE']:
            if self.name not in self._assets:
                self._assets[self.name] = self._load_assets()
            return self._assets[self.name]
        return self._load_assets()

    def filter_chunks(self, chunks):
        for chunk in chunks:
            ignore = any(regex.match(chunk['name'])
                         for regex in self.config['ignores'])
            if not ignore:
                chunk['url'] = self.get_chunk_url(chunk)
                yield chunk

    def filter_chunks_auto(self, chunks):
        for key, value in chunks.items():
            for chunk in chunks[key]:
                ignore = any(regex.match(chunk['name'])
                             for regex in self.config['ignores'])
                if not ignore:
                    chunk['url'] = self.get_chunk_url(chunk)
                    yield chunk

    def get_chunk_url(self, chunk):
        public_path = chunk.get('publicPath')
        if public_path:
            return public_path

        relpath = '{0}{1}'.format(
            self.config['BUNDLE_DIR_NAME'], chunk['name']
        )
        return staticfiles_storage.url(relpath)

    def get_bundle(self, bundle_name, mode):
        assets = self.get_assets()

        # poll when debugging and block request until bundle is compiled
        # or the build times out
        if settings.DEBUG:
            timeout = self.config['TIMEOUT'] or 0
            timed_out = False
            start = time.time()
            while assets['status'] == 'compiling' and not timed_out:
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
            if mode == 'auto':
                chunks = {}
                search_chunks = assets['chunks']
                for chunk in search_chunks.keys():
                    split_chunk = chunk.split('~')

                    # the last module name might have a hash appended.  assume dash separator and strip it off
                    last_chunk = split_chunk.pop()
                    if bundle_name in split_chunk + [last_chunk.split("-")[0]]:
                        chunks.update({chunk: search_chunks[chunk]})
            else:
                chunks = assets['chunks'].get(bundle_name, None)
            if chunks is None:
                raise WebpackBundleLookupError('Cannot resolve bundle {0}.'.format(bundle_name))
            if mode == 'auto':
                return self.filter_chunks_auto(chunks)
            return self.filter_chunks(chunks)

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
