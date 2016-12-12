from django import template, VERSION
from django.conf import settings
from django.utils.safestring import mark_safe

from ..utils import get_loader

register = template.Library()


def filter_by_extension(bundle, extension):
    '''Return only files with the given extension'''
    for chunk in bundle:
        if chunk['name'].endswith('.{0}'.format(extension)):
            yield chunk


def render_as_tags(bundle, attrs):
    tags = []
    for chunk in bundle:
        if chunk['name'].endswith(('.js', '.js.gz')):
            tags.append((
                '<script type="text/javascript" src="{0}" {1}></script>'
            ).format(chunk['url'], attrs))
        elif chunk['name'].endswith(('.css', '.css.gz')):
            tags.append((
                '<link type="text/css" href="{0}" rel="stylesheet" {1}/>'
            ).format(chunk['url'], attrs))
    return mark_safe('\n'.join(tags))


def _get_content(bundle_name, extension, config, loader_function):
    content = getattr(get_loader(config), loader_function)(bundle_name)
    if extension:
        content = filter_by_extension(content, extension)
    return content


@register.simple_tag
def render_bundle(bundle_name, extension=None, config='DEFAULT', attrs=''):
    return render_as_tags(_get_content(bundle_name, extension, config, 'get_bundle'), attrs)


@register.simple_tag
def webpack_static(asset_name, config='DEFAULT'):
    return "{0}{1}".format(
        get_loader(config).get_assets().get(
            'publicPath', getattr(settings, 'STATIC_URL')
        ),
        asset_name
    )

@register.simple_tag
def webpack_asset_path(bundle_name, config='DEFAULT'):
    return _get_content(bundle_name, None, config, 'get_exported_asset')['publicPath']

assignment_tag = register.simple_tag if VERSION >= (1, 9) else register.assignment_tag
@assignment_tag
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
    return list(_get_content(bundle_name, extension, config, 'get_bundle'))
