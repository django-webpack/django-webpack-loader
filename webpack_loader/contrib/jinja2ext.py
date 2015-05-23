from jinja2.ext import Extension

from ..templatetags.webpack_loader import render_bundle


class WebpackExtension(Extension):
    def __init__(self, environment):
        super(WebpackExtension, self).__init__(environment)
        environment.globals["render_bundle"] = render_bundle
