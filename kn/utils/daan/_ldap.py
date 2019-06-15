import hashlib
import logging

import ldap
import ldap.modlist
import six

from django.conf import settings


def nthash(password):
    return hashlib.new('md4', password.encode('utf-16le')).hexdigest().upper()


def ldap_setpass(user, password):
    if not password:
        return
    if not settings.LDAP_PASS:
        logging.warning('ldap: no credentials available, skipping')
        return
    ld = ldap.initialize(settings.LDAP_URL)
    ld.bind_s(settings.LDAP_USER, settings.LDAP_PASS)
    udn = 'uid=%s,%s' % (user, settings.LDAP_BASE)
    try:
        # Set LDAP password
        ld.passwd_s(udn, None, password)
        # Set SAMBA password entries (to support MSCHAPv2 authentication
        # for WiFi via FreeRADIUS via LDAP).
        res = ld.search_s(settings.LDAP_BASE, ldap.SCOPE_ONELEVEL,
                          'uid=%s' % user)
        if not res:
            return
        _o = res[0][1]
        if 'sambaNTPassword' in _o:
            ld.modify_s(udn, ldap.modlist.modifyModlist(
                {'sambaNTPassword': _o['sambaNTPassword'][0]},
                {'sambaNTPassword': [nthash(password).encode('utf-8')]}))
        else:
            # NOTE See /doc/ldap/scheme.ldif
            #      We added the scheme *after* the creation of the database.
            #      Thus, the user may still miss the objectClass knAccount.
            ld.modify_s(udn, ldap.modlist.modifyModlist(
                {'objectClass': _o['objectClass']},
                {'objectClass': _o['objectClass'] + [b'knAccount'],
                 'sambaNTPassword': [nthash(password).encode('utf-8')]}))
    finally:
        ld.unbind_s()

# TODO exception safety


def apply_ldap_changes(changes):
    if not changes.upsert and not changes.remove:
        return
    ld = ldap.initialize(settings.LDAP_URL)
    ld.bind_s(settings.LDAP_USER, settings.LDAP_PASS)
    try:
        for uid in changes.remove:
            if six.PY3:
                # pyldap is a bit inconsistent with unicode/bytes API between
                # python 2 and python 3.
                uid = uid.decode()
            dn = 'uid=' + uid + ',' + settings.LDAP_BASE
            ld.delete_s(dn)
        for ldapUser in changes.upsert:
            uid = ldapUser.uid
            if six.PY3:
                uid = uid.decode()
            dn = 'uid=' + uid + ',' + settings.LDAP_BASE
            res = ld.search_s(settings.LDAP_BASE, ldap.SCOPE_ONELEVEL,
                              'uid=' + uid)
            if not res:
                entry = {'objectClass': [b'inetOrgPerson'],
                         'uid': [uid.encode()],
                         'sn': [ldapUser.lastName],
                         'cn': [ldapUser.humanName],
                         'mail': [ldapUser.email]}
                ld.add_s(dn, ldap.modlist.addModlist(entry))
                continue
            _o = res[0][1]
            old = {'uid': _o['uid'][0],
                   'sn': _o['sn'][0],
                   'cn': _o['cn'][0],
                   'mail': _o['mail'][0]}
            new = {'uid': [uid.encode()],
                   'sn': [ldapUser.lastName],
                   'cn': [ldapUser.humanName],
                   'mail': [ldapUser.email]}
            ld.modify_s(dn, ldap.modlist.modifyModlist(old, new))
    finally:
        ld.unbind_s()

# vim: et:sta:bs=2:sw=4:
