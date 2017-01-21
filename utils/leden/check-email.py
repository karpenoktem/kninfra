# vim: et:sta:bs=2:sw=4:

import _import  # noqa: F401
from common import args_to_users

from kn.leden.mongo import _id
import kn.leden.entities as Es
from kn.leden.date import now

from django.core.mail import send_mail
from django.template import Context, Template

import sys
from cStringIO import StringIO

DAYS_IN_YEAR = 365.242199


def check_email():
    dt_now = now()
    comm_ids = map(_id, Es.by_name('comms').get_bearers())
    list_ids = map(_id, Es.by_name('lists-opted').get_bearers())
    with open('check-email.template') as f:
        template_text = StringIO()
        for line in f:
            if line.endswith("\\\n"):
                template_text.write(line[:-2])
            else:
                template_text.write(line)
        templ = Template(template_text.getvalue())
    for m in args_to_users(sys.argv[1:]):
        rels = m.get_related()
        rels = sorted(rels, cmp=lambda x, y: cmp(str(x['with'].humanName),
                                                 str(y['with'].humanName)))
        comms = []
        lists = []
        others = []
        for rel in rels:
            if Es.relation_is_virtual(rel):
                continue
            if _id(rel['with']) in comm_ids:
                comms.append(rel)
            elif _id(rel['with']) in list_ids:
                lists.append(rel)
            else:
                others.append(rel)
        print m.name
        em = templ.render(Context({
                        'u': m,
                        'comms': comms,
                        'lists': lists,
                        'others': others}))
        send_mail('Controle Karpe Noktem ledenadministratie',
                  em, 'secretaris@karpenoktem.nl',
                  [m.primary_email])

if __name__ == '__main__':
    check_email()
