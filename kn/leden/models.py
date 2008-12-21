from django.db import models
from django.contrib.auth.models import User, Group

KN_DOMAIN = 'karpenoktem.nl'

class EduInstitute(models.Model):
	name = models.CharField(max_length=80)
	
	def __unicode__(self):
		return self.name

class Study(models.Model):
	class Meta:
		verbose_name_plural = 'Studies'
	
	name = models.CharField(max_length=80)

	def __unicode__(self):
		return self.name

class KnUser(User):
	dateOfBirth = models.DateField(null=True, blank=True)
	dateJoined = models.DateField(null=True, blank=True)
	
	addr_street = models.CharField(max_length=100)
	addr_number = models.CharField(max_length=20)
	addr_zipCode = models.CharField(max_length=10)
	addr_city = models.CharField(max_length=80)
	
	gender = models.CharField(max_length=1, blank=True)
	telephone = models.CharField(max_length=20, null=True)
	studentNumber = models.CharField(max_length=20,
					 unique=True,
					 null=True,
					 blank=True)
	institute = models.ForeignKey('EduInstitute')
	study = models.ForeignKey('Study')

	def get_full_name(self):
		bits = self.last_name.split(',', 1)
		if len(bits) == 1:
			return self.first_name + ' ' + self.last_name
		return self.first_name + bits[1] + ' ' + bits[0]

	def get_primary_email(self):
		return self.username + '@' + KN_DOMAIN

	@models.permalink
	def get_absolute_url(self):
		return ('knuser-detail', (), {'name': self.username})

class KnGroup(Group):
	parent = models.ForeignKey('KnGroup')
	humanName = models.CharField(max_length=120)
	genitive_prefix = models.CharField(max_length=20,
					   default='van de')
	description = models.TextField()
	isVirtual = models.BooleanField()
	
	def get_primary_email(self):
		return self.name + '@' + KN_DOMAIN

	@models.permalink
	def get_absolute_url(self):
		return ('kngroup-detail', (), {'name': self.name})

class Seat(models.Model):
	name = models.CharField(max_length=80)
	humanName = models.CharField(max_length=120)
	description = models.TextField()
	group = models.ForeignKey('KnGroup')
	user = models.ForeignKey('KnUser')
	isGlobal = models.BooleanField()

	def __unicode__(self):
		return unicode(self.humanName) + " (" + \
				unicode(self.group) + ")"

class Alias(models.Model):
	source = models.CharField(max_length=80)
	target = models.CharField(max_length=80)

	def __unicode__(self):
		return unicode(self.source + " -> " + self.target)
