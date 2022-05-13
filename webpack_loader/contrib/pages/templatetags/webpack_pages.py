import functools
import os

from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

from webpack_loader.config import load_config
from webpack_loader.contrib.pages.pageassetfinder import PageAssetFinder
from webpack_loader.contrib.pages.utils import is_first_visit
from webpack_loader.utils import get_loader, get_unique_entrypoint_files

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
    preload_tags = []
    noscript_tags = []
    for file in get_unique_entrypoint_files(entrypoints, "css", config):
        preload_tags.append(
            f'<link rel="preload" href="{file["url"]}" as="style" '
            f"onload=\"this.onload=null;this.rel='stylesheet'\">"
        )
        noscript_tags.append(f'<link rel="stylesheet" href="{file["url"]}">')
    cfg = load_config(config)
    loader = get_loader(config)
    base = cfg["STATICFILE_BUNDLES_BASE"].format(locale=loader.locale)
    critical_path = finders.find(f"{base}{entrypoints[-1]}.critical.css")
    if is_first_visit(context["request"]) and cfg["CRITICAL_CSS_ENABLED"] and critical_path:
        with open(critical_path, encoding="utf-8") as f:
            critical_css = f.read()
        return mark_safe(
            f"<style>{critical_css}</style>\n"
            f"{''.join(preload_tags)}\n"
            f"<script>{inline_static_file(base + 'cssrelpreload.js')}</script>\n"
            f"<noscript>{''.join(noscript_tags)}</noscript>"
        )
    return mark_safe("".join(noscript_tags))


@register.simple_tag(takes_context=True)
def render_js(context, config="DEFAULT"):
    files = get_unique_entrypoint_files(getattr(context, "webpack_entrypoints", []), "js", config)
    return mark_safe("".join(f"<script src='{file['url']}'></script>" for file in files))


@functools.lru_cache()
def inline_static_file(path):
    with open(finders.find(path), encoding="utf-8") as f:  # type: ignore
        return mark_safe(f.read())


@functools.lru_cache()
def inline_entrypoint(entrypoint, extension, config="DEFAULT"):
    inlined = ""
    cfg = load_config(config)
    loader = get_loader(config)
    base = cfg["STATICFILE_BUNDLES_BASE"].format(locale=loader.locale)
    for file in get_unique_entrypoint_files((entrypoint,), extension, config=config):
        with open(finders.find(base + file["name"]), encoding="utf-8") as f:  # type: ignore
            inlined += f.read()
    return mark_safe(inlined)


@register.simple_tag(takes_context=True)
def asset_url(context, path, absolute=False, config="DEFAULT"):
    if absolute:
        pagename, _, path = path.partition("/")
    elif hasattr(context, "assets_pagename"):
        pagename = context.assets_pagename
    else:
        template_ = context.environment.get_template(context.name)
        pages_location = os.path.normpath(template_.filename)[: -(len(os.path.normpath(context.name)) + 1)]
        cfg = load_config(config)
        if pages_location == cfg["ROOT_PAGE_DIR"]:
            app_name = "root"
        else:
            app_name = os.path.basename(os.path.dirname(pages_location))
        pagename = os.path.join(app_name, os.path.dirname(context.name)).replace(os.path.sep, ".")
        context.assets_pagename = pagename  # caching for next asset
    return PageAssetFinder.page_asset_url(pagename, path)
