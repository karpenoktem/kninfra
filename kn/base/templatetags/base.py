from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.conf import settings
from django import template

import os
import random
import os.path
import json

register = template.Library()

@stringfilter
@register.filter(name='email')
def email_filter(value):
    n, r = conditional_escape(value).split('@',1)
    d, e = r.rsplit('.',1)
    return mark_safe(("<script type='text/javascript'>email("+
        "'%s', '%s', '%s')</script><noscript>X@Y.Z waar Z=%s,"+
        " Y=%s, X=%s</noscript>") % (\
        e, d, n, e, d, n))

@stringfilter
@register.filter(name='mark_safe')
def mark_safe_filter(value):
    return mark_safe(value)

@stringfilter
@register.filter(name='json')
def json_filter(data):
    return mark_safe(json.dumps(data)
                         .replace('&', '\u0026')
                         .replace('<', '\u003c')
                         .replace('>', '\u003e')
                         .replace('/', '\u002f'))

# http://ianrolfe.livejournal.com/37243.html
@register.filter(name='lookup')
def lookup_filter(dict, index):
    return dict.get(index, '')

_header_images = None
@register.simple_tag
def header():
    global _header_images
    path = os.path.join(settings.MEDIA_ROOT, 'base/headers')
    if _header_images is None:
        _header_images = [fn for fn in os.listdir(path)]
    pick = random.choice(_header_images)
    return os.path.join(settings.MEDIA_URL, 'base/headers', pick)

# easily look up external URLs defined in settings.py
@register.simple_tag
def external_url(name):
    return settings.EXTERNAL_URLS[name]

# vim: et:sta:bs=2:sw=4:
