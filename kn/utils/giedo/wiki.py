import MySQLdb
import logging
import itertools

import kn.leden.entities as Es

from kn import settings

def generate_wiki_changes(self):
        users = dict()
        id2name = dict()
        creds = settings.WIKI_MYSQL_CREDS
        dc = MySQLdb.connect(creds[0], user=creds[1],
                        passwd=creds[2], db=creds[3])
        c = dc.cursor()
        c.execute("SELECT user_id, user_name FROM user")
        todo = {'add': [], 'remove': [], 'activate': [], 'deactivate': []}

        cur, old = Es.by_name('leden').get_current_and_old_members()
        for m in itertools.chain(cur, old):
                users[str(m.name)] = m
        leden = filter(lambda x: x.is_active, users)

        for uid, user in c.fetchall():
                user = user.lower()
                if user not in users:
                        if user == 'admin':
                                continue
                        todo['remove'].append(user)
                        logging.info("wiki: removing user %s", user)
                else:
                        id2name[uid] = user
                        del users[user]
        for name, user in users.iteritems():
                todo['add'].append((name, unicode(user.humanName),
                                        user.canonical_email))

        c.execute("SELECT ug_user FROM user_groups WHERE ug_group=%s", 'leden')
        for uid, in c.fetchall():
                user = id2name[uid]
                if user not in leden:
                        todo['deactivate'].append(user)
                else:
                        del leden[user]

        for name, in users.iteritems():
                todo['activate'].append(name)

        c.close()
        dc.close()
        return todo
