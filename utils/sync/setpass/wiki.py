from common import *
import MySQLdb
import hashlib

def setpass(user, passwd):
	dbuser, dbname, dbpasswd = read_ssv_file('wiki.login')
	dc = MySQLdb.connect(host='localhost', user=dbuser, passwd=dbpasswd,
			db=dbname)
	c = dc.cursor()
	user = user.capitalize()
	c.execute("SELECT user_id FROM user WHERE user_name=%s;", user)
	user_id, = c.fetchone()
	h = hashlib.md5()
	h.update(passwd)
	hash = h.hexdigest()
	h = hashlib.md5()
	h.update("%s-%s" % (user_id, hash))
	hash = h.hexdigest()
	c.execute("UPDATE user SET user_password=%s WHERE user_name=%s;",
			(hash, user))
	c.execute("commit;")
