from django.http import HttpResponseRedirect, HttpResponse, Http404

def redirect_to_referer(request):
        referer = request.META.get('HTTP_REFERER', None)
        if referer is None:
                return HttpResponse("No referer set")
        return HttpResponseRedirect(referer)
