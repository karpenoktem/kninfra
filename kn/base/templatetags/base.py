import json
import os
import os.path
import random

from django import template
from django.conf import settings
from django.core.urlresolvers import Resolver404, resolve, reverse
from django.template.defaultfilters import stringfilter
from django.utils import translation
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

register = template.Library()


@stringfilter
@register.filter(name='email')
def email_filter(value):
    n, r = conditional_escape(value).split('@', 1)
    d, e = r.rsplit('.', 1)
    return mark_safe(("<script type='text/javascript'>email("
                      "'%s', '%s', '%s')</script><noscript>X@Y.Z %s Z=%s,"
                      " Y=%s, X=%s</noscript>") % (
        e, d, n, _('waar'), e, d, n))


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

# easily look up external URLs defined in settings.py


@register.simple_tag
def external_url(name):
    return settings.EXTERNAL_URLS[name]


@register.assignment_tag
def store_external_url(name):
    return settings.EXTERNAL_URLS[name]


@register.simple_tag(takes_context=True)
def translate_url(context, language):
    # Do not forget to add django.core.context_processors.request as
    # a template context processor.
    try:
        view = resolve(context['request'].path)
    except Resolver404:
        return
    request_language = translation.get_language()
    translation.activate(language)
    try:
        url = reverse(view.url_name, args=view.args, kwargs=view.kwargs)
    finally:
        translation.activate(request_language)
    return url

# vim: et:sta:bs=2:sw=4:
