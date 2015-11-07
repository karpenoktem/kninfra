from django import template

register = template.Library()

@register.filter(name='last_shift')
def last_shift_filter(worker, pool):
    return pool.last_shift(worker)

# vim: et:sta:bs=2:sw=4:
