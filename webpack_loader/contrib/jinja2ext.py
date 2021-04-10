import jinja2.ext

from ..templatetags.webpack_loader import *


class WebpackExtension(jinja2.ext.Extension):
    def __init__(self, environment):
        super(WebpackExtension, self).__init__(environment)
        environment.globals.update({
            "render_bundle": render_bundle,
            "render_entrypoint": render_entrypoint,
        })

    def parse(self, parser):
        super(WebpackExtension, self).parse(parser)
