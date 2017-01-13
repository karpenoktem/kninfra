# vim: et:sta:bs=2:sw=4:
from __future__ import with_statement

import _import # noqa: F401
from common import *
from kn.leden.models import OldKnGroup


def forum_email():
    with open('fools-email.template', 'r') as f:
        templ = f.read()
    l5 = OldKnGroup.objects.get(name=MEMBER_GROUP).user_set.all()
    for m in l5:
        txt = templ % ({'username': m.username})
        m.email_user(
            'LEES DIT: BELANGRIJK',
            txt, from_email='karpenoktemwebcie@hotmail.com')
        print m.username

if __name__ == '__main__':
    forum_email()
