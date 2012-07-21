# vim: et:sta:bs=2:sw=4:
import decimal

from regl.model import Document

from django.db.models import permalink

from kn.leden.mongo import db, SONWrapper, _id, son_property, ObjectId

import kn.leden.entities as Es

rcol = db['reglement']
vcol = db['reglement_versions']

def ensure_indices():
    rcol.ensure_index('name', unique=True)
    vcol.ensure_index('reglement', unique=True)
    vcol.ensure_index('name')
    vcol.ensure_index('reglement')
    vcol.ensure_index([('until',1),
                       ('from',-1)])
def all():
    for m in rcol.find():
        yield Reglement(m)

def version_by_names(reglement_name, version_name):
    regl = reglement_by_name(reglement_name)
    if not regl:
        return None
    tmp = vcol.find_one({'name': version_name,
                         'reglement': _id(regl.id)})
    return None if tmp is None else ReglementVersion(tmp)

def reglement_by_name(name):
    tmp = rcol.find_one({'name': name})
    return None if tmp is None else Reglement(tmp)

def reglement_by_id(the_id):
    tmp = rcol.find_one({'_id': _id(the_id)})
    return None if tmp is None else Reglement(tmp)

class Reglement(SONWrapper):
    def __init__(self, data):
        super(Reglement, self).__init__(data, rcol)
    @property
    def id(self):
        return str(self._data['_id'])
    description = son_property(('description',))
    humanName = son_property(('humanName',))
    name = son_property(('name',))

    def get_versions(self):
        for v in vcol.find({'reglement': self._id}).sort('until'):
            yield ReglementVersion(v)

    def __unicode__(self):
        return self.humanName

    @permalink
    def get_absolute_url(self):
        return ('reglement-detail', (), {'name': self.name})

class ReglementVersion(SONWrapper):
    def __init__(self, data):
        super(ReglementVersion, self).__init__(data, vcol)
    @property
    def id(self):
        return str(self._data['_id'])
    @property
    def reglement(self):
        return reglement_by_id(self._data['reglement'])
    def to_html(self):
        if 'html' not in self._data:
            self._data['html'] = Document.from_string(self.regl).to_html()
            self.save()
        return self._data['html']

    description = son_property(('description',))
    humanName = son_property(('humanName',))
    name = son_property(('name',))
    regl = son_property(('regl',))
    valid_from = son_property(('from',))
    valid_until = son_property(('until',))

    def __unicode__(self):
        return self.humanName

    @permalink
    def get_absolute_url(self):
        # TODO eliminate the query in self.reglement.name
        return ('version-detail', (), {
                            'reglement_name': self.reglement.name,
                            'version_name': self.name})
