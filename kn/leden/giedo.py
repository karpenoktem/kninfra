import time

from django.conf import settings

from kn.utils.whim import WhimClient

import kn.leden.entities as Es

__GIEDO = None


def get_giedo_connection():
    global __GIEDO
    if __GIEDO is None:
        __GIEDO = WhimClient(settings.GIEDO_SOCKET)
    return __GIEDO


class ChangePasswordError(Exception):
    pass


def change_password(user, old, new):
    giedo = get_giedo_connection()
    ret = giedo.send({'type': 'setpass',
                      'user': user,
                      'oldpass': old,
                      'newpass': new})
    if 'error' in ret:
        raise ChangePasswordError(ret['error'])


def sync():
    get_giedo_connection().send({'type': 'sync'})


def sync_async(request):
    """ Lets giedo sync, but do not wait for it to complete.  Instead, set
        a session variable in the Django HTTPRequest object `request`
        such that the status of the sync is shown on every pageview until
        it completes. """
    now = time.time()
    get_giedo_connection().send_noret({'type': 'sync'})
    request.session['waitingOnGiedoSync'] = now


def get_last_synced():
    """ Get the datetime when giedo finished the last sync. """
    return get_giedo_connection().send({'type': 'last-synced?'})


class SyncStatusMiddleware(object):
    """ Removes `waitingOnGiedoSync` when giedo's sync is done. """

    def process_request(self, request):
        if 'waitingOnGiedoSync' not in request.session:
            return
        if get_last_synced() > request.session['waitingOnGiedoSync']:
            del request.session['waitingOnGiedoSync']


def update_site_agenda():
    get_giedo_connection().send({'type': 'update-site-agenda'})


def fotoadmin_scan_userdirs():
    return get_giedo_connection().send({'type': 'fotoadmin-scan-userdirs'})


def fotoadmin_create_event(date, name, humanName):
    return get_giedo_connection().send({'type': 'fotoadmin-create-event',
                                        'date': date,
                                        'name': name,
                                        'humanname': humanName})


def fotoadmin_move_fotos(event, store, user, dir):
    return get_giedo_connection().send({'type': 'fotoadmin-move-fotos',
                                        'event': event,
                                        'store': store,
                                        'user': user,
                                        'dir': dir})


def openvpn_create(user, want):
    """ Requests giedo to create an OpenVPN installer.
        @user   the user for whom to create the installer
        @want   either 'zip' or 'exe' """
    get_giedo_connection().send({'type': 'openvpn_create',
                                 'user': user,
                                 'want': want})


def fin_get_account(ent):
    return get_giedo_connection().send({
        'type': 'fin-get-account',
        'name': str(ent.name),
        'full_name': str(ent.humanName),
        'account_type': "user" if ent.is_user else "group"
    })


def fin_get_debitors():
    return get_giedo_connection().send({
        'type': 'fin-get-debitors'
    })


def fin_check_names():
    users = Es.by_name('leden').as_group().get_members()
    comms = Es.by_name('comms').as_tag().get_bearers()

    return get_giedo_connection().send({
        'type': 'fin-check-names',
        'names': {
            'user': [str(user.humanName) for user in users],
            'group': [str(com.humanName) for com in comms]
        }


def maillist_get_moderated_lists():
    return get_giedo_connection().send({
        'type': 'maillist-get-moderated-lists'
    })


def maillist_activate_moderation(name):
    return get_giedo_connection().send({
        'type': 'maillist-activate-moderation',
        'name': name
    })


def maillist_deactivate_moderation(name):
    return get_giedo_connection().send({
        'type': 'maillist-deactivate-moderation',
        'name': name
    })

# vim: et:sta:bs=2:sw=4:
