import jinja2.ext

from ..templatetags.webpack_loader import *
from ..contrib.pages.templatetags.webpack_pages import *


class WebpackExtension(jinja2.ext.Extension):
    def __init__(self, environment):
        super(WebpackExtension, self).__init__(environment)
        environment.globals.update({
            "render_bundle": render_bundle,
            "render_entrypoint": render_entrypoint,
            "register_entrypoint": jinja2.contextfunction(register_entrypoint),
            "render_css": jinja2.contextfunction(render_css),
            "render_js": jinja2.contextfunction(render_js),
            "inline_entrypoint": inline_entrypoint,
            "asset": jinja2.contextfunction(asset_url),
        })

    def parse(self, parser):
        super(WebpackExtension, self).parse(parser)
