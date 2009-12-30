from django.db import models
from kn.leden.models import OldKnUser, OldKnGroup

class Event(models.Model):
	name = models.CharField(max_length=32)
	humanName = models.CharField(max_length=120)
	description = models.TextField()
	mailBody = models.TextField()
	owner = models.ForeignKey(OldKnGroup)
	cost = models.DecimalField(max_digits=11, decimal_places=2)

	def __unicode__(self):
		return unicode('%s (%s)' % (self.humanName, self.owner))

	@models.permalink
	def get_absolute_url(self):
		return ('event-detail', (), {'name': self.name})

class EventSubscription(models.Model):
	event = models.ForeignKey('Event')
	user = models.ForeignKey(OldKnUser)
	debit = models.DecimalField(max_digits=11, decimal_places=2)

	class Meta:
		unique_together = (("event", "user"), )
		ordering = ['id']

	def __unicode__(self):
		return unicode(u"%s for %s" % (self.user.username, 
						self.event.humanName))
