# vim: et:sta:bs=2:sw=4:
import _import

import datetime

import Mailman.MailList
from django.conf import settings

from kn.leden.models import OldKnGroup

from kn.moderation.models import ModerationRecord
from kn.moderation.views import _deactivate_mm


def main():
	moderators = OldKnGroup.objects.get(name=settings.MODERATORS_GROUP)
	for r in ModerationRecord.objects.all():
		if r.at + settings.MOD_RENEW_INTERVAL < datetime.datetime.now():
			ml = Mailman.MailList.MailList(r.list, True)
			try:
				_deactivate_mm(ml, r.list, None, r, moderators)
			finally:
				ml.Unlock()

if __name__ == '__main__':
	main()