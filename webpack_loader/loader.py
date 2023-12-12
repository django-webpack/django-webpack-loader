import json
import time
import os
from io import open

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

from .exceptions import (
    WebpackError,
    WebpackLoaderBadStatsError,
    WebpackLoaderTimeoutError,
    WebpackBundleLookupError,
)

try:
    from django.utils.six.moves.urllib import parse as urlparse
except ImportError:
    from urllib import parse as urlparse


class WebpackLoader(object):
    _assets = {}

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def load_assets(self):
        try:
            with open(self.config["STATS_FILE"], encoding="utf-8") as f:
                return json.load(f)
        except IOError:
            raise IOError(
                "Error reading {0}. Are you sure webpack has generated "
                "the file and the path is correct?".format(self.config["STATS_FILE"])
            )

    def get_assets(self):
        if self.config["CACHE"]:
            if self.name not in self._assets:
                self._assets[self.name] = self.load_assets()
            return self._assets[self.name]
        return self.load_assets()

    def filter_chunks(self, chunks):
        filtered_chunks = []

        for chunk in chunks:
            ignore = any(regex.match(chunk) for regex in self.config["ignores"])
            if not ignore:
                filtered_chunks.append(chunk)

        return filtered_chunks

    def map_chunk_files_to_url(self, chunks):
        assets = self.get_assets()
        files = assets["assets"]

        for chunk in chunks:
            url = self.get_chunk_url(files[chunk])
            yield {"name": chunk, "url": url}

    def get_chunk_url(self, chunk_file):
        public_path = chunk_file.get("publicPath")
        if public_path:
            return public_path

        # Use os.path.normpath for Windows paths
        relpath = os.path.normpath(
            os.path.join(self.config["BUNDLE_DIR_NAME"], chunk_file["name"])
        )
        return self._strip_signing_parameters(staticfiles_storage.url(relpath))

    def _strip_signing_parameters(self, url):
        # Boto3 does not currently support generating URLs that are unsigned. Instead we
        # take the signed URLs and strip any querystring params related to signing and expiration.
        # Note that this may end up with URLs that are still invalid, especially if params are
        # passed in that only work with signed URLs, e.g. response header params.
        # The code attempts to strip all query parameters that match names of known parameters
        # from v2 and v4 signatures, regardless of the actual signature version used.
        split_url = urlparse.urlsplit(url)
        qs = urlparse.parse_qsl(split_url.query, keep_blank_values=True)
        blacklist = {
            "x-amz-algorithm",
            "x-amz-credential",
            "x-amz-date",
            "x-amz-expires",
            "x-amz-signedheaders",
            "x-amz-signature",
            "x-amz-security-token",
            "awsaccesskeyid",
            "expires",
            "signature",
        }
        filtered_qs = ((key, val) for key, val in qs if key.lower() not in blacklist)
        # Note: Parameters that did not have a value in the original query string will have
        # an '=' sign appended to it, e.g ?foo&bar becomes ?foo=&bar=
        joined_qs = ("=".join(keyval) for keyval in filtered_qs)
        split_url = split_url._replace(query="&".join(joined_qs))
        return split_url.geturl()

    def get_bundle(self, bundle_name):
        assets = self.get_assets()

        # poll when debugging and block request until bundle is compiled
        # or the build times out
        if settings.DEBUG:
            timeout = self.config["TIMEOUT"] or 0
            timed_out = False
            start = time.time()
            while assets["status"] == "compile" and not timed_out:
                time.sleep(self.config["POLL_INTERVAL"])
                if timeout and (time.time() - timeout > start):
                    timed_out = True
                assets = self.get_assets()

            if timed_out:
                raise WebpackLoaderTimeoutError(
                    "Timed Out. Bundle `{0}` took more than {1} seconds "
                    "to compile.".format(bundle_name, timeout)
                )

        if assets.get("status") == "done":
            chunks = assets["chunks"].get(bundle_name, None)
            if chunks is None:
                raise WebpackBundleLookupError(
                    "Cannot resolve bundle {0}.".format(bundle_name)
                )

            filtered_chunks = self.filter_chunks(chunks)

            for chunk in filtered_chunks:
                asset = assets["assets"][chunk]
                if asset is None:
                    raise WebpackBundleLookupError(
                        "Cannot resolve asset {0}.".format(chunk)
                    )

            return self.map_chunk_files_to_url(filtered_chunks)

        elif assets.get("status") == "error":
            if "file" not in assets:
                assets["file"] = ""
            if "error" not in assets:
                assets["error"] = "Unknown Error"
            if "message" not in assets:
                assets["message"] = ""
            error = """
            {error} in {file}
            {message}
            """.format(
                **assets
            )
            raise WebpackError(error)

        raise WebpackLoaderBadStatsError(
            "The stats file does not contain valid data. Make sure "
            "webpack-bundle-tracker plugin is enabled and try to run "
            "webpack again."
        )
