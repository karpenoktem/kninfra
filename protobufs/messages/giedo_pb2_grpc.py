# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from protobufs.messages import common_pb2 as protobufs_dot_messages_dot_common__pb2
from protobufs.messages import daan_pb2 as protobufs_dot_messages_dot_daan__pb2
from protobufs.messages import giedo_pb2 as protobufs_dot_messages_dot_giedo__pb2


class GiedoStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SyncAsync = channel.unary_unary(
        '/Giedo/SyncAsync',
        request_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
        response_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
        )
    self.SyncBlocking = channel.unary_unary(
        '/Giedo/SyncBlocking',
        request_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
        response_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
        )
    self.LastSynced = channel.unary_unary(
        '/Giedo/LastSynced',
        request_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
        response_deserializer=protobufs_dot_messages_dot_giedo__pb2.LastSyncedResult.FromString,
        )
    self.SetPassword = channel.unary_unary(
        '/Giedo/SetPassword',
        request_serializer=protobufs_dot_messages_dot_giedo__pb2.GiedoSetPassword.SerializeToString,
        response_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
        )
    self.FotoadminCreateEvent = channel.unary_unary(
        '/Giedo/FotoadminCreateEvent',
        request_serializer=protobufs_dot_messages_dot_daan__pb2.FotoadminEvent.SerializeToString,
        response_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
        )
    self.ScanFotos = channel.unary_unary(
        '/Giedo/ScanFotos',
        request_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
        response_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
        )
    self.UpdateSiteAgenda = channel.unary_unary(
        '/Giedo/UpdateSiteAgenda',
        request_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
        response_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
        )


class GiedoServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def SyncAsync(self, request, context):
    """SyncAsync starts a synchronization action in the background.
    All external services will be updated with the information in the web
    application database, by adding/removing users, adding/removing group
    memberships, etc.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SyncBlocking(self, request, context):
    """SyncBlocking is the blocking version of SyncAsync.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def LastSynced(self, request, context):
    """LastSynced returns the time when the last synchronization was completed.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SetPassword(self, request, context):
    """SetPassword updates the password of this user throughout the system.
    It either succeeds or returns an error with code INVALID_ARGUMENT if the
    user is not found or the old password doesn't match.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def FotoadminCreateEvent(self, request, context):
    """Create a new event in the photo album.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ScanFotos(self, request, context):
    """ScanFotos runs a (blocking) scan to index all photos in the photo book.
    New photos are added and old photos are marked lost.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def UpdateSiteAgenda(self, request, context):
    """UpdateSiteAgenda fetches the current agenda from Google Calendar and
    updates the cached agenda on the website with it.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_GiedoServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SyncAsync': grpc.unary_unary_rpc_method_handler(
          servicer.SyncAsync,
          request_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
          response_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
      ),
      'SyncBlocking': grpc.unary_unary_rpc_method_handler(
          servicer.SyncBlocking,
          request_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
          response_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
      ),
      'LastSynced': grpc.unary_unary_rpc_method_handler(
          servicer.LastSynced,
          request_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
          response_serializer=protobufs_dot_messages_dot_giedo__pb2.LastSyncedResult.SerializeToString,
      ),
      'SetPassword': grpc.unary_unary_rpc_method_handler(
          servicer.SetPassword,
          request_deserializer=protobufs_dot_messages_dot_giedo__pb2.GiedoSetPassword.FromString,
          response_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
      ),
      'FotoadminCreateEvent': grpc.unary_unary_rpc_method_handler(
          servicer.FotoadminCreateEvent,
          request_deserializer=protobufs_dot_messages_dot_daan__pb2.FotoadminEvent.FromString,
          response_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
      ),
      'ScanFotos': grpc.unary_unary_rpc_method_handler(
          servicer.ScanFotos,
          request_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
          response_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
      ),
      'UpdateSiteAgenda': grpc.unary_unary_rpc_method_handler(
          servicer.UpdateSiteAgenda,
          request_deserializer=protobufs_dot_messages_dot_common__pb2.Empty.FromString,
          response_serializer=protobufs_dot_messages_dot_common__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Giedo', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
