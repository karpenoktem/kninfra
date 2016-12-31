import logging

import ldap

import kn.leden.entities as Es

from django.conf import settings

def generate_ldap_changes(giedo):
    if not settings.LDAP_PASS:
        logging.warning('ldap: no credentials available, skipping')
        return None
    todo = {'upsert': [], 'remove': []}
    l = ldap.open(settings.LDAP_HOST)
    l.bind_s(settings.LDAP_USER, settings.LDAP_PASS)
    try:
        users = Es.by_name('leden').get_members()
        unaccounted_for = set()
        in_ldap = {}
        for dn, entry in l.search_s(settings.LDAP_BASE, ldap.SCOPE_ONELEVEL):
            unaccounted_for.add(entry['uid'][0])
            in_ldap[(entry['uid'][0])] = (entry['uid'][0],
                                          entry['mail'][0],
                                          entry['sn'][0],
                                          entry['cn'][0])
        for u in users:
            uid = str(u.name)
            should_have = (uid,
                           u.canonical_email,
                           u.last_name.encode('utf-8'),
                           unicode(u.humanName).encode('utf-8'))
            if uid in unaccounted_for:
                unaccounted_for.remove(uid)
                if in_ldap[uid] == should_have:
                    continue
                logging.info('ldap: updating %s', uid)
            else:
                logging.info('ldap: adding %s', uid)
            todo['upsert'].append(should_have)

        for uid in unaccounted_for:
            todo['remove'].append(uid)
            logging.info('ldap: removing %s', uid)
    finally:
        l.unbind_s()
    return todo

# vim: et:sta:bs=2:sw=4:
