from django import template
import kn.agenda.entities as Es_a

register = template.Library()

@register.inclusion_tag('agenda/short_agenda.html')
def show_short_agenda():
        return {'short_agenda': Es_a.all()}
