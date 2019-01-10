from django import template, VERSION
from django.conf import settings
from django.utils.safestring import mark_safe

from .. import utils

register = template.Library()



def validate_context(context):
    """
    Validates a given context.
    Returns True if the context is valid.
    Returns False if the context is invalid but the error should be silently
    ignored.
    Raises a TemplateSyntaxError if the context is invalid and we're in debug
    mode.
    """
    try:
        template_debug = context.template.engine.debug
    except AttributeError:
        try:
            # Get the default engine debug value
            template_debug = template.Engine.get_default().debug
        except AttributeError:
            # Django 1.9 and below fallback
            template_debug = settings.TEMPLATE_DEBUG

    if utils.get_varname() in context:
        return True
    if not template_debug:
        return False
    raise template.TemplateSyntaxError(
        "You must enable the 'webpack_loader.context_processors.webpack' template "
        "context processor or use 'webpack_loader.context.WebpackLoaderContext' to "
        "render your templates."
    )

def filtered_asset_links(context, tags, config):
    tags = set(tags)
    varname = utils.get_varname()
    newtags = tags - context[varname][config]
    context[varname][config] |= tags
    return mark_safe('\n'.join( newtags ))

@register.simple_tag(takes_context=True)
def render_bundle(context, bundle_name, extension=None, config='DEFAULT', attrs=''):
    if validate_context(context):
        tags = utils.get_as_tags(bundle_name, extension=extension, config=config, attrs=attrs)
        return filtered_asset_links(context, tags, config)

@register.simple_tag(takes_context=True)
def render_entrypoint(context, entrypoint_name, extension=None, config='DEFAULT', attrs=''):
    if validate_context(context):
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
