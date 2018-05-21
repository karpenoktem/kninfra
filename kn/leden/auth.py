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

# vim: et:sta:bs=2:sw=4:
