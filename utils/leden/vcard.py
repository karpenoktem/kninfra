# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import vobject
import tarfile
import sys

from common import *

from cStringIO import StringIO


def vcard(u):
    c = vobject.vCard()
    c.add('n')
    ln = ' '.join(reversed(map(lambda x: x.strip(),
                   u.last_name.split(',', 1))))
    c.n.value = vobject.vcard.Name(ln,
                       given=u.first_name)
    c.add('fn')
    c.fn.value = u.full_name()
    l = c.add('email', 'kn')
    l.value = u.primary_email
    l.type_paramlist = ['INTERNET']
    c.add('X-ABLabel', 'kn').value = 'kn'
    if not u.telephone is None:
        c.add('tel', 'kn')
        c.tel.value = u.telephone
        c.tel.type_param = 'CELL'
    if (not u.addr_street is None and
        not u.addr_city is None and
        not u.addr_number is None and
        not u.addr_zipCode is None):
        l = c.add('adr', 'kn')
        l.value = vobject.vcard.Address(' '.join((u.addr_street,
                              u.addr_number)),
                        u.addr_city,
                        '',
                        u.addr_zipCode,
                        'Nederland')
        c.add('x-abadr', 'kn').value = 'nl'
    return c.serialize()

if __name__ == '__main__':
    tb = StringIO()
    tf = tarfile.open(mode='w', fileobj=tb)
    for u in args_to_users(sys.argv[1:]):
        ti = tarfile.TarInfo(u.username + ".vcf")
        td = vcard(u)
        ti.size = len(td)
        tf.addfile(ti, StringIO(td))
    tf.close()
    print tb.getvalue()
