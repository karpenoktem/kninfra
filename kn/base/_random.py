import os
import struct

from django.utils.six.moves import range

ALPHA = 'qwertyuiopasdfghjklzxcvbnm'
NUM = '1234567890'
ALPHANUMUL = ALPHA + ALPHA.upper() + NUM


def pseudo_randint():
    # generate 4 bytes and decode it as a 32-bit unsigned number
    return struct.unpack('I', os.urandom(4))[0]


def pseudo_randstr(length=12, chars=ALPHANUMUL):
    ret = ''
    for i in range(length):
        ret += chars[pseudo_randint() % len(chars)]
    return ret

# vim: et:sta:bs=2:sw=4:
