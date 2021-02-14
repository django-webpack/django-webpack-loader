import os

from django import template

from ..config import load_config
from ..contrib.pageassetfinder import PageAssetFinder

register = template.Library()


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
