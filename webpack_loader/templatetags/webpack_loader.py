import functools

from django import template, VERSION
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

from .. import utils
from ..config import load_config
from ..utils import get_unique_entrypoint_files

register = template.Library()


@register.simple_tag
def render_bundle(bundle_name, extension=None, config="DEFAULT", attrs=""):
    tags = utils.get_as_tags(bundle_name, extension=extension, config=config, attrs=attrs)
    return mark_safe("\n".join(tags))


@register.simple_tag
def render_entrypoint(entrypoint_name, extension=None, config="DEFAULT", attrs=""):
    tags = utils.get_entrypoint_files_as_tags(entrypoint_name, extension=extension, config=config, attrs=attrs)
    return mark_safe("\n".join(tags))


@register.simple_tag
def webpack_static(asset_name, config="DEFAULT"):
    return utils.get_static(asset_name, config=config)


assignment_tag = getattr(register, "simple_tag" if VERSION >= (1, 9) else "assignment_tag")


@assignment_tag
def get_files(bundle_name, extension=None, config="DEFAULT"):
    """
    Returns all chunks in the given bundle.
    Example usage::

        {% get_files "editor" "css" as editor_css_chunks %}
        CKEDITOR.config.contentsCss = "{{ editor_css_chunks.0.publicPath }}";

    :param bundle_name: The name of the bundle
    :param extension: (optional) filter by extension
    :param config: (optional) the name of the configuration
    :return: a list of matching chunks
    """
    return utils.get_files(bundle_name, extension=extension, config=config)


@register.simple_tag(takes_context=True)
def register_entrypoint(context, entrypoint):
    if not hasattr(context, "webpack_entrypoints"):
        context.webpack_entrypoints = []
    context.webpack_entrypoints.insert(0, entrypoint)


@register.simple_tag(takes_context=True)
def render_css(context, config="DEFAULT"):
    """Render <style> and/or <link> tags, depending on the use of CRITICAL_CSS. Should be put in the <head>"""
    entrypoints = getattr(context, "webpack_entrypoints", [])
    preloadTags = []
    noscriptTags = []
    for file in get_unique_entrypoint_files(entrypoints, "css", config):
        preloadTags.append(f'<link rel="preload" href="{file["url"]}" as="style" '
                           f'onload="this.onload=null;this.rel=\'stylesheet\'">')
        noscriptTags.append(f'<link rel="stylesheet" href="{file["url"]}">')
    criticalPath = finders.find(f"bundles/{entrypoints[-1]}.critical.css")
    cfg = load_config(config)
    if context["request"].first_visit and cfg["CRITICAL_CSS_ENABLED"] and criticalPath:
        with open(criticalPath) as f:
            criticalCss = f.read()
        return mark_safe(
            f"<style>{criticalCss}</style>\n"
            f"{''.join(preloadTags)}\n"
            f"<script>{inline_static_file('bundles/cssrelpreload.js')}</script>\n"
            f"<noscript>{''.join(noscriptTags)}</noscript>"
        )
    else:
        return mark_safe("".join(noscriptTags))


@register.simple_tag(takes_context=True)
def render_js(context, config="DEFAULT"):
    files = get_unique_entrypoint_files(getattr(context, "webpack_entrypoints", []), "js", config)
    return mark_safe("".join(f"<script src='{file['url']}'></script>" for file in files))


@functools.lru_cache
def inline_static_file(path):
    with open(finders.find(path)) as f:
        return mark_safe(f.read())


@functools.lru_cache
def inline_entrypoint(entrypoint, extension, config="DEFAULT"):
    inlined = ""
    for file in get_unique_entrypoint_files((entrypoint,), extension, config=config):
        with open(finders.find(f"bundles/{file['name']}")) as f:
            inlined += f.read()
    return mark_safe(inlined)
