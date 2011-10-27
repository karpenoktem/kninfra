# vim: et:sta:bs=2:sw=4:
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from kn.reglementen.models import Reglement, Version
from regl.model import Document

def reglement_list(request):
    reglementen = Reglement.objects.order_by('humanName').all()
    return render_to_response('reglementen/reglement_list.html',
            {'reglementen': reglementen},
            context_instance=RequestContext(request))

def reglement_detail(request, name):
    try:
        reglement = Reglement.objects.select_related(
                'version_set').get(name=name)
    except Reglement.DoesNotExist:
        raise Http404
    return render_to_response('reglementen/reglement_detail.html',
            {'reglement': reglement,
             'versions': reglement.version_set.order_by(
                 'validFrom').all()},
            context_instance=RequestContext(request))

def version_detail(request, reglement_name, version_name):
    try:
        version = Version.objects.select_related(
                'reglement').get(name=version_name)
    except Version.DoesNotExist:
        raise Http404
    doc = Document.from_string(version.regl)
    return render_to_response('reglementen/version_detail.html',
            {'version': version,
             'content': doc.to_html()},
            context_instance=RequestContext(request))