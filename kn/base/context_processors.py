from django.conf import settings


def base_url(request):
    return {'ABSOLUTE_MEDIA_URL': settings.ABSOLUTE_MEDIA_URL}

def dev_banner(request):
    if settings.DEBUG or settings.CHUCK_NORRIS_HIS_SECRET == "CHANGE ME":
        return {'DEV_BANNER': "dev"}
    return {'DEV_BANNER': None}

# vim: et:sta:bs=2:sw=4:
