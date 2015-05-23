import datetime
from django import template
from django.contrib.staticfiles.storage import staticfiles_storage

from ..utils import get_bundle


register = template.Library()


@register.simple_tag
def render_bundle(bundle_name):
    bundle = get_bundle(bundle_name)
    tags = []
    for chunk in bundle:
        path = chunk.get('path', None)
        url = staticfiles_storage.url(path)
        name = str(chunk.get('name'))
        if url:
            if name.endswith('.js'):
                tags.append('<script type="text/javascript" src="{}"></script>'.format(url))
            elif name.endswith('.css'):
                tags.append('<link type="text/css" href="{}" rel="stylesheet">'.format(url))
    return '\n'.join(tags)
