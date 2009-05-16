from common import *
import MySQLdb
import hashlib

def setpass(loginFile, user, passwd):
	dbuser, dbname, dbpasswd = read_ssv_file(loginFile)
	dc = MySQLdb.connect(host='localhost', user=dbuser, passwd=dbpasswd,
			db=dbname)
	c = dc.cursor()
	salt = pseudo_randstr()
	h = hashlib.sha1()
	h.update(passwd)
	hash = h.hexdigest()
	h = hashlib.sha1()
	h.update(salt)
	h.update(hash)
	hash = h.hexdigest()
	c.execute("UPDATE users SET password=%s, salt=%s WHERE username=%s;",
			(hash, salt, user))
	c.fetchall()
	
