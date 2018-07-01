import kn.leden.entities as Es


class MongoBackend(object):

    def authenticate(self, username=None, password=None):
        user = Es.by_name(username)
        if user is None or not user.is_user \
                or not user.check_password(password):
            return None
        return user

    def get_user(self, pk):
        # Due to a regression, Django expects an integer as identifier ---
        # so we passed the integer representation of our hexstring _id
        # to it.  Here we convert it back.  See also User._Meta.PK.
        return Es.by_id('{0:x}'.format(pk))

# vim: et:sta:bs=2:sw=4:
