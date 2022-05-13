from jinja2.ext import Extension
from jinja2.runtime import Context
from jinja2.utils import pass_context

from ..templatetags.webpack_loader import *


@pass_context
def _render_bundle(context: Context, *args, **kwargs):
    return render_bundle(context, *args, **kwargs)


class WebpackExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals.update(
            {
                "render_bundle": render_bundle,
                "render_entrypoint": render_entrypoint,
            }
        )
