import _import
import vobject
import sys

from common import *

from kn.leden.models import KnUser

def vcard(u):
	c = vobject.vCard()
	c.add('n')
	ln = ' '.join(reversed(map(lambda x: x.strip(),
				   u.last_name.split(',', 1))))
	c.n.value = vobject.vcard.Name(ln,
				       given=u.first_name)
	c.add('fn')
	c.fn.value = u.get_full_name()
	l = c.add('email', 'kn')
	l.value = u.primary_email
	l.type_paramlist = ['INTERNET']
	c.add('X-ABLabel', 'kn').value='kn'
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
		c.add('x-abadr', 'kn').value='nl'
	return c.serialize()

if __name__ == '__main__':
	for u in args_to_users(sys.argv[1:]):
		print vcard(u)
