#!/usr/bin/python
from __future__ import print_function

import _import  # noqa: F401
import argparse
import getpass
import subprocess

import pymysql

from django.conf import settings

import kn.leden.entities as Es


def change_username(oldname, newname, do):
    if getpass.getuser() != 'root':
        print('Cannot rename user: not root')
        return

    e = Es.by_name(newname)
    if oldname not in e._data['names']:
        print('name %r not in entity %r' % (oldname, e))
        return

    if e.type != 'user':
        print('entity %r is not a user' % e)
        return

    print('kninfra names (old):', e._data['names'])
    e._data['names'].remove(newname)
    e._data['names'].insert(0, newname)
    print('kninfra names (new):', e._data['names'])
    print('email:', e.canonical_email)

    rootpassword = getpass.getpass('MySQL root password:')  # for wolk
    if not rootpassword:
        print('no MySQL root password entered')
        return

    # Update OwnCloud
    creds = settings.WOLK_MYSQL_SECRET
    dc = pymysql.connect(
        host=creds[0],
        user='root',  # needed for UPDATE
        password=rootpassword,
        db=creds[3],
        charset='utf8'
    )
    try:
        c = dc.cursor()
        n = c.execute("UPDATE oc_users SET uid=%s WHERE uid=%s;",
                      (newname, oldname))
        print('wolk: updated oc_users.uid:', n)
        if not n:
            print('WARNING: could not find user %s in wolk' % (oldname))
        print('wolk: updated oc_activity.user:',
              c.execute("UPDATE oc_activity SET user=%s WHERE user=%s;",
                        (newname, oldname)))
        print('wolk: updated oc_activity.affecteduser:',
              c.execute("UPDATE oc_activity SET affecteduser=%s " +
                        "WHERE affecteduser=%s;",
                        (newname, oldname)))
        print('wolk: updated oc_clndr_calendars.affecteduser:',
              c.execute(
                  "UPDATE oc_clndr_calendars SET userid=%s WHERE userid=%s;",
                  (newname, oldname)
              ))
        print('wolk: updated oc_contacts_addressbooks.userid:',
              c.execute("UPDATE oc_contacts_addressbooks " +
                        "SET userid=%s WHERE userid=%s;",
                        (newname, oldname)))
        print('wolk: updated oc_files_trash.user:',
              c.execute("UPDATE oc_files_trash SET user=%s WHERE user=%s;",
                        (newname, oldname)))
        print('wolk: updated oc_group_user.uid:',
              c.execute("UPDATE oc_group_user SET uid=%s WHERE uid=%s;",
                        (newname, oldname)))
        print('wolk: updated oc_preferences.userid:',
              c.execute("UPDATE oc_preferences SET userid=%s WHERE userid=%s;",
                        (newname, oldname)))
        print('wolk: updated oc_share.share_with:',
              c.execute("UPDATE oc_share SET share_with=%s " +
                        "WHERE share_with=%s;",
                        (newname, oldname)))
        print('wolk: updated oc_share.uid_owner:',
              c.execute("UPDATE oc_share SET uid_owner=%s WHERE uid_owner=%s;",
                        (newname, oldname)))
        print('wolk: updated oc_storages.id:',
              c.execute("UPDATE oc_storages SET id=%s WHERE id=%s;",
                        ('home::' + newname, 'home::' + oldname)))
        # TODO: oc_jobs (uses JSON!) and maybe other tables
        # (check a MySQL dump before running this script!)
        if not do:
            # WARNING: this does not appear to work,
            # the change is applied anyway
            dc.rollback()
    except Exception:
        dc.rollback()
        dc.close()
        raise
    else:
        c.close()
        if do:
            dc.commit()
        dc.close()

    if do:
        e.save()

    print('TODO:')
    print(' * change name in the wiki: ' +
          'https://karpenoktem.nl/wiki/Speciaal:GebruikerHernoemen')
    print(' * unimplemented: wiki, LDAP')
    print(' * start giedo again (if stopped)')
    print(' * run giedo-sync while watching the log')

    if not do:
        print('---')
        print('Everything seems okay. ' +
              'It may be a good idea to stop giedo while renaming.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rename a user')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('old', type=str)
    parser.add_argument('new', type=str)
    args = parser.parse_args()
    change_username(args.old, args.new, args.apply)
