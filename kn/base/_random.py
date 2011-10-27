# vim: et:sta:bs=2:sw=4:
import random

ALPHA = 'qwertyuiopasdfghjklzxcvbnm'
NUM = '1234567890'
ALPHANUMUL = ALPHA + ALPHA.upper() + NUM

def pseudo_randstr(l=12, cs=ALPHANUMUL):
    ret = ''
    for i in xrange(l):
        ret += cs[random.randint(0, len(cs)-1)]
    return ret