from django import VERSION, template
from django.conf import settings
from django.utils.safestring import mark_safe

from .. import utils

register = template.Library()


# https://stackoverflow.com/a/46756430
def template_from_string(template_string, using=None):
    """
    Convert a string into a template object,
    using a given template engine or using the default backends
    from settings.TEMPLATES if no engine was specified.
    """
    # This function is based on django.template.loader.get_template,
    # but uses Engine.from_string instead of Engine.get_template.
    chain = []
    engine_list = template.engines.all() if using is None else [template.engines[using]]
    for engine in engine_list:
        try:
            return engine.from_string(template_string)
        except TemplateSyntaxError as e:
            chain.append(e)
    raise TemplateSyntaxError(template_string, chain=chain)


@register.simple_tag(takes_context=True)
def render_bundle(context, bundle_name, extension=None, config='DEFAULT', attrs=''):
    ctx = {}
    if context is not None:
        ctx = context.flatten()
    rendered_attrs = template_from_string(attrs).render(ctx)
    tags = utils.get_as_tags(bundle_name, extension=extension, config=config, attrs=rendered_attrs)
    return mark_safe('\n'.join(tags))


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
