import json

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _


def get_param(request, name, default=None):
    """ get_param(request, name) replaces request.REQUEST.get(name) """
    return request.POST.get(name, request.GET.get(name, default))


def redirect_to_referer(request):
    referer = request.META.get('HTTP_REFERER', None)
    if referer is None:
        return HttpResponse(_("referer header mist"))
    return HttpResponseRedirect(referer)


class JsonHttpResponse(HttpResponse):

    def __init__(self, obj, *args, **kwargs):
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'application/json; charset=utf-8'
        super(JsonHttpResponse, self).__init__(
            json.dumps(obj), *args, **kwargs)

# vim: et:sta:bs=2:sw=4:
