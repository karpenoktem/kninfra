from kn import settings

from collections import namedtuple
foto_root = namedtuple('foto_root', ('base', 'between'))

FOTO_ROOTS = {
              'home': foto_root(settings.USER_DIRS, 'fotos'),
              'wolk_fotos': foto_root(settings.WOLK_DATA_PATH, 'files/fotos'),
              'wolk_photos': foto_root(settings.WOLK_DATA_PATH, 'files/photos'),
              'wolk_Photos': foto_root(settings.WOLK_DATA_PATH, 'files/Photos'),
              }

# vim: et:sta:bs=2:sw=4:
