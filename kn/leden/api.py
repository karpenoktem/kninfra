import datetime
import json

from django.contrib.auth.decorators import login_required
from django.utils import six
from django.views.decorators.http import require_POST

import kn.leden.entities as Es
from kn.base.http import JsonHttpResponse
from kn.base.mail import render_then_email
from kn.base.validators import email_re
from kn.leden import giedo
from kn.leden.mongo import _id
from kn.leden.utils import find_name_for_user, parse_date


@login_required
@require_POST
def view(request):
    data = json.loads(request.POST.get('data', '{}'))
    action = data.get('action')
    handler = ACTION_HANDLER_MAP.get(action, None)
    if handler is None:
        return JsonHttpResponse({'error': 'No such action'}, status=400)
    return JsonHttpResponse(handler(data, request))


def _humanName_of_entity(e):
    """ Returns the human name of an entity, as used in the API. """
    if e.name:
        return six.text_type("%s (%s)") % (e.humanName, e.name)
    return six.text_type(e.humanName)


def entities_by_keyword(data, request):
    """ Wraps Es.by_keyword.  Finds the first 20 entities matching the given
        keyword.  Example:

          >> {action:"by_keyword", keyword: "giedo"}
          << [["4e6fcc85e60edf3dc0000270", "Giedo Jansen (giedo)"]]

        The return format is optimized for size and compatibility with
        jquery-ui.autocomplete """
    _type = data.get('type', None)
    if _type and not isinstance(_type, six.string_types):
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


def get_last_synced(data, request):
    """ Returns the timestamp when giedo last synced.  Example:

          >> {action:"get_last_synced"}
          << 1362912433.822199 """
    return giedo.get_last_synced()


def delete_note(data, request):
    """ Wraps Note.delete()

          >> {action:"delete_note", id: "5038b134d4080073f410fafd"}
          << {ok: true}
        ( << {ok: false, error: "Note not found"} ) """
    if 'secretariaat' not in request.user.cached_groups_names:
        return {'ok': False, 'error': 'Permission denied'}
    note = Es.note_by_id(_id(data.get('id')))
    if note is None:
        return {'ok': False, 'error': 'Note not found'}
    note.delete()
    render_then_email('leden/note-deleted.mail.html',
                      Es.by_name('secretariaat').canonical_full_email,
                      {'note': note, 'closed_by': request.user},
                      headers={
                              'In-Reply-To': note.messageId,
                              'References': note.messageId,
                      })
    return {'ok': True}


def entity_update_primary(data, request):
    """ Updates an entity
            >> (see below)

            << {ok: true}
          ( << {ok: false, error: "Permission denied"} ) """
    if 'id' not in data or not isinstance(data['id'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "id"'}
    if 'type' not in data or not isinstance(data['type'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "type"'}
    if 'new' not in data:
        return {'ok': False, 'error': 'Missing argument "new"'}
    new = data['new']
    typ = data['type']
    is_secretariaat = 'secretariaat' in request.user.cached_groups_names
    if not is_secretariaat:
        return {'ok': False, 'error': 'Permission denied'}
    if typ in ('email', 'telephone'):
        if not isinstance(new, six.string_types):
            return {'ok': False, 'error': '"new" should be a string'}
    elif typ == 'address':
        if not isinstance(new, dict):
            return {'ok': False, 'error': '"new" should be a dict'}
        for attr in ('street', 'number', 'zip', 'city'):
            if attr not in new or not isinstance(new[attr], six.string_types):
                return {
                    'ok': False,
                    'error': 'Missing argument "new.%s"' % attr}
    else:
        return {'ok': False, 'error': 'Unknown update type: "%s"' % typ}
    e = Es.by_id(data['id'])
    if e is None:
        return {'ok': False, 'error': 'Entity not found'}
    if (typ == 'email'):
        """ >> {action:"entity_update_email",id:"4e6fcc85e60edf3dc0000270",
                    new:"giedo@univ.gov"} """
        if not email_re.match(new):
            return {'ok': False, 'error': 'Not valid e-mail address'}
        e.update_email(new)
    elif (typ == 'telephone'):
        """ >> {action:"entity_update_telephone",id:"4e6fcc85e60edf3dc0000270",
                    new:"+31611223344"} """
        if not len(new) > 9:
            return {'ok': False, 'error': 'Phone number is too short'}
        e.update_telephone(new)
    elif (typ == 'address'):
        """ >> {action:"entity_update_address",id:"4e6fcc85e60edf3dc0000270",
                    street:"Street",
                    number:"23",
                    zip:"1234AA",
                    city:"Amsterdam"} """
        e.update_address(new['street'], new['number'], new['zip'], new['city'])
    else:
        return {'ok': False, 'error': 'Unknown update type: "%s"' % typ}
    giedo.sync_async(request)
    return {'ok': True}


def entity_update_visibility(data, request):
    """ Updates the visibility of a part of an entity (e.g. email,
        phone number...)
            Example:
            >> {action:"entity_update_visibility",
                id:"4e6fcc85e60edf3dc0000270",
                property: "telephone",
                value: False}
            << {ok: true}
        or: << {ok: false, error: "Permission denied"}
    """

    if 'id' not in data or not isinstance(data['id'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "id"'}
    if 'key' not in data or not isinstance(data['key'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "key"'}
    if 'value' not in data or not isinstance(data['value'], bool):
        return {'ok': False, 'error': 'Missing argument "value"'}

    is_secretariaat = 'secretariaat' in request.user.cached_groups_names
    is_user = data['id'] == request.user.id
    if not (is_secretariaat or is_user):
        return {'ok': False, 'error': 'Permission denied'}

    property = data['key']
    value = data['value']

    if property not in ['telephone', 'dateOfBirth']:
        return {'ok': False, 'error': 'Unknown property "%s"' % property}

    e = Es.by_id(data['id'])
    if e is None:
        return {'ok': False, 'error': 'Entity not found'}

    e.update_visibility_preference(property, value)

    return {'ok': True}


def entity_remove_property(data, request):
    """ Removes a property of an entity (e.g. date of birth).
            Example:
            >> {action:"entity_remove_property",
                id:"4e6fcc85e60edf3dc0000270",
                key: "dateOfBirth"}
            << {ok: true}
        or: << {ok: false, error: "Permission denied"}
    """

    if 'id' not in data or not isinstance(data['id'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "id"'}
    if 'key' not in data or not isinstance(data['key'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "key"'}

    is_secretariaat = 'secretariaat' in request.user.cached_groups_names
    is_user = data['id'] == request.user.id
    if not (is_secretariaat or is_user):
        return {'ok': False, 'error': 'Permission denied'}

    e = Es.by_id(data['id'])
    if e is None:
        return {'ok': False, 'error': 'Entity not found'}

    property = data['key']
    if property == 'dateOfBirth':
        e.remove_dateOfBirth()
    elif property == 'address':
        e.remove_address()
    else:
        return {'ok': False, 'error': 'Unknown property "%s"' % property}

    return {'ok': True}


def entity_end_study(data, request):
    '''
    End a study at the specified date.
    '''
    if 'id' not in data or not isinstance(data['id'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "id"'}
    if 'key' not in data or not isinstance(data['key'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "key"'}
    if 'value' not in data or not isinstance(data['value'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "value"'}

    if 'secretariaat' not in request.user.cached_groups_names:
        return {'ok': False, 'error': 'Permission denied'}

    e = Es.by_id(data['id'])
    if e is None:
        return {'ok': False, 'error': 'Entity not found'}
    try:
        end_date = parse_date(data['value'])
    except ValueError:
        return {'ok': False, 'error': 'Invalid date'}
    if not end_date:
        return {'ok': False, 'error': 'No valid end date given'}
    try:
        study = int(data['key'])
    except ValueError:
        return {'ok': False, 'error': 'Invalid study'}
    try:
        e.study_end(study, end_date)
    except Es.EntityException as why:
        return {'ok': False, 'error': why.message}

    return {'ok': True}


def entity_set_property(data, request):
    if 'id' not in data or not isinstance(data['id'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "id"'}
    if 'key' not in data or not isinstance(data['key'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "key"'}
    if 'value' not in data or not isinstance(data['value'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "value"'}

    if 'secretariaat' not in request.user.cached_groups_names:
        return {'ok': False, 'error': 'Permission denied'}

    property = data['key']
    value = data['value']

    e = Es.by_id(data['id'])
    if e is None:
        return {'ok': False, 'error': 'Entity not found'}

    if property == 'description':
        e.set_description(value)
    elif property == 'humanName':
        e.set_humanName(value)
    elif property == 'dateOfBirth':
        try:
            dateOfBirth = parse_date(value)
            if dateOfBirth is None:
                raise ValueError('cannot parse date')
            dateOfBirth = datetime.datetime.combine(
                dateOfBirth, datetime.datetime.min.time())
        except ValueError as e:
            return {'ok': False, 'error': str(e)}
        e.set_dateOfBirth(dateOfBirth)
    else:
        return {'ok': False, 'error': 'Unknown property "%s"' % property}

    return {'ok': True}


def adduser_suggest_username(data, request):
    if 'first_name' not in data or not isinstance(
            data['first_name'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "first_name"'}
    if 'last_name' not in data or not isinstance(
            data['last_name'], six.string_types):
        return {'ok': False, 'error': 'Missing argument "last_name"'}

    if 'secretariaat' not in request.user.cached_groups_names:
        return {'ok': False, 'error': 'Permission denied'}

    return {
        'ok': True,
        'username': find_name_for_user(
            data['first_name'],
            data['last_name'])}


ACTION_HANDLER_MAP = {
    'entity_humanName_by_id': entity_humanName_by_id,
    'entities_by_keyword': entities_by_keyword,
    'delete_note': delete_note,
    'entity_set_property': entity_set_property,
    'entity_update_primary': entity_update_primary,
    'entity_update_visibility': entity_update_visibility,
    'entity_remove_property': entity_remove_property,
    'entity_end_study': entity_end_study,
    'get_last_synced': get_last_synced,
    'adduser_suggest_username': adduser_suggest_username,
}

# vim: et:sta:bs=2:sw=4:
