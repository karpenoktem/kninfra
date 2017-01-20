# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import logging

from kn.utils.daan import Daan

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Daan().run()
