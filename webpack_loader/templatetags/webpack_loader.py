from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from ..utils import get_config, get_assets, get_bundle


register = template.Library()


def filter_by_extension(bundle, extension):
    for chunk in bundle:
        if chunk['name'].endswith('.{}'.format(extension)):
            yield chunk


def render_as_tags(bundle, config='DEFAULT'):
    config = get_config(config)
    tags = []
    for chunk in bundle:
        if chunk['name'].endswith('.js'):
            tags.append('<script type="text/javascript" src="{}"></script>'.format(config['get_chunk_url'](chunk, config)))
        elif chunk['name'].endswith('.css'):
            tags.append('<link type="text/css" href="{}" rel="stylesheet"/>'.format(config['get_chunk_url'](chunk, config)))
    return mark_safe('\n'.join(tags))


def _get_bundle(bundle_name, extension, config):
    bundle = get_bundle(bundle_name, get_config(config))
    if extension:
        bundle = filter_by_extension(bundle, extension)
    return bundle


@register.simple_tag
def render_bundle(bundle_name, extension=None, config='DEFAULT'):
    return render_as_tags(_get_bundle(bundle_name, extension, config), config)


@register.simple_tag
def webpack_static(asset_name, config='DEFAULT'):
    return "{}{}".format(
        get_assets(get_config(config)).get(
            'publicPath', getattr(settings, 'STATIC_URL')
        ),
        asset_name
    )


@register.assignment_tag
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
    return list(_get_bundle(bundle_name, extension, config))
