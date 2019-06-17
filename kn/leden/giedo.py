import time

import grpc
import msgpack
import protobufs.messages.common_pb2 as common_pb2
import protobufs.messages.daan_pb2 as daan_pb2
import protobufs.messages.giedo_pb2 as giedo_pb2
import protobufs.messages.giedo_pb2_grpc as giedo_pb2_grpc
import protobufs.messages.moniek_pb2 as moniek_pb2
import six

from django.conf import settings

import kn.leden.entities as Es

giedo = giedo_pb2_grpc.GiedoStub(
    grpc.insecure_channel('unix:' + settings.GIEDO_SOCKET))


class ChangePasswordError(Exception):
    pass


def change_password(user, old, new):
    try:
        giedo.SetPassword(giedo_pb2.GiedoSetPassword(
            user=user,
            oldpass=old,
            newpass=new))
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise ChangePasswordError(e.details())
        raise e  # re-raise unknown exception


def sync():
    giedo.SyncBlocking(common_pb2.Empty())


def sync_async(request):
    """ Lets giedo sync, but do not wait for it to complete.  Instead, set
        a session variable in the Django HTTPRequest object `request`
        such that the status of the sync is shown on every pageview until
        it completes. """
    now = time.time()
    giedo.SyncAsync(common_pb2.Empty())
    request.session['waitingOnGiedoSync'] = now


def get_last_synced():
    """ Get the datetime when giedo finished the last sync. """
    return giedo.LastSynced(common_pb2.Empty()).time


class SyncStatusMiddleware(object):

    """ Removes `waitingOnGiedoSync` when giedo's sync is done. """

    def process_request(self, request):
        if 'waitingOnGiedoSync' not in request.session:
            return
        if get_last_synced() > request.session['waitingOnGiedoSync']:
            del request.session['waitingOnGiedoSync']


def update_site_agenda():
    giedo.UpdateSiteAgenda(common_pb2.Empty())


def fotoadmin_scan_userdirs():
    userdirs = []
    for userdir in giedo.FotoadminScanUserdirs(common_pb2.Empty()).userdirs:
        userdirs.append((userdir.path, userdir.displayName))
    return userdirs


def fotoadmin_create_event(date, name, humanName):
    try:
        giedo.FotoadminCreateEvent(daan_pb2.FotoadminEvent(
            date=date,
            name=name,
            humanName=humanName))
    except grpc.RpcError as e:
        return {'error': e.details()}
    return {'success': True}


def fotoadmin_move_fotos(event, store, user, dir):
    giedo.FotoadminMoveFotos(daan_pb2.FotoadminMoveAction(
        event=event,
        store=store,
        user=user,
        dir=dir))


def fin_get_account(ent):
    return giedo.FinGetAccount(moniek_pb2.FinGetAccountReq(
        name=six.text_type(ent.name),
        fullName=six.text_type(ent.humanName),
        accountType="user" if ent.is_user else "group"))


def fin_get_debitors():
    return giedo.FinGetDebitors(common_pb2.Empty()).debitors


def fin_check_names():
    users = Es.by_name('leden').as_group().get_members()
    comms = Es.by_name('comms').as_tag().get_bearers()
    req = moniek_pb2.FinNamesList()
    req.user.extend([six.text_type(user.humanName) for user in users])
    req.group.extend([six.text_type(com.humanName) for com in comms])
    return giedo.FinCheckNames(req)


def fin_get_gnucash_object(year, handle):
    obj = giedo.FinGetGnuCashObject(moniek_pb2.FinObjectRequest(
        year=year,
        handle=handle))
    return msgpack.unpackb(obj.msgpack, encoding='utf-8')


def fin_get_errors(year):
    return giedo.FinGetErrors(moniek_pb2.FinYear(year=year)).errors


def fin_get_years():
    return giedo.FinGetYears(common_pb2.Empty()).years

# vim: et:sta:bs=2:sw=4:
