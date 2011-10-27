# vim: et:sta:bs=2:sw=4:
import random
from settings import BASE_BGS

def bg(request):
        return {'BASE_BACKGROUND': random.choice(BASE_BGS)}