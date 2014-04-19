from django.shortcuts import render_to_response
from django.template import RequestContext
import kn.agenda.entities as Es_a

def agenda(request):
    return render_to_response('agenda/agenda.html',
            {'agenda': Es_a.all()},
            context_instance=RequestContext(request))

# vim: et:sta:bs=2:sw=4:
