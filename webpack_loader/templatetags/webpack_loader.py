import datetime
from django import template

from ..utils import get_bundle


register = template.Library()


@register.simple_tag
def render_bundle(bundle_name):
    bundle = get_bundle(bundle_name)
    tags = []
    for chunk in bundle:
        if chunk['name'].endswith('.js'):
            url = chunk.get('publicPath') or chunk['url']
            tags.append('<script type="text/javascript" src="{}"></script>'.format(url))
        elif chunk['name'].endswith('.css'):
            tags.append('<link type="text/css" href="{}" rel="stylesheet">'.format(url))
    return '\n'.join(tags)
