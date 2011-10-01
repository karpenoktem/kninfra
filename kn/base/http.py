import json
from django.http import HttpResponseRedirect, HttpResponse, Http404

def redirect_to_referer(request):
        referer = request.META.get('HTTP_REFERER', None)
        if referer is None:
                return HttpResponse("No referer set")
        return HttpResponseRedirect(referer)

class JsonHttpResponse(HttpResponse):
        def __init__(self, obj, *args, **kwargs):
                if 'mimetype' not in kwargs:
                        kwargs['mimetype'] = 'application/json; charset=utf8'
                super(JsonHttpResponse, self).__init__(
                        json.dumps(obj), *args, **kwargs)
