import logging
import itertools

import MySQLdb

import kn.leden.entities as Es

from django.conf import settings


def generate_forum_changes(self):
    creds = settings.FORUM_MYSQL_SECRET
    if not creds:
        logging.warning('forum: no credentials available, skipping')
        return None
    users = dict()
    dc = MySQLdb.connect(creds[0], user=creds[1],
                         passwd=creds[2], db=creds[3])
    c = dc.cursor()
    c.execute("SELECT username, realname FROM users")
    todo = {'add': [], 'remove': [], 'update-realname': []}

    cur, old = Es.by_name('leden').get_current_and_old_members()
    for m in itertools.chain(cur, old):
        users[str(m.name)] = m
    for user, realname in c.fetchall():
        user = user.lower()
        if realname is not None:
            realname = realname.decode('latin1')
        if user not in users:
            if user == 'guest':
                continue
            todo['remove'].append(user)
            logging.info("forum: removing user %s", user)
        else:
            if users[user].humanName != realname:
                todo['update-realname'].append((user,
                                                unicode(users[user].humanName)))
            del users[user]
    for name, user in users.iteritems():
        todo['add'].append((name, unicode(user.humanName),
                            user.canonical_email))
    c.close()
    dc.close()
    return todo

# vim: et:sta:bs=2:sw=4:
