import logging

import ldap
import protobufs.messages.daan_pb2 as daan_pb2

from django.conf import settings
from django.utils import six

import kn.leden.entities as Es


def generate_ldap_changes():
    if not settings.LDAP_PASS:
        logging.warning('ldap: no credentials available, skipping')
        return None
    todo = daan_pb2.LDAPChanges()
    ld = ldap.initialize(settings.LDAP_URL)
    ld.bind_s(settings.LDAP_USER, settings.LDAP_PASS)
    try:
        users = Es.by_name('leden').get_members()
        unaccounted_for = set()
        in_ldap = {}
        for dn, entry in ld.search_s(settings.LDAP_BASE, ldap.SCOPE_ONELEVEL):
            unaccounted_for.add(entry['uid'][0])
            in_ldap[(entry['uid'][0])] = daan_pb2.LDAPUser(
                uid=entry['uid'][0],
                email=entry['mail'][0],
                lastName=entry['sn'][0],
                humanName=entry['cn'][0]
            )
        for u in users:
            uid = str(u.name).encode('utf-8')
            should_have = daan_pb2.LDAPUser(
                uid=uid,
                email=u.canonical_email.encode('utf-8'),
                lastName=u.last_name.encode('utf-8'),
                humanName=six.text_type(u.humanName).encode('utf-8'))
            if uid in unaccounted_for:
                unaccounted_for.remove(uid)
                if in_ldap[uid] == should_have:
                    continue
                logging.info('ldap: updating %s', uid)
            else:
                logging.info('ldap: adding %s', uid)
            todo.upsert.append(should_have)

        for uid in unaccounted_for:
            todo.remove.append(uid)
            logging.info('ldap: removing %s', uid)
    finally:
        ld.unbind_s()
    return todo

# vim: et:sta:bs=2:sw=4:
