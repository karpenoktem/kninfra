from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

import os.path

_slideshow_images = None

def home(request):
    global _slideshow_images
    if _slideshow_images is None:
        _slideshow_images = []
        path = os.path.join(settings.MEDIA_ROOT, 'static/slideshow')
        for fn in os.listdir(path):
            _slideshow_images.append(os.path.join(settings.MEDIA_URL,
                                        'static/slideshow', fn))
    return render_to_response('static/home.html',
            {'slideshow_images': _slideshow_images},
            context_instance=RequestContext(request))


# vim: et:sta:bs=2:sw=4:
