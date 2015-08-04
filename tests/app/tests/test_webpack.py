import os
import time
import json
from subprocess import call
from threading import Thread

import django
from django.conf import settings
from django.test import TestCase, RequestFactory
from django_jinja.builtins import DEFAULT_EXTENSIONS
from django.views.generic.base import TemplateView

from webpack_loader.utils import get_assets, get_bundle, WebpackException


BUNDLE_PATH = os.path.join(settings.BASE_DIR, 'assets/bundles/')


class LoaderTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def clean_dir(self, directory):
        if os.path.exists(BUNDLE_PATH):
            [os.remove(os.path.join(BUNDLE_PATH, F)) for F in os.listdir(BUNDLE_PATH)]
        os.remove(settings.WEBPACK_LOADER['STATS_FILE'])

    def compile_bundles(self, config, wait=None):
        if wait:
            time.sleep(wait)
        call(['./node_modules/.bin/webpack', '--config', config])

    def test_simple_and_css_extract(self):
        self.compile_bundles('webpack.config.simple.js')
        assets = get_assets()
        self.assertEqual(assets['status'], 'done')
        self.assertIn('chunks', assets)

        chunks = assets['chunks']
        self.assertIn('main', chunks)
        self.assertEquals(len(chunks), 1)

        main = chunks['main']
        self.assertEqual(main[0]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/main.js'))
        self.assertEqual(main[1]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/styles.css'))

    def test_code_spliting(self):
        self.compile_bundles('webpack.config.split.js')
        assets = get_assets()
        self.assertEqual(assets['status'], 'done')
        self.assertIn('chunks', assets)

        chunks = assets['chunks']
        self.assertIn('main', chunks)
        self.assertEquals(len(chunks), 2)

        main = chunks['main']
        self.assertEqual(main[0]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/main.js'))

        vendor = chunks['vendor']
        self.assertEqual(vendor[0]['path'], os.path.join(settings.BASE_DIR, 'assets/bundles/vendor.js'))

    def test_django(self):
        self.compile_bundles('webpack.config.simple.js')
        view = TemplateView.as_view(template_name='home.html')

        different_domain_static_url = '//:derp.com/_/static/'

        with self.settings(STATIC_URL=different_domain_static_url):
            request = self.factory.get('/')
            result = view(request)
            self.assertIn('<link type="text/css" href="%sbundles/styles.css" rel="stylesheet">' % different_domain_static_url, result.rendered_content)
            self.assertIn('<script type="text/javascript" src="%sbundles/main.js"></script>' % different_domain_static_url, result.rendered_content)

    def test_django_defer_script_option(self):
        self.compile_bundles('webpack.config.simple.js')
        view = TemplateView.as_view(template_name='home.html')

        with self.settings(WEBPACK_LOADER={'DEFER': True}):
            request = self.factory.get('/')
            result = view(request)
            self.assertIn('defer', result.rendered_content)

        with self.settings():
            request = self.factory.get('/')
            result = view(request)
            self.assertNotIn('defer', result.rendered_content)

    def test_jinja2(self):
        self.compile_bundles('webpack.config.simple.js')
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
            self.assertIn('<link type="text/css" href="/static/bundles/styles.css" rel="stylesheet">', result.rendered_content)
            self.assertIn('<script type="text/javascript" src="/static/bundles/main.js"></script>', result.rendered_content)

    def test_reporting_errors(self):
        #TODO:
        self.compile_bundles('webpack.config.error.js')
        try:
            get_bundle('main')
        except WebpackException as e:
            self.assertIn("Cannot resolve module 'the-library-that-did-not-exist'", str(e))

    def test_missing_stats_file(self):
        os.remove(settings.WEBPACK_LOADER['STATS_FILE'])
        try:
            get_assets()
        except IOError as e:
            expected = 'Error reading {}. Are you sure webpack has generated the file and the path is correct?'.format(settings.WEBPACK_LOADER['STATS_FILE'])
            self.assertIn(expected, str(e))

    def test_request_blocking(self):
        # FIXME: This will work 99% time but there is no garauntee with the
        # 4 second thing. Need a better way to detect if request was blocked on
        # not.
        wait_for = 3
        view = TemplateView.as_view(template_name='home.html')

        with self.settings(DEBUG=True):
            open(settings.WEBPACK_LOADER['STATS_FILE'], 'w').write(json.dumps({'status': 'compiling'}))
            then = time.time()
            request = self.factory.get('/')
            result = view(request)
            t = Thread(target=self.compile_bundles, args=('webpack.config.simple.js', wait_for))
            t.start()
            result.rendered_content
            elapsed = time.time() - then
            t.join()
            self.assertTrue(elapsed > wait_for)

        with self.settings(DEBUG=False):
            self.compile_bundles('webpack.config.simple.js')
            then = time.time()
            request = self.factory.get('/')
            result = view(request)
            result.rendered_content
            elapsed = time.time() - then
            self.assertTrue(elapsed < wait_for)
