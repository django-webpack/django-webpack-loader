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
            tags.append('<script type="text/javascript" src="{}"/>'.format(chunk['publicPath']))
        elif chunk['name'].endwith('.css'):
            tags.append('<link type="text/css" href="{}" rel="stylesheet"/>'.format(chunk['publicPath']))
    return '\n'.join(tags)
