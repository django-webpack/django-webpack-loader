from warnings import warn

from django.template import Library
from django.utils.safestring import mark_safe

from .. import utils

register = Library()
_WARNING_MESSAGE = (
    'You have specified skip_common_chunks=True but the passed context '
    'doesn\'t have a request. django_webpack_loader needs a request object to '
    'filter out duplicate chunks. Please see https://github.com/django-webpack'
    '/django-webpack-loader#skipping-the-generation-of-multiple-common-chunks')


@register.simple_tag(takes_context=True)
def render_bundle(
        context, bundle_name, extension=None, config='DEFAULT', suffix='',
        attrs='', is_preload=False, skip_common_chunks=None):
    if skip_common_chunks is None:
        skip_common_chunks = utils.get_skip_common_chunks(config)
    tags = utils.get_as_tags(
        bundle_name, extension=extension, config=config, suffix=suffix,
        attrs=attrs, is_preload=is_preload)
    request = context.get('request')
    if request is None:
        if skip_common_chunks:
            warn(message=_WARNING_MESSAGE, category=RuntimeWarning)
        return mark_safe('\n'.join(tags))
    used_tags = getattr(request, '_webpack_loader_used_tags', None)
    if not used_tags:
        used_tags = request._webpack_loader_used_tags = set()
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
        CKEDITOR.config.contentsCss = '{{ editor_css_chunks.0.url }}';

    :param bundle_name: The name of the bundle
    :param extension: (optional) filter by extension
    :param config: (optional) the name of the configuration
    :return: a list of matching chunks
    """
    return utils.get_files(bundle_name, extension=extension, config=config)
