import jinja2.ext

from ..templatetags.webpack_loader import *


class WebpackExtension(jinja2.ext.Extension):
    def __init__(self, environment):
        super(WebpackExtension, self).__init__(environment)
        environment.globals["render_bundle"] = lambda *a, **k: jinja2.Markup(render_bundle(*a, **k))
        environment.globals["render_entrypoint"] = lambda *a, **k: jinja2.Markup(render_entrypoint(*a, **k))

    def parse(self, parser):
        super(WebpackExtension, self).parse(parser)
