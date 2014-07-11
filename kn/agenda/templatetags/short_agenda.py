from django import template
import kn.agenda.entities as Es_a

register = template.Library()
MAX_ITEMS = 10;

@register.inclusion_tag('agenda/short_agenda.html')
def show_short_agenda():
    items = list(Es_a.all(limit=MAX_ITEMS + 1));
    return {'short_agenda': items[0:MAX_ITEMS],
            'has_more': len(items) > MAX_ITEMS}

# vim: et:sta:bs=2:sw=4:
