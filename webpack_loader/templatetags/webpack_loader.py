from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe

from .. import utils

register = Library()
_PROC_DJTEMPLATE = 'django.template.context_processors.request'
_DJ_TEMPLATEPROCESSOR = 'django.template.backends.django.DjangoTemplates'
_STARTUP_ERROR = (
    f'Please make sure that "{_PROC_DJTEMPLATE}" is added '
    'to your ["OPTIONS"]["context_processors"] list in your '
    f'settings.TEMPLATES where the BACKEND is "{_DJ_TEMPLATEPROCESSOR}". '
    'django-webpack-loader needs it and cannot run without it.')


def _is_request_in_context():
    for item in settings.TEMPLATES:
        backend = item.get('BACKEND', {})
        if backend == _DJ_TEMPLATEPROCESSOR:
            processors = set(
                item.get('OPTIONS', {}).get('context_processors', []))
            if _PROC_DJTEMPLATE not in processors:
                raise RuntimeError(_STARTUP_ERROR)


# Check settings at module import time
_is_request_in_context()


@register.simple_tag(takes_context=True)
def render_bundle(
        context, bundle_name, extension=None, config='DEFAULT', suffix='',
        attrs='', is_preload=False, skip_common_chunks=False):
    tags = utils.get_as_tags(
        bundle_name, extension=extension, config=config, suffix=suffix,
        attrs=attrs, is_preload=is_preload)

    if not hasattr(context['request'], '_webpack_loader_used_tags'):
        context['request']._webpack_loader_used_tags = set()

    used_tags = context['request']._webpack_loader_used_tags
    if skip_common_chunks:
        tags = [tag for tag in tags if tag not in used_tags]
    used_tags.update(tags)

    return mark_safe('\n'.join(tags))


@register.simple_tag
def webpack_static(asset_name, config='DEFAULT'):
    return utils.get_static(asset_name, config=config)


@register.simple_tag
def get_files(bundle_name, extension=None, config='DEFAULT'):
    """
    Returns all chunks in the given bundle.
    Example usage::

        {% get_files 'editor' 'css' as editor_css_chunks %}
        CKEDITOR.config.contentsCss = '{{ editor_css_chunks.0.publicPath }}';

    :param bundle_name: The name of the bundle
    :param extension: (optional) filter by extension
    :param config: (optional) the name of the configuration
    :return: a list of matching chunks
    """
    return utils.get_files(bundle_name, extension=extension, config=config)
