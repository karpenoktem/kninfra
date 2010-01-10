from common import *
import MySQLdb
from hashlib import md5

def setpass(user, passwd):
	hashed_passwd = md5.new(user+passwd).hexdigest()

	dbuser, dbname, dbpasswd = read_ssv_file('photos.login')
	dc = MySQLdb.connect(host='localhost', user=dbuser, passwd=dbpasswd,
			db=dbname)
	c = dc.cursor()
	c.execute("""	UPDATE zp_administrators 
			SET pass=%s 
			WHERE user=%s""", (hashed_passwd, user))
