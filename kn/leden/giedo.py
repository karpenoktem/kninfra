from kn import settings

from kn.utils.whim import WhimDaemon, WhimClient

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
