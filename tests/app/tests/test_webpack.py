import json
import os
import time
from shutil import rmtree
from subprocess import call
from threading import Thread
from unittest.mock import Mock
from unittest.mock import call as MockCall
from unittest.mock import patch

from django.conf import settings
from django.template import Context, Template, engines
from django.template.response import TemplateResponse
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.views.generic.base import TemplateView
from django_jinja.backend import Jinja2
from django_jinja.backend import Template as Jinja2Template
from django_jinja.builtins import DEFAULT_EXTENSIONS

from webpack_loader.exceptions import (WebpackBundleLookupError, WebpackError,
                                       WebpackLoaderBadStatsError,
                                       WebpackLoaderTimeoutError)
from webpack_loader.templatetags.webpack_loader import _WARNING_MESSAGE
from webpack_loader.utils import get_as_tags, get_loader

BUNDLE_PATH = os.path.join(
    settings.BASE_DIR, 'assets/django_webpack_loader_bundles/')
DEFAULT_CONFIG = 'DEFAULT'
_OUR_EXTENSION = 'webpack_loader.contrib.jinja2ext.WebpackExtension'


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

    def test_config_check(self):
        from webpack_loader.apps import webpack_cfg_check
        from webpack_loader.errors import BAD_CONFIG_ERROR

        with self.settings(WEBPACK_LOADER={
            'BUNDLE_DIR_NAME': 'django_webpack_loader_bundles/',
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

        files = assets['assets']
        self.assertEqual(
            files['main.css']['path'],
            os.path.join(
                settings.BASE_DIR,
                'assets/django_webpack_loader_bundles/main.css'))
        self.assertEqual(
            files['main.js']['path'],
            os.path.join(
                settings.BASE_DIR,
                'assets/django_webpack_loader_bundles/main.js'))

    def test_default_ignore_config_ignores_map_files(self):
        self.compile_bundles('webpack.config.sourcemaps.js')
        chunks = get_loader('NO_IGNORE_APP').get_bundle('main')
        has_map_files_chunks = \
            any(['.map' in chunk['name'] for chunk in chunks])

        self.assertTrue(has_map_files_chunks)

        chunks = get_loader(DEFAULT_CONFIG).get_bundle('main')
        has_map_files_chunks = \
            any(['.map' in chunk['name'] for chunk in chunks])

        self.assertFalse(has_map_files_chunks)

    def test_js_gzip_extract(self):
        self.compile_bundles('webpack.config.gzipTest.js')
        assets = get_loader(DEFAULT_CONFIG).get_assets()
        self.assertEqual(assets['status'], 'done')
        self.assertIn('chunks', assets)

        chunks = assets['chunks']
        self.assertIn('main', chunks)
        self.assertEqual(len(chunks), 1)

        files = assets['assets']
        self.assertEqual(
            files['main.css']['path'],
            os.path.join(
                settings.BASE_DIR,
                'assets/django_webpack_loader_bundles/main.css'))
        self.assertEqual(
            files['main.js.gz']['path'],
            os.path.join(
                settings.BASE_DIR,
                'assets/django_webpack_loader_bundles/main.js.gz'))

    def test_static_url(self):
        self.compile_bundles('webpack.config.publicPath.js')
        assets = get_loader(DEFAULT_CONFIG).get_assets()
        self.assertEqual(assets['status'], 'done')
        self.assertEqual(assets['publicPath'],
                         'http://custom-static-host.com/')

    def test_code_spliting(self):
        self.compile_bundles('webpack.config.split.js')
        assets = get_loader(DEFAULT_CONFIG).get_assets()
        self.assertEqual(assets['status'], 'done')
        self.assertIn('chunks', assets)

        chunks = assets['chunks']
        self.assertIn('main', chunks)
        self.assertEqual(len(chunks), 1)

        files = assets['assets']
        self.assertEqual(files['main.js']['path'], os.path.join(
            settings.BASE_DIR, 'assets/django_webpack_loader_bundles/main.js'))
        self.assertEqual(files['vendors.js']['path'], os.path.join(
            settings.BASE_DIR,
            'assets/django_webpack_loader_bundles/vendors.js'))

    def test_templatetags(self):
        self.compile_bundles('webpack.config.simple.js')
        self.compile_bundles('webpack.config.app2.js')
        self.compile_bundles('webpack.config.getFiles.js')
        view = TemplateView.as_view(template_name='home.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn((
            '<link href="/static/django_webpack_loader_bundles/main.css" '
            'rel="stylesheet" />'),
            result.rendered_content)
        self.assertIn((
            '<script src="/static/django_webpack_loader_bundles/main.js" '
            'async charset="UTF-8"></script>'), result.rendered_content)

        self.assertIn((
            '<link href="/static/django_webpack_loader_bundles/app2.css" '
            'rel="stylesheet" />'), result.rendered_content)
        self.assertIn((
            '<script src="/static/django_webpack_loader_bundles/app2.js" >'
            '</script>'), result.rendered_content)
        self.assertIn(
            '<img src="/static/my-image.png"/>', result.rendered_content)

        self.assertIn('<li>All from getFiles already rendered</li>', result.rendered_content)

        request = self.factory.get('/')
        view = TemplateView.as_view(template_name='only_files.html')
        result = view(request)
        self.assertIn((
            "var contentCss = "
            "'/static/django_webpack_loader_bundles/main.css'"),
            result.rendered_content)
        self.assertIn(
            "var contentJS = '/static/django_webpack_loader_bundles/main.js'",
            result.rendered_content)

        self.compile_bundles('webpack.config.publicPath.js')
        request = self.factory.get('/')
        view = TemplateView.as_view(template_name='home.html')
        request = self.factory.get('/')
        result = view(request)
        self.assertIn(
            '<img src="http://custom-static-host.com/my-image.png"/>',
            result.rendered_content)

    def test_preload(self):
        self.compile_bundles('webpack.config.simple.js')
        view = TemplateView.as_view(template_name='preload.html')
        request = self.factory.get('/')
        result = view(request)

        # Preload
        self.assertIn((
            '<link href="/static/django_webpack_loader_bundles/main.css" '
            'rel="preload" as="style" />'), result.rendered_content)
        self.assertIn((
            '<link rel="preload" as="script" href="/static/'
            'django_webpack_loader_bundles/main.js" />'),
            result.rendered_content)

        # Resources
        self.assertIn((
            '<link href="/static/django_webpack_loader_bundles/main.css" '
            'rel="stylesheet" />'), result.rendered_content)
        self.assertIn((
            '<script src="/static/django_webpack_loader_bundles/main.js" >'
            '</script>'), result.rendered_content)

    def test_integrity(self):
        self.compile_bundles('webpack.config.integrity.js')

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {'INTEGRITY': True}):
            view = TemplateView.as_view(template_name='single.html')
            request = self.factory.get('/')
            result = view(request)

            self.assertIn((
                '<script src="/static/django_webpack_loader_bundles/main.js" '
                'integrity="sha256-1wgFMxcDlOWYV727qRvWNoPHdnOGFNVMLuKd25cjR+o=" >'
                '</script>'), result.rendered_content)
            self.assertIn((
                '<link href="/static/django_webpack_loader_bundles/main.css" rel="stylesheet" '
                'integrity="sha256-cYWwRvS04/VsttQYx4BalKYrBDuw5t8vKFhWB/LKX30=" />'),
                result.rendered_content
            )

    def test_integrity_missing_config(self):
        self.compile_bundles('webpack.config.integrity.js')

        loader = get_loader(DEFAULT_CONFIG)
        # remove INTEGRITY from config completely to test backward compatibility
        integrity_from_config = loader.config.pop('INTEGRITY')

        view = TemplateView.as_view(template_name='single.html')
        request = self.factory.get('/')
        result = view(request)

        self.assertIn((
            '<script src="/static/django_webpack_loader_bundles/main.js" >'
            '</script>'), result.rendered_content
        )
        self.assertIn((
            '<link href="/static/django_webpack_loader_bundles/main.css" rel="stylesheet" />'),
            result.rendered_content
        )

        # return removed key
        loader.config['INTEGRITY'] = integrity_from_config

    def test_integrity_missing_hash(self):
        self.compile_bundles('webpack.config.simple.js')

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {'INTEGRITY': True}), self.assertRaises(WebpackLoaderBadStatsError):
            view = TemplateView.as_view(template_name='single.html')
            request = self.factory.get('/')
            str(view(request).rendered_content)

    def test_append_extensions(self):
        self.compile_bundles('webpack.config.gzipTest.js')
        view = TemplateView.as_view(template_name='append_extensions.html')
        request = self.factory.get('/')
        result = view(request)

        self.assertIn((
            '<script src="/static/django_webpack_loader_bundles/main.js.gz" >'
            '</script>'), result.rendered_content)

    def test_jinja2(self):
        self.compile_bundles('webpack.config.simple.js')
        self.compile_bundles('webpack.config.app2.js')
        view = TemplateView.as_view(template_name='home.jinja')

        settings = {
            'TEMPLATES': [
                {
                    'BACKEND': 'django_jinja.backend.Jinja2',
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'match_extension': '.jinja',
                        'extensions': DEFAULT_EXTENSIONS + [_OUR_EXTENSION],
                    }
                },
            ]
        }
        with self.settings(**settings):
            request = self.factory.get('/')
            result = view(request)
            self.assertIn((
                '<link href="/static/django_webpack_loader_bundles'
                '/main.css" rel="stylesheet" />'), result.rendered_content)
            self.assertIn((
                '<script src="/static/django_webpack_loader_bundles/main.js" '
                'async charset="UTF-8"></script>'), result.rendered_content)

    def test_reporting_errors(self):
        self.compile_bundles('webpack.config.error.js')
        try:
            get_loader(DEFAULT_CONFIG).get_bundle('main')
        except WebpackError as e:
            self.assertIn(
                "Can't resolve 'the-library-that-did-not-exist'", str(e))

    def test_missing_bundle(self):
        missing_bundle_name = 'missing_bundle'
        self.compile_bundles('webpack.config.simple.js')
        try:
            get_loader(DEFAULT_CONFIG).get_bundle(missing_bundle_name)
        except WebpackBundleLookupError as e:
            self.assertIn(
                'Cannot resolve bundle {0}'.format(missing_bundle_name),
                str(e))

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
            statsfile = settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE']
            with open(statsfile, 'w') as fd:
                fd.write(json.dumps({'status': 'compile'}))
            loader = get_loader(DEFAULT_CONFIG)
            loader.config['TIMEOUT'] = 0.1
            with self.assertRaises(WebpackLoaderTimeoutError):
                loader.get_bundle('main')

    def test_bad_status_in_production(self):
        statsfile = settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE']
        with open(statsfile, 'w') as fd:
            fd.write(json.dumps({'status': 'unexpected-status'}))

        try:
            get_loader(DEFAULT_CONFIG).get_bundle('main')
        except WebpackLoaderBadStatsError as e:
            self.assertIn((
                "The stats file does not contain valid data. Make sure "
                "webpack-bundle-tracker plugin is enabled and try to run"
                " webpack again."
            ), str(e))

    def test_request_blocking(self):
        # FIXME: This will work 99% time but there is no guarantee with the
        # 4 second thing. Need a better way to detect if request was blocked on
        # not.
        wait_for = 4
        view = TemplateView.as_view(template_name='home.html')

        with self.settings(DEBUG=True):
            statsfile = settings.WEBPACK_LOADER[DEFAULT_CONFIG]['STATS_FILE']
            with open(statsfile, 'w') as fd:
                fd.write(json.dumps({'status': 'compile'}))
            then = time.time()
            request = self.factory.get('/')
            result = view(request)
            t = Thread(
                target=self.compile_bundles,
                args=('webpack.config.simple.js', wait_for))
            t2 = Thread(
                target=self.compile_bundles,
                args=('webpack.config.app2.js', wait_for))
            t3 = Thread(
                target=self.compile_bundles,
                args=('webpack.config.getFiles.js', wait_for))
            t.start()
            t2.start()
            t3.start()
            result.rendered_content
            elapsed = time.time() - then
            t.join()
            t2.join()
            t3.join()
            self.assertTrue(elapsed >= wait_for)

        with self.settings(DEBUG=False):
            self.compile_bundles('webpack.config.simple.js')
            self.compile_bundles('webpack.config.app2.js')
            self.compile_bundles('webpack.config.getFiles.js')
            then = time.time()
            request = self.factory.get('/')
            result = view(request)
            result.rendered_content
            elapsed = time.time() - then
            self.assertTrue(elapsed < wait_for)

    @patch(target='webpack_loader.templatetags.webpack_loader.warn')
    def test_emits_warning_on_no_request_in_djangoengine(self, warn_mock):
        """
        Should emit warnings on having no request in context (django
        template).
        """
        self.compile_bundles('webpack.config.skipCommon.js')
        asset_vendor = (
            '<script src="/static/django_webpack_loader_bundles/vendors.js" >'
            '</script>')
        asset_app1 = (
            '<script src="/static/django_webpack_loader_bundles/app1.js" >'
            '</script>')
        asset_app2 = (
            '<script src="/static/django_webpack_loader_bundles/app2.js" >'
            '</script>')

        # Shouldn't call any `warn()` here
        dups_template = Template(template_string=(
            r'{% load render_bundle from webpack_loader %}'
            r'{% render_bundle "app1" %}'
            r'{% render_bundle "app2" %}'))  # type: Template
        output = dups_template.render(context=Context())
        warn_mock.assert_not_called()
        self.assertEqual(output.count(asset_app1), 1)
        self.assertEqual(output.count(asset_app2), 1)
        self.assertEqual(output.count(asset_vendor), 2)

        # Should call `warn()` here
        nodups_template = Template(template_string=(
            r'{% load render_bundle from webpack_loader %}'
            r'{% render_bundle "app1" %}'
            r'{% render_bundle "app2" skip_common_chunks=True %}')
        )  # type: Template
        output = nodups_template.render(context=Context())
        self.assertEqual(output.count(asset_app1), 1)
        self.assertEqual(output.count(asset_app2), 1)
        self.assertEqual(output.count(asset_vendor), 2)
        warn_mock.assert_called_once_with(
            message=_WARNING_MESSAGE, category=RuntimeWarning)

        # Should NOT call `warn()` here
        warn_mock.reset_mock()
        nodups_template = Template(template_string=(
            r'{% load render_bundle from webpack_loader %}'
            r'{% render_bundle "app1" %}'
            r'{% render_bundle "app2" skip_common_chunks=True %}')
        )  # type: Template
        request = self.factory.get(path='/')
        output = nodups_template.render(context=Context({'request': request}))
        used_urls = getattr(request, '_webpack_loader_used_urls', None)
        self.assertIsNotNone(used_urls, msg=(
            '_webpack_loader_used_urls should be a property of request!'))
        self.assertEqual(output.count(asset_app1), 1)
        self.assertEqual(output.count(asset_app2), 1)
        self.assertEqual(output.count(asset_vendor), 1)
        warn_mock.assert_not_called()
        warn_mock.reset_mock()

    @patch(target='webpack_loader.templatetags.webpack_loader.warn')
    def test_emits_warning_on_no_request_in_jinja2engine(self, warn_mock):
        'Should emit warnings on having no request in context (Jinja2).'
        self.compile_bundles('webpack.config.skipCommon.js')
        settings = {
            'TEMPLATES': [
                {
                    'NAME': 'jinja2',
                    'BACKEND': 'django_jinja.backend.Jinja2',
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'match_extension': '.jinja',
                        'extensions': DEFAULT_EXTENSIONS + [_OUR_EXTENSION],
                    }
                },
            ]
        }
        asset_vendor = (
            '<script src="/static/django_webpack_loader_bundles/vendors.js" >'
            '</script>')
        asset_app1 = (
            '<script src="/static/django_webpack_loader_bundles/app1.js" >'
            '</script>')
        asset_app2 = (
            '<script src="/static/django_webpack_loader_bundles/app2.js" >'
            '</script>')
        warning_call = MockCall(
            message=_WARNING_MESSAGE, category=RuntimeWarning)

        # Shouldn't call any `warn()` here
        with self.settings(**settings):
            jinja2_engine = engines['jinja2']  # type: Jinja2
            dups_template = jinja2_engine.get_template(
                template_name='home-duplicated.jinja')  # type: Jinja2Template
            output = dups_template.render()
        warn_mock.assert_not_called()
        self.assertEqual(output.count(asset_app1), 2)
        self.assertEqual(output.count(asset_app2), 2)
        self.assertEqual(output.count(asset_vendor), 4)

        # Should call `warn()` here
        with self.settings(**settings):
            jinja2_engine = engines['jinja2']  # type: Jinja2
            nodups_template = jinja2_engine.get_template(
                template_name='home-deduplicated.jinja'
            )  # type: Jinja2Template
            output = nodups_template.render()
        self.assertEqual(output.count(asset_app1), 2)
        self.assertEqual(output.count(asset_app2), 2)
        self.assertEqual(output.count(asset_vendor), 4)
        self.assertEqual(warn_mock.call_count, 3)
        self.assertListEqual(
            warn_mock.call_args_list,
            [warning_call, warning_call, warning_call])

        # Should NOT call `warn()` here
        warn_mock.reset_mock()
        request = self.factory.get(path='/')
        with self.settings(**settings):
            jinja2_engine = engines['jinja2']  # type: Jinja2
            nodups_template = jinja2_engine.get_template(
                template_name='home-deduplicated.jinja'
            )  # type: Jinja2Template
            output = nodups_template.render(request=request)
        used_urls = getattr(request, '_webpack_loader_used_urls', None)
        self.assertIsNotNone(used_urls, msg=(
            '_webpack_loader_used_urls should be a property of request!'))
        self.assertEqual(output.count(asset_app1), 1)
        self.assertEqual(output.count(asset_app2), 1)
        self.assertEqual(output.count(asset_vendor), 1)
        warn_mock.assert_not_called()
        warn_mock.reset_mock()

    @patch(target='webpack_loader.templatetags.webpack_loader.warn')
    def test_get_files_emits_warning_on_no_request_in_djangoengine(self, warn_mock):
        self.compile_bundles('webpack.config.skipCommon.js')
        asset_vendor = '/static/django_webpack_loader_bundles/vendors.js'
        asset_app1 = '/static/django_webpack_loader_bundles/app1.js'
        asset_app2 = '/static/django_webpack_loader_bundles/app2.js'

        template = Template(template_string=(
            '{% load render_bundle get_files from webpack_loader %}'
            '{% render_bundle "app1" %}'
            '{% get_files "app2" skip_common_chunks=True as app2_files %}'
            '{% for f in app2_files %}'
            '    <link rel="prefetch" href="{{ f.url }}" />'
            '{% endfor %}'),
        )  # type: Template
        output = template.render(context=Context())
        self.assertEqual(output.count(asset_app1), 1)
        self.assertEqual(output.count(asset_app2), 1)
        self.assertEqual(output.count(asset_vendor), 2)
        warn_mock.assert_called_once_with(
            message=_WARNING_MESSAGE, category=RuntimeWarning)

    @patch(target='webpack_loader.templatetags.webpack_loader.warn')
    def test_get_files_emits_warning_on_no_request_in_jinja2engine(self, warn_mock):
        self.compile_bundles('webpack.config.skipCommon.js')
        asset_vendor = '/static/django_webpack_loader_bundles/vendors.js'
        asset_app1 = '/static/django_webpack_loader_bundles/app1.js'
        asset_app2 = '/static/django_webpack_loader_bundles/app2.js'
        settings = {
            'TEMPLATES': [
                {
                    'NAME': 'jinja2',
                    'BACKEND': 'django_jinja.backend.Jinja2',
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'match_extension': '.jinja',
                        'extensions': DEFAULT_EXTENSIONS + [_OUR_EXTENSION],
                    }
                },
            ]
        }

        with self.settings(**settings):
            jinja2_engine = engines['jinja2']  # type: Jinja2
            template = jinja2_engine.from_string(
                "{{ render_bundle('app1', 'js') }}"
                "{% set app2_files = webpack_get_files('app2', skip_common_chunks=True) %}"
                "{% for f in app2_files %}"
                "    <link rel='prefetch' href='{{ f.url }}' />"
                "{% endfor %}"
            )
            output = template.render(context=Context())
        self.assertEqual(output.count(asset_app1), 1)
        self.assertEqual(output.count(asset_app2), 1)
        self.assertEqual(output.count(asset_vendor), 2)
        warn_mock.assert_called_once_with(
            message=_WARNING_MESSAGE, category=RuntimeWarning)

    def _assert_common_chunks_duplicated_djangoengine(self, template):
        """
        Verify that any common chunks between two bundles are duplicated in
        the HTML markup.

        :param template: A Django template instance
        """
        request = self.factory.get(path='/')
        asset_vendor = (
            '<script src="/static/django_webpack_loader_bundles/vendors.js" >'
            '</script>')
        asset_app1 = (
            '<script src="/static/django_webpack_loader_bundles/app1.js" >'
            '</script>')
        asset_app2 = (
            '<script src="/static/django_webpack_loader_bundles/app2.js" >'
            '</script>')
        rendered_template = template.render(
            context=None, request=request)
        used_urls = getattr(request, '_webpack_loader_used_urls', None)

        self.assertIsNotNone(used_urls, msg=(
            '_webpack_loader_used_urls should be a property of request!'))
        self.assertEqual(rendered_template.count(asset_app1), 1)
        self.assertEqual(rendered_template.count(asset_app2), 1)
        self.assertEqual(rendered_template.count(asset_vendor), 2)

    def _assert_common_chunks_not_duplicated_djangoengine(self, template):
        """
        Verify that any common chunks between two bundles are not duplicated in
        the HTML markup.

        :param template: A Django template instance
        """
        request = self.factory.get(path='/')
        asset_vendor = (
            '<script src="/static/django_webpack_loader_bundles/vendors.js" >'
            '</script>')
        asset_app1 = (
            '<script src="/static/django_webpack_loader_bundles/app1.js" >'
            '</script>')
        asset_app2 = (
            '<script src="/static/django_webpack_loader_bundles/app2.js" >'
            '</script>')
        rendered_template = template.render(
            context=None, request=request)
        used_urls = getattr(request, '_webpack_loader_used_urls', None)

        self.assertIsNotNone(used_urls, msg=(
            '_webpack_loader_used_urls should be a property of request!'))
        self.assertEqual(rendered_template.count(asset_app1), 1)
        self.assertEqual(rendered_template.count(asset_app2), 1)
        self.assertEqual(rendered_template.count(asset_vendor), 1)

    def _assert_common_chunks_duplicated_jinja2engine(self, view):
        """
        Verify that any common chunks between two bundles are duplicated in
        the HTML markup.

        :param view: A Django TemplateView instance
        """
        settings = {
            'TEMPLATES': [
                {
                    'BACKEND': 'django_jinja.backend.Jinja2',
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'match_extension': '.jinja',
                        'extensions': DEFAULT_EXTENSIONS + [_OUR_EXTENSION],
                    }
                },
            ]
        }
        asset_vendor = (
            '<script src="/static/django_webpack_loader_bundles/vendors.js" >'
            '</script>')
        asset_app1 = (
            '<script src="/static/django_webpack_loader_bundles/app1.js" >'
            '</script>')
        asset_app2 = (
            '<script src="/static/django_webpack_loader_bundles/app2.js" >'
            '</script>')

        with self.settings(**settings):
            request = self.factory.get('/')
            result = view(request)  # type: TemplateResponse
            content = result.rendered_content
        self.assertIn(asset_vendor, content)
        self.assertIn(asset_app1, content)
        self.assertIn(asset_app2, content)
        self.assertEqual(content.count(asset_vendor), 4)
        self.assertEqual(content.count(asset_app1), 2)
        self.assertEqual(content.count(asset_app2), 2)
        used_urls = getattr(request, '_webpack_loader_used_urls', None)
        self.assertIsNotNone(used_urls, msg=(
            '_webpack_loader_used_urls should be a property of request!'))

    def _assert_common_chunks_not_duplicated_jinja2engine(self, view):
        """
        Verify that any common chunks between two bundles are not duplicated in
        the HTML markup.

        :param view: A Django TemplateView instance
        """
        settings = {
            'TEMPLATES': [
                {
                    'BACKEND': 'django_jinja.backend.Jinja2',
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'match_extension': '.jinja',
                        'extensions': DEFAULT_EXTENSIONS + [_OUR_EXTENSION],
                    }
                },
            ]
        }
        asset_vendor = (
            '<script src="/static/django_webpack_loader_bundles/vendors.js" >'
            '</script>')
        asset_app1 = (
            '<script src="/static/django_webpack_loader_bundles/app1.js" >'
            '</script>')
        asset_app2 = (
            '<script src="/static/django_webpack_loader_bundles/app2.js" >'
            '</script>')

        with self.settings(**settings):
            request = self.factory.get('/')
            result = view(request)  # type: TemplateResponse
            content = result.rendered_content
        self.assertIn(asset_vendor, content)
        self.assertIn(asset_app1, content)
        self.assertIn(asset_app2, content)
        self.assertEqual(content.count(asset_vendor), 1)
        self.assertEqual(content.count(asset_app1), 1)
        self.assertEqual(content.count(asset_app2), 1)
        used_urls = getattr(request, '_webpack_loader_used_urls', None)
        self.assertIsNotNone(used_urls, msg=(
            '_webpack_loader_used_urls should be a property of request!'))

    def test_skip_common_chunks_templatetag_djangoengine(self):
        """Test case for deduplication of modules with the django engine via the render_bundle template tag."""
        self.compile_bundles('webpack.config.skipCommon.js')

        django_engine = engines['django']
        dups_template = django_engine.from_string(template_code=(
            r'{% load render_bundle from webpack_loader %}'
            r'{% render_bundle "app1" %}'
            r'{% render_bundle "app2" %}'))  # type: Template
        self._assert_common_chunks_duplicated_djangoengine(dups_template)

        nodups_template = django_engine.from_string(template_code=(
            r'{% load render_bundle from webpack_loader %}'
            r'{% render_bundle "app1" %}'
            r'{% render_bundle "app2" skip_common_chunks=True %}')
        )  # type: Template
        self._assert_common_chunks_not_duplicated_djangoengine(nodups_template)


    def test_skip_common_chunks_templatetag_jinja2engine(self):
        """Test case for deduplication of modules with the Jinja2 engine via the render_bundle template tag."""
        self.compile_bundles('webpack.config.skipCommon.js')

        view = TemplateView.as_view(template_name='home-deduplicated.jinja')
        self._assert_common_chunks_not_duplicated_jinja2engine(view)

    def test_skip_common_chunks_setting_djangoengine(self):
        """The global setting should default to False and deduplicate chunks without changing the render_bundle template tag."""
        self.compile_bundles('webpack.config.skipCommon.js')

        django_engine = engines['django']
        dups_template = django_engine.from_string(template_code=(
            r'{% load render_bundle from webpack_loader %}'
            r'{% render_bundle "app1" %}'
            r'{% render_bundle "app2" %}'))  # type: Template
        self._assert_common_chunks_duplicated_djangoengine(dups_template)

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {"SKIP_COMMON_CHUNKS": True}):
            self._assert_common_chunks_not_duplicated_djangoengine(dups_template)

    def test_skip_common_chunks_setting_jinja2engine(self):
        """The global setting should default to False and deduplicate chunks without changing the render_bundle template tag."""
        self.compile_bundles('webpack.config.skipCommon.js')

        view = TemplateView.as_view(template_name='home-duplicated.jinja')
        self._assert_common_chunks_duplicated_jinja2engine(view)

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {"SKIP_COMMON_CHUNKS": True}):
            self._assert_common_chunks_not_duplicated_jinja2engine(view)

    def test_skip_common_chunks_setting_can_be_overridden_djangoengine(self):
        """The skip common chunks template tag parameters should take precedent over the global setting."""
        self.compile_bundles('webpack.config.skipCommon.js')

        django_engine = engines['django']
        nodups_template = django_engine.from_string(template_code=(
            r'{% load render_bundle from webpack_loader %}'
            r'{% render_bundle "app1" %}'
            r'{% render_bundle "app2" skip_common_chunks=True %}')
        )  # type: Template
        self._assert_common_chunks_not_duplicated_djangoengine(nodups_template)

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {"SKIP_COMMON_CHUNKS": True}):
            dups_template = django_engine.from_string(template_code=(
                r'{% load render_bundle from webpack_loader %}'
                r'{% render_bundle "app1" %}'
                r'{% render_bundle "app2" skip_common_chunks=False %}'))  # type: Template
            self._assert_common_chunks_duplicated_djangoengine(dups_template)

    def test_skip_common_chunks_setting_can_be_overridden_jinja2engine(self):
        """The skip common chunks template tag parameters should take precedent over the global setting."""
        self.compile_bundles('webpack.config.skipCommon.js')

        view = TemplateView.as_view(template_name='home-deduplicated.jinja')
        self._assert_common_chunks_not_duplicated_jinja2engine(view)

        loader = get_loader(DEFAULT_CONFIG)
        with patch.dict(loader.config, {"SKIP_COMMON_CHUNKS": True}):
            view = TemplateView.as_view(template_name='home-duplicated-forced.jinja')
            self._assert_common_chunks_duplicated_jinja2engine(view)

    def test_skip_common_chunks_missing_config(self):
        """If the setting is not present we should default to allowing common chunks."""
        self.compile_bundles('webpack.config.skipCommon.js')

        loader = get_loader(DEFAULT_CONFIG)
        # remove SKIP_COMMON_CHUNKS from config completely to test backward compatibility
        skip_common_chunks = loader.config.pop('SKIP_COMMON_CHUNKS')

        django_engine = engines['django']
        dups_template = django_engine.from_string(template_code=(
            r'{% load render_bundle from webpack_loader %}'
            r'{% render_bundle "app1" %}'
            r'{% render_bundle "app2" %}'))  # type: Template
        self._assert_common_chunks_duplicated_djangoengine(dups_template)

        # return removed key
        loader.config['SKIP_COMMON_CHUNKS'] = skip_common_chunks

    def test_get_as_tags_direct_usage(self):
        self.compile_bundles('webpack.config.skipCommon.js')
        
        asset_vendor = (
            '<script src="/static/django_webpack_loader_bundles/vendors.js" >'
            '</script>')
        asset_app1 = (
            '<link href="/static/django_webpack_loader_bundles/app1.css" rel="stylesheet" />')
        asset_app2 = (
            '<script src="/static/django_webpack_loader_bundles/app1.js" >'
            '</script>')
        
        tags = get_as_tags('app1')
        
        self.assertEqual(len(tags), 3)
        self.assertEqual(tags[0], asset_vendor)
        self.assertEqual(tags[1], asset_app1)
        self.assertEqual(tags[2], asset_app2)
