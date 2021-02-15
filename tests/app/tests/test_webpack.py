import json
import os
import time
from subprocess import call
from threading import Thread
from unittest import skipIf

import django
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.views.generic.base import TemplateView
from django_jinja.builtins import DEFAULT_EXTENSIONS

from webpack_loader.exceptions import (
    WebpackError,
    WebpackLoaderBadStatsError,
    WebpackLoaderTimeoutError,
    WebpackBundleLookupError
)
from webpack_loader.utils import get_loader

BUNDLE_PATH = os.path.join(settings.BASE_DIR, 'assets/bundles/')
DEFAULT_CONFIG = 'DEFAULT'


# noinspection PyMethodMayBeStatic
class LoaderTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def compile_bundles(self, config, wait=None):
        if wait:
            time.sleep(wait)
        call(['./node_modules/.bin/webpack', '--config', config])

    @skipIf(django.VERSION < (1, 7), 'not supported in this django version')
    def test_config_check(self):
        from webpack_loader.apps import webpack_cfg_check
        from webpack_loader.errors import BAD_CONFIG_ERROR

        with self.settings(WEBPACK_LOADER={
            'BUNDLE_DIR_NAME': 'bundles/',
            'STATS_FILE': 'webpack-stats.json',
        }):
            errors = webpack_cfg_check(None)
            expected_errors = [BAD_CONFIG_ERROR]
            self.assertEqual(errors, expected_errors)

        with self.settings(WEBPACK_LOADER={
            'DEFAULT': {}
        }):
            errors = webpack_cfg_check(None)
            expected_errors = []
            self.assertEqual(errors, expected_errors)

    def test_simple_and_css_extract(self):
        self.compile_bundles('webpack.config.simple.js')
        assets = get_loader(DEFAULT_CONFIG).get_assets()
        self.assertEqual(assets['status'], 'done')
        self.assertIn('chunks', assets)

        chunks = assets['chunks']
        self.assertIn('main', chunks)
        self.assertEqual(len(chunks), 1)

        main = chunks['main']
        self.assertEqual(main[0]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/main.css'))
        self.assertEqual(main[1]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/main.js'))

    def test_js_gzip_extract(self):
        self.compile_bundles('webpack.config.gzipTest.js')
        assets = get_loader(DEFAULT_CONFIG).get_assets()
        self.assertEqual(assets['status'], 'done')
        self.assertIn('chunks', assets)

        chunks = assets['chunks']
        self.assertIn('main', chunks)
        self.assertEqual(len(chunks), 1)

        main = chunks['main']
        self.assertEqual(main[0]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/main.css'))
        self.assertEqual(main[1]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/main.js.gz'))

    def test_static_url(self):
        self.compile_bundles('webpack.config.publicPath.js')
        assets = get_loader(DEFAULT_CONFIG).get_assets()
        self.assertEqual(assets['status'], 'done')
        self.assertEqual(assets['publicPath'], 'http://custom-static-host.com/')

    def test_templatetags(self):
        self.compile_bundles('webpack.config.simple.js')
        self.compile_bundles('webpack.config.app2.js')
        view = TemplateView.as_view(template_name='home.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn('<link type="text/css" href="/static/bundles/main.css" rel="stylesheet" />',
            result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/main.js" async charset="UTF-8"></script>',
            result.rendered_content)

        self.assertIn('<link type="text/css" href="/static/bundles/app2.css" rel="stylesheet" />',
            result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/app2.js" ></script>',
            result.rendered_content)
        self.assertIn('<img src="/static/bundles/assets/my-image.png" alt="my-image"/>', result.rendered_content)

        view = TemplateView.as_view(template_name='only_files.html')
        result = view(request)
        self.assertIn("var contentCss = '/static/bundles/main.css'", result.rendered_content)
        self.assertIn("var contentJS = '/static/bundles/main.js'", result.rendered_content)

        self.compile_bundles('webpack.config.publicPath.js')
        view = TemplateView.as_view(template_name='home.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn('<img src="http://custom-static-host.com/assets/my-image.png" alt="my-image"/>', result.rendered_content)

        self.compile_bundles('webpack.config.multipleEntrypoints.js')
        view = TemplateView.as_view(template_name='main_entrypoint.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn('<link type="text/css" href="/static/bundles/main.css" rel="stylesheet" />',
            result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/main.js" ></script>',
            result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/runtime.js" ></script>',
            result.rendered_content)

        view = TemplateView.as_view(template_name='another_entrypoint.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn('<link type="text/css" href="/static/bundles/another_entrypoint.css" rel="stylesheet" />',
            result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/another_entrypoint.js" ></script>',
            result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/runtime.js" ></script>',
            result.rendered_content)

    def test_exclude_runtime(self):
        self.compile_bundles('webpack.config.multipleEntrypoints.js')
        view = TemplateView.as_view(template_name='main_template_exclude_runtime.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn('<link type="text/css" href="/static/bundles/main.css" rel="stylesheet" />',
            result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/main.js" ></script>',
            result.rendered_content)
        self.assertNotIn('<script type="text/javascript" src="/static/bundles/runtime.js" ></script>',
            result.rendered_content)

    def test_get_entrypoint_extension_filtering(self):
        self.compile_bundles('webpack.config.multipleEntrypoints.js')
        view = TemplateView.as_view(template_name='main_entrypoint_js_only.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertNotIn('<link type="text/css" href="/static/bundles/main.css" rel="stylesheet" />',
            result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/main.js" ></script>',
            result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/runtime.js" ></script>',
            result.rendered_content)

    def test_jinja2(self):
        self.compile_bundles('webpack.config.simple.js')
        self.compile_bundles('webpack.config.app2.js')
        view = TemplateView.as_view(template_name='home.jinja')

        if django.VERSION >= (1, 8):
            settings_ = {
                'TEMPLATES': [
                    {
                        "BACKEND": "django_jinja.backend.Jinja2",
                        "APP_DIRS": True,
                        "OPTIONS": {
                            "match_extension": ".jinja",
                            "extensions": DEFAULT_EXTENSIONS + [
                                "webpack_loader.contrib.jinja2ext.WebpackExtension",
                            ]
                        }
                    },
                ]
            }
        else:
            settings_ = {
                'TEMPLATE_LOADERS': (
                    'django_jinja.loaders.FileSystemLoader',
                    'django_jinja.loaders.AppLoader',
                ),
            }
        with self.settings(**settings_):
            request = self.factory.get('/')
            result = view(request)
            self.assertIn('<link type="text/css" href="/static/bundles/main.css" rel="stylesheet" />',
                result.rendered_content)
            self.assertIn(
                '<script type="text/javascript" src="/static/bundles/main.js" async charset="UTF-8"></script>',
                result.rendered_content)

        self.compile_bundles('webpack.config.multipleEntrypoints.js')
        view = TemplateView.as_view(template_name='main_entrypoint.jinja')
        with self.settings(**settings_):
            request = self.factory.get('/')
            result = view(request)
            self.assertIn('<link type="text/css" href="/static/bundles/main.css" rel="stylesheet" />',
                result.rendered_content)
            self.assertIn(
                '<script type="text/javascript" src="/static/bundles/main.js" async charset="UTF-8"></script>',
                result.rendered_content)

    def test_reporting_errors(self):
        self.compile_bundles('webpack.config.error.js')
        try:
            get_loader(DEFAULT_CONFIG).get_bundle('main')
        except WebpackError as e:
            self.assertIn("Can't resolve 'the-library-that-did-not-exist'", str(e))

    def test_missing_bundle(self):
        missing_bundle_name = 'missing_bundle'
        self.compile_bundles('webpack.config.simple.js')
        try:
            get_loader(DEFAULT_CONFIG).get_bundle(missing_bundle_name)
        except WebpackBundleLookupError as e:
            self.assertIn('Cannot resolve bundle {0}'.format(missing_bundle_name), str(e))

    def test_missing_entrypoint(self):
        missing_bundle_name = 'missing_entrypoint'
        self.compile_bundles('webpack.config.multipleEntrypoints.js')
        try:
            get_loader(DEFAULT_CONFIG).get_entry(missing_bundle_name)
        except WebpackBundleLookupError as e:
            self.assertIn('Cannot resolve entry {0}'.format(missing_bundle_name), str(e))

    def test_missing_stats_file(self):
        stats_file = settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE']
        if os.path.exists(stats_file):
            os.remove(stats_file)
        try:
            get_loader(DEFAULT_CONFIG).get_assets()
        except IOError as e:
            expected = (
                'Error reading {0}. Are you sure webpack has generated the '
                'file and the path is correct?'
            ).format(stats_file)
            self.assertIn(expected, str(e))

    def test_timeouts(self):
        with self.settings(DEBUG=True):
            with open(
                    settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE'], 'w'
            ) as stats_file:
                stats_file.write(json.dumps({'status': 'compiling'}))
            loader = get_loader(DEFAULT_CONFIG)
            loader.config['TIMEOUT'] = 0.1
            with self.assertRaises(WebpackLoaderTimeoutError):
                loader.get_bundle('main')

    def test_bad_status_in_production(self):
        with open(
                settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE'], 'w'
        ) as stats_file:
            stats_file.write(json.dumps({'status': 'unexpected-status'}))

        try:
            get_loader(DEFAULT_CONFIG).get_bundle('main')
        except WebpackLoaderBadStatsError as e:
            self.assertIn((
                "The stats file does not contain valid data. Make sure "
                "webpack-bundle-tracker plugin is enabled and try to run"
                " webpack again."
            ), str(e))

    def test_request_blocking(self):
        # FIXME: This will work 99% time but there is no garauntee with the
        # 4 second thing. Need a better way to detect if request was blocked on
        # not.
        wait_for = 3
        view = TemplateView.as_view(template_name='home.html')

        with self.settings(DEBUG=True):
            open(settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE'], 'w').write(json.dumps({'status': 'compiling'}))
            then = time.time()
            request = self.factory.get('/')
            result = view(request)
            t = Thread(target=self.compile_bundles, args=('webpack.config.simple.js', wait_for))
            t2 = Thread(target=self.compile_bundles, args=('webpack.config.app2.js', wait_for))
            t.start()
            t2.start()
            assert result.rendered_content
            elapsed = time.time() - then
            t.join()
            t2.join()
            self.assertTrue(elapsed >= wait_for)

        with self.settings(DEBUG=False):
            self.compile_bundles('webpack.config.simple.js')
            self.compile_bundles('webpack.config.app2.js')
            then = time.time()
            request = self.factory.get('/')
            result = view(request)
            assert result.rendered_content
            elapsed = time.time() - then
            self.assertTrue(elapsed < wait_for)
