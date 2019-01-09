from django.template import Context
from webpack_loader.context_processors import sekizai


class WebpackLoaderContext(Context):
    """
    An alternative context to be used instead of RequestContext in places where
    no request is available.
    """
    def __init__(self, *args, **kwargs):
        super(WebpackLoaderContext, self).__init__(*args, **kwargs)
        self.update(webpack())

