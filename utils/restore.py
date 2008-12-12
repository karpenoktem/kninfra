from __future__ import with_statement

import sys
import _import
import simplejson

import django.db as db
from django.db.models import Model
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from kn.leden.models import KnUser, KnGroup, Seat, Alias, EduInstitute,\
			    Study

def restore(d):
	for name, _list in d.iteritems():
		model = globals()[name]
		print ' --- %s ---' % model
		fields = dict()
		for raw_dict in _list:
			cleaned = dict()
			for key, val in raw_dict.iteritems():
				skey = key
				if not key in fields:
					fields[key] = model._meta.get_field(key)
				field = fields[key]
				if isinstance(field, db.models.ForeignKey):
					cleaned[field.attname] = raw_dict[key]
				elif isinstance(field,
						db.models.ManyToManyField):
					pass
				else:
					cleaned[str(key)] = field.to_python(
							raw_dict[skey])
			obj = model.objects.create(**cleaned)
			for key, field in fields.iteritems():
				if not isinstance(field,
						db.models.ManyToManyField):
					continue
				relman = getattr(obj, key)
				for v in raw_dict[key]:
					relman.add(v)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Usage: restore.py <file>"
		sys.exit(-1)
	if sys.argv[1] == '-':
		f = sys.stdin
	else:
		f = open(sys.argv[1])
	restore(simplejson.load(sys.stdin))
	f.close()
