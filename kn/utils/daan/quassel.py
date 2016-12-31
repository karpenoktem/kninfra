import os.path
import sqlite3
import hashlib
import logging

from django.conf import settings
from kn.base._random import pseudo_randstr


def quassel_setpass(daan, user, password):
    if settings.QUASSEL_CONFIGDIR is None:
        logging.warning('no QUASSEL_CONFIGDIR available, skipping')
        return
    db_path = os.path.join(settings.QUASSEL_CONFIGDIR, 'quassel-storage.sqlite')
    conn = sqlite3.connect(db_path)
    hashed_pw = hashlib.sha1(password).hexdigest()
    c = conn.cursor()
    try:
        c.execute("UPDATE quasseluser SET password=? where username=?",
                                        (hashed_pw, user))
        conn.commit()
    except sqlite3.OperationalError:
        logging.exception("OperationalError")

def apply_quassel_changes(daan, changes):
    if not changes:
        return
    if settings.QUASSEL_CONFIGDIR is None:
        logging.warning('no QUASSEL_CONFIGDIR available, skipping')
        return
    db_path = os.path.join(settings.QUASSEL_CONFIGDIR, 'quassel-storage.sqlite')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for user in changes['remove']:
        logging.info('quassel: removing %s', user)
        c.execute("SELECT userid FORM quasseluser WHERE username=?", (user,))
        userid, = c.fetchone()
        c.execute("DELETE FROM quasseluser WHERE username=?", (user,))
        c.execute("DELETE FROM identity WHERE userid=?", (userid,))
        c.execute("DELETE FROM ircserver WHERE userid=?", (userid,))
        c.execute("DELETE FROM user_setting WHERE userid=?", (userid,))
        c.execute("DELETE FROM buffer WHERE userid=?", (userid,))
        c.execute("DELETE FROM network WHERE userid=?", (userid,))
    for user in changes['add']:
        logging.info('quassel: adding %s', user)
        hashed_pw = hashlib.sha1(pseudo_randstr()).hexdigest()
        c.execute("INSERT INTO quasseluser(username, password) VALUES (?, ?)",
                    (user, hashed_pw))
    conn.commit()

# vim: et:sta:bs=2:sw=4:
