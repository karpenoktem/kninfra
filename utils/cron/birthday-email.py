# vim: et:sta:bs=2:sw=4:
from __future__ import with_statement

import _import  # noqa: F401
import datetime

from django.core.mail import EmailMessage

import kn.leden.entities as Es


def birthday_email():
    with open('birthday-email.template') as f:
        templ = f.read()
    now = datetime.datetime.now().date()
    for user in Es.by_name('leden').get_members():
        if user.dateOfBirth is None:
            continue
        if (user.dateOfBirth.day != now.day or
                user.dateOfBirth.month != now.month):
            continue
        email = EmailMessage("Hartelijk gefeliciteerd!",
                             templ % {'firstName': user.first_name},
                             'webcie@karpenoktem.nl',
                             [user.canonical_email],
                             ['webcie@karpenoktem.nl'])
        email.send()


if __name__ == '__main__':
    birthday_email()
