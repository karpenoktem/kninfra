# vim: et:sta:bs=2:sw=4:
import logging

import os.path

from kn.settings import POSTFIX_VIRTUAL_MAP
from subprocess import call

def set_postfix_map(daan, tbl):
        # TODO check whether the entries are valid and within karpenoktem.nl!
        with open(POSTFIX_VIRTUAL_MAP, 'w') as f:
                for k, v in tbl.iteritems():
                        v = filter(lambda x: x, v)
                        if not v:
                                continue
                        f.write("%s %s\n" % (k, ', '.join(v)))
        call(['postmap', POSTFIX_VIRTUAL_MAP])