# vim: et:sta:bs=2:sw=4:
import hashlib
import logging
import time

import pymysql

from django.conf import settings

from kn.base._random import pseudo_randstr


def forum_setpass(daan, user, password):
    creds = settings.FORUM_MYSQL_SECRET
    if not creds:
        logging.warning('forum: no credentials available, skipping')
        return None
    dc = pymysql.connect(
        host=creds[0],
        user=creds[1],
        password=creds[2],
        db=creds[3],
        charset='utf8'
    )
    try:
        with dc.cursor() as c:
            salt = pseudo_randstr()
            h = hashlib.sha1(password).hexdigest()
            h = hashlib.sha1(salt + h).hexdigest()
            c.execute("""
                UPDATE users
                SET password=%s, salt=%s
                WHERE username=%s;""",
                      (h, salt, user))
            dc.commit()
    finally:
        dc.close()


def apply_forum_changes(daan, changes):
    if not changes:
        return
    creds = settings.FORUM_MYSQL_SECRET
    dc = pymysql.connect(
        host=creds[0],
        user=creds[1],
        password=creds[2],
        db=creds[3],
        charset='utf8'
    )
    try:
        with dc.cursor() as c:
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
            dc.commit()
    finally:
        dc.close()
