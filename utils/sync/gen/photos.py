from common import * #settings
import MySQLdb

from kn.leden.models import Member
import os

MEMBERS_ALBUM = "per-lid"

def sync_photos():
	sync_members_album()

def sync_members_album():
	msa = os.path.join(GALLERY_PATH, MEMBERS_ALBUM)

	members = dict([(m.username,m) for m in Member.objects.all()])
	
	if not os.path.exists(msa):
		print "photos mkdir %s " % sesc(msa)
	else:
		for name in os.listdir(msa):
			ma = os.path.join(msa,name)
			if name not in members:
				print "photos rm %s" % sesc(ma)
				continue
			# The link will be checked in the next loop.

	for member in members.values():
		mh = os.path.expanduser('~%s'%member.username)
		if not os.path.exists(mh):
			print "warn %s's home, %s, does not exist" % (
					member.username,mh)
			continue
		mf = os.path.join(mh, MEMBER_PHOTO_DIR)
		if not os.path.exists(mf):
			continue
		ma = os.path.join(msa, member.username)
		if not os.path.exists(ma):
			print "photos symlink %s %s" % (sesc(mf),sesc(ma))
			continue
		if not os.path.islink(ma):
			print "warn %s's album, %s, is not a link." % (
					member.username, ma)
			continue
		if os.readlink(ma)!=mf:
			print (("warn %s's album, %s, does not link to her/his" 
					+ " photodir, %s.") % (member.username,
						ma, mf))

