import _import

import logging

from kn.utils.giedo import Giedo

if __name__ == '__main__':
        logging.basicConfig(level=logging.DEBUG)
        Giedo().run()
