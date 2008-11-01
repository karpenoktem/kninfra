from common import * #settings
import MySQLdb

from kn.leden.models import Member
import os

MEMBERS_ALBUM = "per-lid"

def sync_photos():
	members = dict([(m.username,m) for m in Member.objects.all()])
	
	sync_members_album(members)
	sync_database(members)


def sync_database(members):
	user, db, passwd = read_ssv_file('photos.login')
	dc = MySQLdb.connect(host='localhost', user=user, db=db, passwd=passwd)
	c = dc.cursor()
	c.execute('SELECT id, user, password, name, email, rights '+
			'FROM zp_administrators')
	
	uid = set([])

	for adm in c.fetchall():
		uid.add(adm[1]) #[1]=username
		checkDatabaseAdmin(adm, members)
	
	for member in members.values():
		if member.username in uid:
			continue
		user = member.username
		name = member.get_full_name()
		email = member.username+"@"+DOMAIN
		rights = 258

		print "photos adm-add %s %s %s %s" % (user, sesc(name), 
				email, rights)



def checkDatabaseAdmin(adm, members):
	id, user, passwd, name, email, rights = adm
	if user not in members:
		print "warn gallery admin %s is not a member." % user
		return
	member = members[user]
	member_name = member.get_full_name()
	if member_name!=name:
		print "# %s's name, %s, is outdated," % (user,name) 
		print "photos adm-update %s name %s" % (user,sesc(member_name))	

def sync_members_album(members):
	msa = os.path.join(GALLERY_PATH, MEMBERS_ALBUM)

	if not os.path.exists(msa):
		print "# The members gallery does not exist, so,"
		print "photos mkdir %s " % sesc(msa)
	else:
		for name in os.listdir(msa):
			checkMemberAlbum(msa, members, name)

	for member in members.values():
		checkMemberPhotoDir(msa, member.username)

def memberPhotoDir(username):
	mh = os.path.expanduser('~%s'%username)
	mf = os.path.join(mh, MEMBER_PHOTO_DIR)
	return mf

def checkMemberPhotoDir(msa, name):
	mf = memberPhotoDir(name)
	if not os.path.exists(mf):
		return
	if len(os.listdir(mf))==0:
		return
	ma = os.path.join(msa, name)
	if not os.path.exists(ma):
		print ("# %s has a non-trivial photodir, so, "+
				"let us link an album to it,") % name
		print "photos symlink %s %s" % (sesc(mf),sesc(ma))
		return
	# Since the album exists, it should have been checked.
	# Ah, the smell of race conditions.

def checkMemberAlbum(msa, members, name):
	ma = os.path.join(msa,name)
	if name not in members:
		print "# %s is not a member, so," % name
		print "photos rm %s" % sesc(ma)
		return
	if not os.path.islink(ma):
		print "warn %s's album, %s, is not a link." % (name, ma)
		return
	mf = memberPhotoDir(name)
	lt = os.readlink(ma)
	if lt!=mf:
		print ("warn %s does not link to %s, as instead to %s" 
				% (ma,mf,lt))
		return
	if not os.path.exists(mf):
		print (("# %s's photodir, %s, does not exist, so let " +
			"us remove the link to it,") % (name,mf))
		print "photos rm %s" % sesc(ma)
		return
	if len(os.listdir(mf))==0:
		print (("# %s's photodir, %s, is trivial, so let us remove" +
			" the link to it,")% (name,mf))
		print "photos rm %s" % sesc(ma)




					
