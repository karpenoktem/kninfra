from __future__ import with_statement
import _import

from unix import sync_unix
from mailman import sync_mailman
from vpopmail import sync_vpopmail
from commissions import sync_commissions

import os.path
import sys

def sync_all():
	sync_commissions()
	sync_vpopmail()
	sync_mailman()
	sync_unix()

if __name__ == '__main__':
	p = os.path.dirname(sys.argv[0])
	if p != '': os.chdir(p)
	sync_all()
