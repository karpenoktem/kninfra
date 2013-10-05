from django import template

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
        ret += "van %s" % _from.date()
    if until:
        if ret:
            ret += ' '
        ret += 'tot %s' % until.date()
    return '(%s)' % ret

# http://ianrolfe.livejournal.com/37243.html
@register.filter(name='lookup')
def lookup_filter(dict, index):
    if index in dict:
        return dict[index]
    return ''

# vim: et:sta:bs=2:sw=4:
