import random
from settings import BASE_BGS

def bg(request):
        return {'BASE_BACKGROUND': random.choice(BASE_BGS)}
