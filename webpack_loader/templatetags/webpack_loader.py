from django import template, VERSION
from django.conf import settings
from django.utils.safestring import mark_safe

from .. import utils

register = template.Library()


@register.simple_tag(takes_context=True)
def render_bundle(context, bundle_name, extension=None, config='DEFAULT', suffix='', attrs='', is_preload=False, skip_common_chunks=False):
    tags = utils.get_as_tags(
        bundle_name, extension=extension, config=config,
        suffix=suffix, attrs=attrs, is_preload=is_preload
    )
    used_tags = context.get("webpack_loader_used_tags", [])
    if not used_tags:
        context["webpack_loader_used_tags"] = []
    if skip_common_chunks:
        tags = [mark_safe(tag) for tag in tags if tag not in used_tags]

    context["webpack_loader_used_tags"] = context["webpack_loader_used_tags"] + tags
    
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
