import base64

from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.views import redirect_to_login

import kn.leden.entities as Es


class MongoBackend(object):
    def authenticate(self, username=None, password=None):
        user = Es.by_name(username)
        if user is None or not user.is_user \
                or not user.check_password(password):
            return None
        return user

    def get_user(self, pk):
        return Es.by_id(pk)


def login_or_basicauth_required(view):
    """ Require Django session or credentials via HTTP basic auth. """
    def _auth_check(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view(request, *args, **kwargs)

        # They are not logged in. See if they provided login credentials
        #
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    uname, passwd = base64.b64decode(auth[1]).split(':')
                    user = authenticate(username=uname, password=passwd)
                    if user and user.is_active:
                        request.user = user
                        return view(request, *args, **kwargs)
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="Karpe Noktem"'
            return response
        return redirect_to_login(request.path)
    return _auth_check

# vim: et:sta:bs=2:sw=4:
