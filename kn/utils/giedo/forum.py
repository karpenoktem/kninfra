import MySQLdb
import logging
import itertools

import kn.leden.entities as Es

from kn import settings

def generate_forum_changes(self):
        users = dict()
        creds = settings.FORUM_MYSQL_CREDS
        dc = MySQLdb.connect(creds[0], user=creds[1],
                        passwd=creds[2], db=creds[3])
        c = dc.cursor()
        c.execute("SELECT username FROM users")
        todo = {'add': [], 'remove': []}

        cur, old = Es.by_name('leden').get_current_and_old_members()
        for m in itertools.chain(cur, old):
                users[str(m.name)] = m
        for user, in c.fetchall():
                user = user.lower()
                if user not in users:
                        if user == 'guest':
                                continue
                        todo['remove'].append(user)
                        logging.info("forum: removing user %s", user)
                else:
                        del users[user]
        for name, user in users.iteritems():
                todo['add'].append((name, unicode(user.humanName),
                                        user.canonical_email))
        c.close()
        dc.close()
        return todo
