# vim: et:sta:bs=2:sw=4:
import logging
import MySQLdb
import hashlib
import time

from kn import settings
from kn.base._random import pseudo_randstr

def forum_setpass(daan, user, password):
    creds = settings.FORUM_MYSQL_SECRET
    dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2], db=creds[3])
    c = dc.cursor()
    salt = pseudo_randstr()
    h = hashlib.sha1(password).hexdigest()
    h = hashlib.sha1(salt + h).hexdigest()
    c.execute("UPDATE users SET password=%s, salt=%s WHERE username=%s;",
            (h, salt, user))
    c.execute("COMMIT;")
    c.close()
    dc.close()

def forum_rename_entity(daan, entity, newname, primary_type):
    creds = settings.FORUM_MYSQL_SECRET
    dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2], db=creds[3])
    c = dc.cursor()
    c.execute("UPDATE users SET username=%s WHERE username=%s;",
            (newname, entity))
    c.execute("UPDATE topics SET poster=%s WHERE poster=%s;", (newname, entity))
    c.execute("UPDATE topics SET last_poster=%s WHERE last_poster=%s;",
            (newname, entity))
    c.execute("UPDATE forums SET last_poster=%s WHERE last_poster=%s;",
            (newname, entity))
    c.execute("UPDATE online SET ident=%s WHERE ident=%s;", (newname, entity))
    c.execute("UPDATE posts SET edited_by=%s WHERE edited_by=%s;",
            (newname, entity))
    # XXX forum-moderators need extra queries to keep them moderators of
    # specific forums and their name could be in the ban-cache. We'll just
    # ignore them for now.
    c.execute("COMMIT;")
    c.close()
    dc.close()

def apply_forum_changes(daan, changes):
    creds = settings.FORUM_MYSQL_SECRET
    dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2],
                db=creds[3])
    c = dc.cursor()
    for user, realname, email in changes['add']:
        q = """INSERT INTO users (`username`,
                      `password`,
                      `email`,
                      `realname`,
                      `registered`)
            VALUES (%s, %s, %s, %s, %s);"""
        c.execute(q, (user, '37', email, realname, int(time.time())))
    for user, realname in changes['update-realname']:
        c.execute("UPDATE users SET realname=%s WHERE username=%s", (
                realname, user))
    for user in changes['remove']:
        c.execute("DELETE FROM `users` WHERE `username`=%s", user)
    c.execute("COMMIT;")
    c.close()
    dc.close()
