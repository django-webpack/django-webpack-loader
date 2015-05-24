import os
import time
import json
from subprocess import call
from threading import Thread

from django.conf import settings
from django.test import TestCase, RequestFactory
from webpack_loader.utils import get_assets
from django.views.generic.base import TemplateView


view = TemplateView.as_view(template_name='home.html')


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
        call(['./node_modules/.bin/webpack', '--config', os.path.join('assets/', config)])

    def test_request_blocking(self):
        # FIXME: This will work 99% time but there is no garauntee with the
        # 4 second thing. Need a better way to detect if request was blocked on
        # not.
        wait_for = 3

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

    def test_reporting_errors(self):
        #TODO:
        pass

    def test_simple(self):
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

    def test_multiple_files(self):
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
