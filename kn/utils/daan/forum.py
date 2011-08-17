import logging
import MySQLdb
import time

from kn import settings

def apply_forum_changes(daan, changes):
        creds = settings.FORUM_MYSQL_CREDS
        dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2],
                                db=creds[3])
        for user, realname, email in changes['add']:
                c = dc.cursor()
                q = """INSERT INTO users (`username`,
                                          `password`,
                                          `email`,
                                          `realname`,
                                          `registered`)
                        VALUES (%s, %s, %s, %s, %s);"""
                c.execute(q, user, '37', email, realname, int(time.time()))
                c.execute("COMMIT;")
                c.close()
        for user in changes['remove']:
                c = dc.cursor()
                c.execute("DELETE FROM `users` WHERE `username`=%s", user)
                c.execute("COMMIT;")
                c.close()
        dc.close()
