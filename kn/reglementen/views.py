from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.template import RequestContext

import kn.reglementen.entities as Es_regl


@login_required
def reglement_list(request):
    return render(request, 'reglementen/reglement_list.html',
                  {'reglementen': Es_regl.all()})


@login_required
def reglement_detail(request, name):
    reglement = Es_regl.reglement_by_name(name)
    if not reglement:
        raise Http404
    return render(request, 'reglementen/reglement_detail.html',
                  {'reglement': reglement})


@login_required
def version_detail(request, reglement_name, version_name):
    version = Es_regl.version_by_names(reglement_name, version_name)
    return render(request, 'reglementen/version_detail.html',
                  {'version': version,
                   'content': version.to_html()})

# vim: et:sta:bs=2:sw=4:
