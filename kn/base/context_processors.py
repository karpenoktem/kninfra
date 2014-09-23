import random
from settings import BASE_BGS, BASE_URL

def bg(request):
        return {'BASE_BACKGROUND': random.choice(BASE_BGS)}

def base_url(request):
    return {'BASE_URL': BASE_URL}

# vim: et:sta:bs=2:sw=4:
