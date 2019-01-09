from collections import defaultdict

from .utils import get_varname


def webpack(request=None):
    """
    Simple context processor which makes sure that the Webpack Dictionary is
    available in all templates.
    """
    return {get_varname(): defaultdict(set)}

