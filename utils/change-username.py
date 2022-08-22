#!/usr/bin/python
from __future__ import print_function

import _import  # noqa: F401
import argparse
import getpass
import subprocess

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

    print('TODO:')
    print(' * change name in the wiki: ' +
          'https://karpenoktem.nl/wiki/Speciaal:GebruikerHernoemen')
    print(' * unimplemented: wiki')
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
