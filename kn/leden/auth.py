import kn.leden.entities as Es

class MongoBackend(object):
	def authenticate(self, username=None, password=None):
		return Es.by_name(username).check_password(password)

	def get_user(self, pk):
		return Es.by_id(pk)

