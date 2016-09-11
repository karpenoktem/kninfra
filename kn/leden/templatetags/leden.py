from django import template
from django.utils.translation import ugettext as _

register = template.Library()

@register.filter(name='rel_when')
def rel_when_filter(r):
    if not isinstance(r, dict):
        raise ValueError("Expecting dict")
    _from = r.get('from')
    until = r.get('until')
    if not _from and not until:
        return ''
    ret = ''
    if _from:
        ret += _("van %s") % _from.date()
    if until:
        if ret:
            ret += ' '
        ret += _('tot %s') % until.date()
    return '(%s)' % ret

# vim: et:sta:bs=2:sw=4:
