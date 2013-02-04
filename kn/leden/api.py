import json

from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.validators import email_re

from kn.base.http import JsonHttpResponse
import kn.leden.entities as Es
from kn.leden.mongo import _id
from kn.leden import giedo

@login_required
def view(request):
    data = json.loads(request.REQUEST.get('data', {}))
    action = data.get('action')
    handler = ACTION_HANDLER_MAP.get(action,
                    ACTION_HANDLER_MAP[None])
    return JsonHttpResponse(handler(data, request))

def no_such_action(data, request):
    return {'error': 'No such action'}


def _humanName_of_entity(e):
    """ Returns the human name of an entity, as used in the API. """
    if e.name:
        return "%s (%s)" % (e.humanName, e.name)
    return unicode(e.humanName)

def entities_by_keyword(data, request):
    """ Wraps Es.by_keyword.  Finds the first 20 entities matching the given
        keyword.  Example:
        
          >> {action:"by_keyword", keyword: "giedo"}
          << [["4e6fcc85e60edf3dc0000270", "Giedo Jansen (giedo)"]]

        The return format is optimized for size and compatibility with
        jquery-ui.autocomplete """
    _type = data.get('type', None)
    if _type and not isinstance(_type, basestring):
        _type = None
    return [[e.id, _humanName_of_entity(e)]
                    for e in Es.by_keyword(data.get('keyword', ''),
                                           _type=_type)]

def entity_humanName_by_id(data, request):
    """ Returns the human name of an entity by its id.  Example:

          >> {action:"entity_humanName_by_id", id="4e6fcc85e60edf3dc0000270"}
          << "Giedo Jansen (giedo) """
    e = Es.by_id(data['id'])
    return None if e is None else _humanName_of_entity(e)

def close_note(data, request):
    """ Wraps Note.close()

          >> {action:"close_note", id: "5038b134d4080073f410fafd"}
          << {ok: true}
        ( << {ok: false, error: "Note already closed"} ) """
    if not 'secretariaat' in request.user.cached_groups_names:
        return {'ok': False, 'error': 'Permission denied'}
    note = Es.note_by_id(_id(data.get('id'))) 
    if note is None:
        return {'ok': False, 'error': 'Note not found'}
    if not note.open:
        return {'ok': False, 'error': 'Note already closed'}
    note.close(_id(request.user))
    EmailMessage(
            "Notitie gesloten",
            ("De volgende notitie van %s op %s:\r\n\r\n%s\r\n\r\n"+
             "is door %s gesloten") % (
                    unicode(note.by.humanName), unicode(note.on.humanName),
                    unicode(note.note), unicode(note.closed_by.humanName)),
             'Karpe Noktem\'s ledenadministratie <root@karpenoktem.nl>',
             [Es.by_name('secretariaat').canonical_full_email]).send()
    return {'ok': True}

def entity_update_primary(update_type, data, request):
    """ Updates an entity
            >> (see below)

            << {ok: true}
          ( << {ok: false, error: "Permission denied"} ) """
    is_secretariaat = 'secretariaat' in request.user.cached_groups_names
    if not is_secretariaat:
        return {'ok': False, 'error': 'Permission denied'}
    if not 'id' in data or not isinstance(data['id'], basestring):
        return {'ok': False, 'error': 'Missing argument "id"'}
    if update_type in ('email', 'telephone'):
        if not 'new' in data or not isinstance(data['new'], basestring):
            return {'ok': False, 'error': 'Missing argument "new"'}
    if update_type in ('address'):
        for attr in ('street', 'number', 'zip', 'city'):
            if attr not in data or not isinstance(data[attr], basestring):
                return {'ok': False, 'error': 'Missing argument "%s"' % attr}

    e = Es.by_id(data['id'])
    if e is None:
        return {'ok': False, 'error': 'Entity not found'}

    if (update_type == 'email'):
        """ >> {action:"entity_update_primary_email",id:"4e6fcc85e60edf3dc0000270",
                    new:"giedo@univ.gov"} """
        new_email = data['new']
        if not email_re.match(new_email):
            return {'ok': False, 'error': 'Not valid e-mail address'}
        e.update_primary_email(new_email)
    elif (update_type == 'telephone'):
        """ >> {action:"entity_update_primary_telephone",id:"4e6fcc85e60edf3dc0000270",
                    new:"+31611223344"} """
        new_phone = data['new']
        if not len(new_phone) > 9:
            return {'ok': False, 'error': 'Phone number is too short'}
        e.update_primary_telephone(new_phone)
    elif (update_type == 'address'):
        """ >> {action:"entity_update_address",id:"4e6fcc85e60edf3dc0000270",
                    street:"Street",
                    number:"23",
                    zip:"1234AA",
                    city:"Amsterdam"} """
        e.update_address(data['street'], data['number'], data['zip'], data['city'])
    else:
        return {'ok': False, 'error': 'Unknown update type: "%s"' % update_type}

    giedo.sync()
    return {'ok': True}

def entity_update_primary_email(data, request):
    """ Calls entity.update_primary_email via entity_update """
    return entity_update('primary_email', data, request)

def entity_update_primary_telephone(data, request):
    """ Calls entity.update_primary_telephone via entity_update """
    return entity_update('primary_telephone', data, request)

def entity_update_address(data, request):
    """ Calls entity.update_address via entity_update """
    return entity_update('address', data, request)


ACTION_HANDLER_MAP = {
        'entity_humanName_by_id': entity_humanName_by_id,
        'entities_by_keyword': entities_by_keyword,
        'close_note': close_note,
        'entity_update_primary':  entity_update_primary,
        None: no_such_action,
        }

# vim: et:sta:bs=2:sw=4:
