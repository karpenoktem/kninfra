import random
from settings import ABSOLUTE_MEDIA_URL

def base_url(request):
    return {'ABSOLUTE_MEDIA_URL': ABSOLUTE_MEDIA_URL}

# vim: et:sta:bs=2:sw=4:
