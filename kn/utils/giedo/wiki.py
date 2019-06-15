import itertools
import logging

import pymysql

from django.conf import settings
from django.utils import six

import kn.leden.entities as Es
import kn.utils.daan.daan_pb2 as daan_pb2


def generate_wiki_changes():
    creds = settings.WIKI_MYSQL_SECRET
    if not creds:
        logging.warning('wiki: no credentials available, skipping')
        return None
    users = dict()
    id2name = dict()
    dc = pymysql.connect(
        host=creds[0],
        user=creds[1],
        password=creds[2],
        db=creds[3],
        charset='utf8'
    )
    try:
        with dc.cursor() as c:
            c.execute("SELECT user_id, user_name FROM user")
            todo = daan_pb2.WikiChanges()

            cur, old = Es.by_name('leden').get_current_and_old_members()
            for m in itertools.chain(cur, old):
                if str(m.name) == 'admin':
                    logging.warning("wiki can't handle an admin user")
                    continue
                users[str(m.name)] = m
            ausers = set([u for u in users if users[u].is_active])

            for uid, user in c.fetchall():
                user = user.lower()
                if six.PY3:
                    user = user.decode()
                if user not in users:
                    if user == 'admin':
                        continue
                    todo.remove.append(user)
                    logging.info("wiki: removing user %s", user)
                else:
                    id2name[uid] = user
                    del users[user]
            for name, user in six.iteritems(users):
                todo.add.append(daan_pb2.WikiUser(
                    name=name,
                    humanName=six.text_type(user.humanName),
                    email=user.canonical_email))

            c.execute("""SELECT ug_user FROM user_groups
                         WHERE ug_group=%s""", 'leden')
            for uid, in c.fetchall():
                if uid not in id2name:
                    continue
                user = id2name[uid]
                if user not in ausers:
                    todo.deactivate.append(user)
                else:
                    ausers.remove(user)

            for name in ausers:
                todo.activate.append(name)
    finally:
        dc.close()
    return todo

# vim: et:sta:bs=2:sw=4:
