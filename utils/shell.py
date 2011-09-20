import _import
try:
	import Mailman.MailList
except ImportError:
	pass

import time
import datetime
import kn.leden.entities as Es
from kn.leden.mongo import _id
from kn.settings import DT_MIN, DT_MAX

def del_rel(who, _with, how):
        """ Removes a relation given by names.

        For instance: del_rel('giedo', 'leden', None) """
        who = Es.id_by_name(who)
        _with = Es.id_by_name(_with)
        how = Es.ecol.find_one({'sofa_suffix': how})['_id'] \
                        if how is not None else None
        Es.rcol.remove({'who': who,
                        'with': _with,
                        'how': how})

def add_rel(who, _with, how, _from, until):
        """ Adds a relation given by strings.

        For instance: add_rel('giedo', 'bestuur', 'voorzitter', '2004-09-01',
                                '2006-09-01') """
        who = Es.id_by_name(who)
        _with = Es.id_by_name(_with)
        how = Es.ecol.find_one({'sofa_suffix': how})['_id'] \
                        if how is not None else None
        _from = str_to_date(_from) if _from is not None else DT_MIN
        until = str_to_date(until) if until is not None else DT_MAX
        Es.rcol.insert({'who': who,
                        'with': _with,
                        'how': how,
                        'from': _from,
                        'until': until})

def str_to_date(s):
        return datetime.datetime(*time.strptime(s, '%Y-%m-%d')[:3])

def add_name(name, extra_name):
        e = Es.by_name(name)
        e._data['names'].append(extra_name)
        e.save()
