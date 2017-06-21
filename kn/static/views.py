import os

from django.conf import settings
from django.shortcuts import redirect, render
from django.template import RequestContext

_slideshow_images = None


def home(request):
    global _slideshow_images
    if _slideshow_images is None:
        _slideshow_images = []
        path = os.path.join(settings.MEDIA_ROOT, 'static/slideshow')
        for fn in sorted(os.listdir(path)):
            _slideshow_images.append(os.path.join(settings.MEDIA_URL,
                                                  'static/slideshow', fn))
    return render(request, 'static/home.html',
                  {'slideshow_images': _slideshow_images})

# legacy URL redirect view


def hink_stap(request, name):
    return redirect(settings.EXTERNAL_URLS[name], permanent=True)


# vim: et:sta:bs=2:sw=4:
