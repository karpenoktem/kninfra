import itertools
import logging

import pymysql

from django.conf import settings
from django.utils import six

import kn.leden.entities as Es


def generate_forum_changes(self):
    creds = settings.FORUM_MYSQL_SECRET
    if not creds:
        logging.warning('forum: no credentials available, skipping')
        return None
    users = dict()
    dc = pymysql.connect(
        host=creds[0],
        user=creds[1],
        password=creds[2],
        db=creds[3],
        charset='utf8'
    )
    try:
        with dc.cursor() as c:
            c.execute("SELECT username, realname FROM users")
            todo = {'add': [], 'remove': [], 'update-realname': []}

            cur, old = Es.by_name('leden').get_current_and_old_members()
            for m in itertools.chain(cur, old):
                users[str(m.name)] = m
            for user, realname in c.fetchall():
                user = user.lower()
                if realname and six.PY2:
                    realname = realname.decode('latin1')
                if user not in users:
                    if user == 'guest':
                        continue
                    todo['remove'].append(user)
                    logging.info("forum: removing user %s", user)
                else:
                    if users[user].humanName != realname:
                        logging.info("forum: updating realname of %s", user)
                        todo['update-realname'].append(
                            (user, six.text_type(users[user].humanName))
                        )
                    del users[user]
            for name, user in six.iteritems(users):
                logging.info("forum: adding %s", user)
                todo['add'].append((name, six.text_type(user.humanName),
                                    user.canonical_email))
    finally:
        dc.close()
    return todo

# vim: et:sta:bs=2:sw=4:
