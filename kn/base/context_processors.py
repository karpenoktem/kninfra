import random
from settings import BASE_BGS, ABSOLUTE_MEDIA_URL

def bg(request):
        return {'BASE_BACKGROUND': random.choice(BASE_BGS)}

def base_url(request):
    return {'ABSOLUTE_MEDIA_URL': ABSOLUTE_MEDIA_URL}

# vim: et:sta:bs=2:sw=4:
