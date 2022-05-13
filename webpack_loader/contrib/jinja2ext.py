from jinja2.ext import Extension
from jinja2.utils import pass_context

from ..templatetags.webpack_loader import render_bundle, render_entrypoint


class WebpackExtension(Extension):  # pylint: disable=abstract-method
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals.update(
            {
                "render_bundle": pass_context(render_bundle),
                "render_entrypoint": pass_context(render_entrypoint),
            }
        )
