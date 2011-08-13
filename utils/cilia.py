import _import

import logging

from kn.utils.cilia import Cilia

if __name__ == '__main__':
        logging.basicConfig(level=logging.DEBUG)
        Cilia().run()
