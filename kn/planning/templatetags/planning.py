from django import template

register = template.Library()


@register.filter(name='last_shift')
def last_shift_filter(worker, pool):
    return pool.last_shift(worker)


@register.filter(name='may_manage')
def may_manage_filter(pool, user):
    return pool.may_manage(user)

# vim: et:sta:bs=2:sw=4:
