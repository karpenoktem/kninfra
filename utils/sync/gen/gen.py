from __future__ import with_statement
import _import

from unix import sync_unix
from wiki import sync_wiki
from forum import sync_forum
from photos import sync_photos
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
	sync_photos()
	sync_wiki()
	sync_forum('zeusForum.login')
	sync_forum('forum.login')

if __name__ == '__main__':
	p = os.path.dirname(sys.argv[0])
	if p != '': os.chdir(p)
	sync_all()
