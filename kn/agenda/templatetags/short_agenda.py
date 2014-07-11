from django import template
import kn.agenda.entities as Es_a

register = template.Library()
max_items = 10;

@register.inclusion_tag('agenda/short_agenda.html')
def show_short_agenda():
        Es_limited = list(Es_a.all(limit=max_items + 1));
        return {'short_agenda': Es_limited[0:max_items], 'has_more': len(Es_limited) > max_items}
