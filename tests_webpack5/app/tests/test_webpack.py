import time
from shutil import rmtree
from subprocess import call
from unittest.mock import patch

from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.views.generic.base import TemplateView

from webpack_loader.utils import get_loader, get_as_url_to_tag_dict

DEFAULT_CONFIG = 'DEFAULT'

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

    def test_integrity(self):
        self.compile_bundles('webpack.config.integrity.js')

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {'INTEGRITY': True, 'CACHE': False}):
            view = TemplateView.as_view(template_name='home.html')
            request = self.factory.get('/')
            result = view(request)

            self.assertIn((
                '<script src="http://custom-static-host.com/resources.js" '
                'integrity="sha256-tq+bx/AOKBO9HvojLMT+nwLvdzX5q9s5hGI8sJr'
                'V+6Q= sha384-MQ3aER73Wrl5JjMLWVotKhBZk4e9/67+xrO8/qqACm7a'
                '695zI9sgQKa6bC54TMvb sha512-dKT17sF4HfpJC+UMIjQch07waKpAt'
                'Tvv9GM2s/eGomGDbCKpKHGp29+6SRrQSrT2+6IF3YGu3BaoQAoAS4opOQ==" '
                '></script>'), result.rendered_content)

    def test_integrity_with_crossorigin_empty(self):
        self.compile_bundles('webpack.config.integrity.js')

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {'INTEGRITY': True, 'CROSSORIGIN': '', 'CACHE': False}):
            view = TemplateView.as_view(template_name='home.html')
            request = self.factory.get('/')
            request.META['HTTP_HOST'] = 'crossorigin-custom-static-host.com'
            result = view(request)

            self.assertIn((
                '<script src="http://custom-static-host.com/resources.js" '
                'integrity="sha256-tq+bx/AOKBO9HvojLMT+nwLvdzX5q9s5hGI8sJr'
                'V+6Q= sha384-MQ3aER73Wrl5JjMLWVotKhBZk4e9/67+xrO8/qqACm7a'
                '695zI9sgQKa6bC54TMvb sha512-dKT17sF4HfpJC+UMIjQch07waKpAt'
                'Tvv9GM2s/eGomGDbCKpKHGp29+6SRrQSrT2+6IF3YGu3BaoQAoAS4opOQ==" '
                'crossorigin ></script>'
            ), result.rendered_content)

    def test_integrity_with_crossorigin_anonymous(self):
        self.compile_bundles('webpack.config.integrity.js')

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {'INTEGRITY': True, 'CROSSORIGIN': 'anonymous', 'CACHE': False}):
            view = TemplateView.as_view(template_name='home.html')
            request = self.factory.get('/')
            request.META['HTTP_HOST'] = 'crossorigin-custom-static-host.com'
            result = view(request)

            self.assertIn((
                '<script src="http://custom-static-host.com/resources.js" '
                'integrity="sha256-tq+bx/AOKBO9HvojLMT+nwLvdzX5q9s5hGI8sJr'
                'V+6Q= sha384-MQ3aER73Wrl5JjMLWVotKhBZk4e9/67+xrO8/qqACm7a'
                '695zI9sgQKa6bC54TMvb sha512-dKT17sF4HfpJC+UMIjQch07waKpAt'
                'Tvv9GM2s/eGomGDbCKpKHGp29+6SRrQSrT2+6IF3YGu3BaoQAoAS4opOQ==" '
                'crossorigin="anonymous" ></script>'
            ), result.rendered_content)

    def test_integrity_with_crossorigin_use_credentials(self):
        self.compile_bundles('webpack.config.integrity.js')

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {'INTEGRITY': True, 'CROSSORIGIN': 'use-credentials', 'CACHE': False}):
            view = TemplateView.as_view(template_name='home.html')
            request = self.factory.get('/')
            request.META['HTTP_HOST'] = 'crossorigin-custom-static-host.com'
            result = view(request)

            self.assertIn((
                '<script src="http://custom-static-host.com/resources.js" '
                'integrity="sha256-tq+bx/AOKBO9HvojLMT+nwLvdzX5q9s5hGI8sJr'
                'V+6Q= sha384-MQ3aER73Wrl5JjMLWVotKhBZk4e9/67+xrO8/qqACm7a'
                '695zI9sgQKa6bC54TMvb sha512-dKT17sF4HfpJC+UMIjQch07waKpAt'
                'Tvv9GM2s/eGomGDbCKpKHGp29+6SRrQSrT2+6IF3YGu3BaoQAoAS4opOQ==" '
                'crossorigin="use-credentials" ></script>'
            ), result.rendered_content)

    def test_get_url_to_tag_dict_with_nonce(self):
        """Test the get_as_url_to_tag_dict function with nonce attribute handling."""

        self.compile_bundles('webpack.config.js')

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {"CSP_NONCE": True, 'CACHE': False}):
            # Create a request with csp_nonce
            request = self.factory.get('/')
            request.csp_nonce = "test-nonce-123"

            # Get tag dict with nonce enabled
            tag_dict = get_as_url_to_tag_dict('resources', extension='js', attrs='', request=request)
            # Verify nonce is in the tag
            self.assertIn('nonce="test-nonce-123"', tag_dict['/static/django_webpack_loader_bundles/resources.js'])

            # Test with existing nonce in attrs - should not duplicate
            tag_dict = get_as_url_to_tag_dict('resources', extension='js', attrs='nonce="existing-nonce"', request=request)
            self.assertIn('nonce="existing-nonce"', tag_dict['/static/django_webpack_loader_bundles/resources.js'])
            self.assertNotIn('nonce="test-nonce-123"', tag_dict['/static/django_webpack_loader_bundles/resources.js'])

            # Test without request - should not have nonce
            tag_dict = get_as_url_to_tag_dict('resources', extension='js', attrs='', request=None)
            self.assertNotIn('nonce=', tag_dict['/static/django_webpack_loader_bundles/resources.js'])

            # Test with request but no csp_nonce attribute - should not have nonce
            request_without_nonce = self.factory.get('/')
            tag_dict = get_as_url_to_tag_dict('resources', extension='js', attrs='', request=request_without_nonce)
            self.assertNotIn('nonce=', tag_dict['/static/django_webpack_loader_bundles/resources.js'])

    def test_get_url_to_tag_dict_with_nonce_disabled(self):
        self.compile_bundles('webpack.config.js')

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {"CSP_NONCE": False, 'CACHE': False}):
            # Create a request without csp_nonce
            request = self.factory.get('/')

            # should not have nonce
            tag_dict = get_as_url_to_tag_dict('resources', extension='js', attrs='', request=request)
            self.assertNotIn('nonce=', tag_dict['/static/django_webpack_loader_bundles/resources.js'])

            # Create a request with csp_nonce
            request_with_nonce = self.factory.get('/')
            request_with_nonce.csp_nonce = "test-nonce-123"

            # Test with CSP_NONCE disabled - should not have nonce
            tag_dict = get_as_url_to_tag_dict('resources', extension='js', attrs='', request=request_with_nonce)
            self.assertNotIn('nonce=', tag_dict['/static/django_webpack_loader_bundles/resources.js'])
