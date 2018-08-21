
from django.conf import settings
from django.shortcuts import redirect, render


def home(request):
    return render(request, 'static/home.html',
                  {'slideshow_images': settings.HOME_SLIDESHOW})

# legacy URL redirect view


def hink_stap(request, name):
    return redirect(settings.EXTERNAL_URLS[name], permanent=True)


# vim: et:sta:bs=2:sw=4:
