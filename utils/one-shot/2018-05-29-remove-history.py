#!/usr/bin/env python

import _import  # noqa: F401
import argparse

import kn.leden.entities as Es


def remove_history_item(user, plural, singular, key=None, save=False):
    if plural in user._data:
        if singular in user._data:
            print('ERROR: user has "%s" and "%s" as key: %s' % (plural, singular, user))
            return

        if len(user._data[plural]) == 0:
            print('WARNING: user has no "%s": %s' % (plural, user))
            return

        item = user._data[plural][0]
        del item['from']
        del item['until']
        if key is not None:
            item = item[key]
        user._data[singular] = item
        del user._data[plural]

        print('converted: %-20s %s' % (user.name, user._data[singular]))
        if save:
            user.save()
    elif singular in user._data:
        print('ok:        %-20s' % user.name)
    else:
        print('no data:   %-20s' % user.name)


def remove_history(save):
    print('Telephone numbers:')
    for user in Es.users():
        remove_history_item(user, 'telephones', 'telephone', 'number', save=save)

    print('\nEmail addresses:')
    for user in Es.users():
        remove_history_item(user, 'emailAddresses', 'email', 'email', save=save)

    print('\nPost addresses:')
    for user in Es.users():
        remove_history_item(user, 'addresses', 'address', None, save=save)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove historic data from users')
    parser.add_argument('--apply', dest='apply', action='store_true', help='apply all changes')
    args = parser.parse_args()
    remove_history(args.apply)
