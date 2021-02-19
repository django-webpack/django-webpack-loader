import functools
import os

from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

from ..pageassetfinder import PageAssetFinder
from ..utils import is_first_visit
from ....config import load_config
from ....utils import get_unique_entrypoint_files

register = template.Library()


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
    if is_first_visit(context["request"]) and cfg["CRITICAL_CSS_ENABLED"] and criticalPath:
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


@functools.lru_cache()
def inline_static_file(path):
    with open(finders.find(path)) as f:
        return mark_safe(f.read())


@functools.lru_cache()
def inline_entrypoint(entrypoint, extension, config="DEFAULT"):
    inlined = ""
    for file in get_unique_entrypoint_files((entrypoint,), extension, config=config):
        with open(finders.find(f"bundles/{file['name']}")) as f:
            inlined += f.read()
    return mark_safe(inlined)


@register.simple_tag(takes_context=True)
def asset_url(context, path, absolute=False, config="DEFAULT"):
    if absolute:
        pagename, slash, path = path.partition("/")
    elif hasattr(context, "assets_pagename"):
        pagename = context.assets_pagename
    else:
        template_ = context.environment.get_template(context.name)
        pages_location = os.path.normpath(template_.filename).rstrip(os.path.normpath(context.name))  # 'pages' folder
        cfg = load_config(config)
        if pages_location == cfg["ROOT_PAGE_DIR"]:
            app_name = "root"
        else:
            app_name = os.path.basename(os.path.dirname(pages_location))
        pagename = os.path.join(app_name, os.path.dirname(context.name)).replace(os.path.sep, ".")
        context.assets_pagename = pagename  # caching for next asset
    return PageAssetFinder.page_asset_url(pagename, path)
