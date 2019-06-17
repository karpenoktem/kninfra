import datetime

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


# https://stackoverflow.com/a/46349237/559350
@register.filter(name='unix_to_datetime')
def unix_to_datetime(value):
    return datetime.datetime.fromtimestamp(value)

# vim: et:sta:bs=2:sw=4:
