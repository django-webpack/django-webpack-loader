import json
import os
import time
from subprocess import call
from threading import Thread

import django
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.views.generic.base import TemplateView
from django_jinja.builtins import DEFAULT_EXTENSIONS
from unittest2 import skipIf
from webpack_loader.utils import (WebpackError, WebpackLoaderBadStatsError,
                                  get_assets, get_bundle, get_config)

BUNDLE_PATH = os.path.join(settings.BASE_DIR, 'assets/bundles/')
DEFAULT_CONFIG = 'DEFAULT'

class LoaderTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def clean_dir(self, directory):
        if os.path.exists(BUNDLE_PATH):
            [os.remove(os.path.join(BUNDLE_PATH, F)) for F in os.listdir(BUNDLE_PATH)]
        os.remove(settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE'])

    def compile_bundles(self, config, wait=None):
        if wait:
            time.sleep(wait)
        call(['./node_modules/.bin/webpack', '--config', config])

    @skipIf(django.VERSION < (1, 7),
            'not supported in this django version')
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
        assets = get_assets(get_config(DEFAULT_CONFIG))
        self.assertEqual(assets['status'], 'done')
        self.assertIn('chunks', assets)

        chunks = assets['chunks']
        self.assertIn('main', chunks)
        self.assertEqual(len(chunks), 1)

        main = chunks['main']
        self.assertEqual(main[0]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/main.js'))
        self.assertEqual(main[1]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/styles.css'))

    def test_static_url(self):
        self.compile_bundles('webpack.config.publicPath.js')
        assets = get_assets(get_config(DEFAULT_CONFIG))
        self.assertEqual(assets['status'], 'done')
        self.assertEqual(assets['publicPath'], 'http://custom-static-host.com/')

    def test_code_spliting(self):
        self.compile_bundles('webpack.config.split.js')
        assets = get_assets(get_config(DEFAULT_CONFIG))
        self.assertEqual(assets['status'], 'done')
        self.assertIn('chunks', assets)

        chunks = assets['chunks']
        self.assertIn('main', chunks)
        self.assertEquals(len(chunks), 2)

        main = chunks['main']
        self.assertEqual(main[0]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/main.js'))

        vendor = chunks['vendor']
        self.assertEqual(vendor[0]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/vendor.js'))

    def test_templatetags(self):
        self.compile_bundles('webpack.config.simple.js')
        self.compile_bundles('webpack.config.app2.js')
        view = TemplateView.as_view(template_name='home.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn('<link type="text/css" href="/static/bundles/styles.css" rel="stylesheet"/>', result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/main.js"></script>', result.rendered_content)

        self.assertIn('<link type="text/css" href="/static/bundles/styles-app2.css" rel="stylesheet"/>', result.rendered_content)
        self.assertIn('<script type="text/javascript" src="/static/bundles/app2.js"></script>', result.rendered_content)
        self.assertIn('<img src="/static/my-image.png"/>', result.rendered_content)

        view = TemplateView.as_view(template_name='only_files.html')
        result = view(request)
        self.assertIn("var contentCss = '/static/bundles/styles.css'", result.rendered_content)
        self.assertIn("var contentJS = '/static/bundles/main.js'", result.rendered_content)

        self.compile_bundles('webpack.config.publicPath.js')
        view = TemplateView.as_view(template_name='home.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn('<img src="http://custom-static-host.com/my-image.png"/>', result.rendered_content)

    def test_jinja2(self):
        self.compile_bundles('webpack.config.simple.js')
        self.compile_bundles('webpack.config.app2.js')
        view = TemplateView.as_view(template_name='home.jinja')

        if django.VERSION >= (1, 8):
            settings = {
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
            settings = {
                'TEMPLATE_LOADERS': (
                    'django_jinja.loaders.FileSystemLoader',
                    'django_jinja.loaders.AppLoader',
                ),
            }
        with self.settings(**settings):
            request = self.factory.get('/')
            result = view(request)
            self.assertIn('<link type="text/css" href="/static/bundles/styles.css" rel="stylesheet"/>', result.rendered_content)
            self.assertIn('<script type="text/javascript" src="/static/bundles/main.js"></script>', result.rendered_content)

    def test_reporting_errors(self):
        #TODO:
        self.compile_bundles('webpack.config.error.js')
        try:
            get_bundle('main', get_config(DEFAULT_CONFIG))
        except WebpackError as e:
            self.assertIn("Cannot resolve module 'the-library-that-did-not-exist'", str(e))

    def test_missing_stats_file(self):
        os.remove(settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE'])
        try:
            get_assets(get_config(DEFAULT_CONFIG))
        except IOError as e:
            expected = 'Error reading {0}. Are you sure webpack has generated the file and the path is correct?'.format(settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE'])
            self.assertIn(expected, str(e))

    def test_bad_status_in_production(self):
        stats_file = open(
            settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE'], 'w'
        )
        stats_file.write(json.dumps({'status': 'unexpected-status'}))
        stats_file.close()
        try:
            get_bundle('main', get_config(DEFAULT_CONFIG))
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
            result.rendered_content
            elapsed = time.time() - then
            t.join()
            t2.join()
            self.assertTrue(elapsed > wait_for)

        with self.settings(DEBUG=False):
            self.compile_bundles('webpack.config.simple.js')
            self.compile_bundles('webpack.config.app2.js')
            then = time.time()
            request = self.factory.get('/')
            result = view(request)
            result.rendered_content
            elapsed = time.time() - then
            self.assertTrue(elapsed < wait_for)

