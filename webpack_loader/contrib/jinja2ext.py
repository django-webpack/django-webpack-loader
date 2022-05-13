from jinja2.ext import Extension
from jinja2.utils import pass_context

from ..contrib.pages.templatetags.webpack_pages import (
    asset_url,
    inline_entrypoint,
    register_entrypoint,
    render_css,
    render_js,
)
from ..templatetags.webpack_loader import render_bundle, render_entrypoint


class WebpackExtension(Extension):  # pylint: disable=abstract-method
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals.update(
            {
                "render_bundle": pass_context(render_bundle),
                "render_entrypoint": pass_context(render_entrypoint),
                "register_entrypoint": pass_context(register_entrypoint),
                "render_css": pass_context(render_css),
                "render_js": pass_context(render_js),
                "inline_entrypoint": inline_entrypoint,
                "asset": pass_context(asset_url),
            }
        )
