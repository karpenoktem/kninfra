from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django import template

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

# vim: et:sta:bs=2:sw=4:
