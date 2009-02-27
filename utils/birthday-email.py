from __future__ import with_statement

import _import
import datetime

from kn.leden.models import KnUser
from django.core.mail import EmailMessage

def birthday_email():
	with open('birthday-email.template') as f:
		templ = f.read()
	now = datetime.datetime.now().date()
	for user in KnUser.objects.all():
		if user.dateOfBirth is None:
			continue
		if (user.dateOfBirth.day != now.day or
		    user.dateOfBirth.month != now.month):
			continue
		email = EmailMessage("Hartelijk gefeliciteerd!",
				     templ % {'firstName': user.first_name},
				     'webcie@karpenoktem.nl',
				     [user.email],
				     ['webcie@karpenoktem.nl'])
		email.send()

if __name__ == '__main__':
	birthday_email()
