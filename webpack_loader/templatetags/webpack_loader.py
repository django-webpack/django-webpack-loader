from django import template, VERSION
from django.conf import settings
from django.utils.safestring import mark_safe

from .. import utils

register = template.Library()




def filtered_asset_links(context, tags, config):
    tags = set(tags)
    varname = utils.get_varname()
    newtags = tags - context[varname][config]
    context[varname][config] |= tags
    return mark_safe('\n'.join( newtags ))

@register.simple_tag(takes_context=True)
def render_bundle(context, bundle_name, extension=None, config='DEFAULT', attrs=''):
    tags = utils.get_as_tags(bundle_name, extension=extension, config=config, attrs=attrs)
    return filtered_asset_links(context, tags, config)

@register.simple_tag(takes_context=True)
def render_entrypoint(context, entrypoint_name, extension=None, config='DEFAULT', attrs=''):
    tags = utils.get_entrypoint_files_as_tags(entrypoint_name, config=config, attrs=attrs)
    return filtered_asset_links(context, tags, config)

@register.simple_tag
def webpack_static(asset_name, config='DEFAULT'):
    return utils.get_static(asset_name, config=config)


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
    return utils.get_files(bundle_name, extension=extension, config=config)
