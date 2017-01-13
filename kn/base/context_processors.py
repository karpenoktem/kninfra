from django.conf import settings


def base_url(request):
    return {'ABSOLUTE_MEDIA_URL': settings.ABSOLUTE_MEDIA_URL}

# vim: et:sta:bs=2:sw=4:
