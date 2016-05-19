
import kn.planning.entities as pEs

def may_manage_planning(request):
    return {'may_manage_planning': pEs.may_manage_planning(request.user)}

# vim: et:sta:bs=2:sw=4:
