from django.shortcuts import render
from django.template import RequestContext

import kn.agenda.entities as Es_a


def agenda(request):
    return render(request, 'agenda/agenda.html',
                  {'agenda': Es_a.events(agenda='kn')})


def agenda_zeus(request):
    return render(request, 'agenda/zeus.html',
                  {'agenda': Es_a.events(agenda='zeus')})


def ledenmail_template(request):
    return render(request, 'agenda/ledenmail-template.html',
                  {'agenda': list(Es_a.events(agenda='kn'))})

# vim: et:sta:bs=2:sw=4:
