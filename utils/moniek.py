# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import logging

from kn.utils.moniek import Moniek

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(relativeCreated)d %(levelname)-8s%(name)s:%(message)s")
    Moniek().run()
