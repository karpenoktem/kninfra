import _import

from django.contrib.auth.models import Permission, User, Group
from kn.leden.models import KnUser, KnGroup, Seat, Alias
from django.db.models import FieldDoesNotExist

import datetime
import django.db as db
import simplejson as json

def dump(model):
	ret = list()
	models_found = set()
	fields = list()
	for f_name in model._meta.get_all_field_names():
		try:
			f = model._meta.get_field(f_name)
		except FieldDoesNotExist:
			continue
		fields.append(f)
		if isinstance(f, db.models.ForeignKey):
			models_found.add(f.rel.to)
		if isinstance(f, db.models.related.ManyToManyField):
			models_found.add(f.rel.to)
	
	for item in model.objects.select_related(depth=1).all():
		dumped = dict()
		for f in fields:
			if isinstance(f, db.models.ForeignKey):
				dumped[f.name] = getattr(item, f.attname)
				continue
			if isinstance(f,
				db.models.fields.related.ManyToManyField):
				m = getattr(item, f.attname)
				dumped[f.name] = map(lambda x: x.pk, m.all())
				continue
			v = getattr(item, f.name)
			if isinstance(v, datetime.datetime) or \
			   isinstance(v, datetime.date):
				dumped[f.name] = f.value_to_string(
							item)
				continue
			dumped[f.name] = getattr(item, f.attname)
		json.dumps(dumped)
		ret.append(dumped)
	return ret, models_found

def dump_all(models, ignore=[]):
	tocheck = list(models)
	had = set(map(lambda x: x.__name__, ignore + models))
	ret = dict()
	while len(tocheck) != 0:
		m = tocheck.pop()
		a_dump, models_found = dump(m)
		for model_found in models_found:
			if not model_found.__name__ in had:
				tocheck.append(model_found)
				had.add(model_found.__name__)
		assert not m.__name__ in ret
		ret[m.__name__] = a_dump
	return ret

if __name__ == '__main__':
	 print json.dumps(dump_all((Alias, Seat), (User, Group)))
