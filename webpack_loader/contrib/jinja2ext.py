import jinja2

from ..templatetags.webpack_loader import render_bundle


class WebpackExtension(jinja2.ext.Extension):
    def __init__(self, environment):
        super(WebpackExtension, self).__init__(environment)
        environment.globals["render_bundle"] = lambda name: jinja2.Markup(render_bundle(name))
