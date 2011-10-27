# vim: et:sta:bs=2:sw=4:
from kn.leden.mongo import  db, SONWrapper, son_property, _id

import kn.leden.entities as Es

mcol = db['moderation_records']

def ensure_indices():
        mcol.ensure_index('list')

class ModerationRecord(SONWrapper):
        def __init__(self, data):
                super(ModerationRecord, self).__init__(data, mcol)
        list = son_property(('list',))
        at = son_property(('at',))
        by_id = son_property(('by',))
        
        def get_by(self):
                return Es.by_id(self._data['by'])
        def set_by(self, x):
                self._data['by'] = _id(x)
        by = property(get_by, set_by)

def by_name(name):
        d = mcol.find_one({'list': name})
        return None if d is None else ModerationRecord(d)
