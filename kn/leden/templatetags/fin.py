from django import template

register = template.Library()


@register.filter(name='id_handle')
def id_handle_filter(_id):
    return "id" + _id


@register.filter(name='tr_handle')
def tr_handle_filter(_num):
    return "tr" + _num


@register.filter(name='day_handle')
def day_handle_filter(date, account):
    return "day" + date + account


@register.filter(name="concat")
def concat_filter(a, b):
    return a + b

# vim: et:sta:bs=2:sw=4:
