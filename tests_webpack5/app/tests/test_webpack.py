import time
from shutil import rmtree
from subprocess import call

from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.views.generic.base import TemplateView


class LoaderTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.cleanup_bundles_folder()

    def cleanup_bundles_folder(self):
        rmtree('./assets/django_webpack_loader_bundles', ignore_errors=True)

    def compile_bundles(self, config, wait=None):
        if wait:
            time.sleep(wait)
        call(['./node_modules/.bin/webpack', '--config', config])

    def test_templatetags(self):
        self.compile_bundles('webpack.config.js')
        view = TemplateView.as_view(template_name='home.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn(
            '<a href="/static/assets/resource-3c9e4020d3e3c7a09c68.txt">Download resource</a>', result.rendered_content)
