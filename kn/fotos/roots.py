from kn import settings

from collections import namedtuple
foto_root = namedtuple('foto_root', ('base', 'between'))

FOTO_ROOTS = {'home': foto_root(settings.USER_DIRS, 'fotos'),
              'wolk': foto_root(settings.WOLK_DATA_PATH, 'files/Photos')}

# vim: et:sta:bs=2:sw=4:
