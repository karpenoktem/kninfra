import random

from django.utils.six.moves import range

ALPHA = 'qwertyuiopasdfghjklzxcvbnm'
NUM = '1234567890'
ALPHANUMUL = ALPHA + ALPHA.upper() + NUM


def pseudo_randstr(length=12, cs=ALPHANUMUL):
    ret = ''
    for i in range(length):
        ret += cs[random.randint(0, len(cs) - 1)]
    return ret

# vim: et:sta:bs=2:sw=4:
