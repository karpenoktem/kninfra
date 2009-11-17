import _import
import sys
from kn.leden.models import OldKnUser, OldKnGroup

def main():
	members = set()
	N = 0
	while True:
		N += 1
		try:
			g = OldKnGroup.objects.get(name='leden%s' % N)
		except OldKnGroup.DoesNotExist:
			break
		members.update([m.username for m in g.user_set.all()])
	N = 0
	for m in OldKnUser.objects.order_by('dateJoined'):
		if not m.username in members:
			continue
		N += 1
		print '%-4s%-30s%s' % (N, m.get_full_name(), m.dateJoined)

if __name__ == '__main__':
	if sys.stdout.encoding is None:
		reload(sys)
		sys.setdefaultencoding('utf-8')
	main()
