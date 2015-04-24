from django.shortcuts import render_to_response
from django.template import RequestContext
import kn.agenda.entities as Es_a

def agenda(request):
    return render_to_response('agenda/agenda.html',
            {'agenda': Es_a.events(agenda='kn')},
            context_instance=RequestContext(request))

def agenda_zeus(request):
    return render_to_response('agenda/zeus.html',
            {'agenda': Es_a.events(agenda='zeus')},
            context_instance=RequestContext(request))

def ledenmail_template(request):
    return render_to_response('agenda/ledenmail-template.html',
            {'agenda': list(Es_a.events(agenda='kn'))},
            context_instance=RequestContext(request))

# vim: et:sta:bs=2:sw=4:
