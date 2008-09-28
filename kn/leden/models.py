from django.db import models
from django.contrib.auth.models import User, Group

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

class Member(User):
	dateOfBirth = models.DateField(null=True, blank=True)
	dateJoined = models.DateField(null=True, blank=True)
	
	addr_street = models.CharField(max_length=100)
	addr_number = models.CharField(max_length=20)
	addr_zipCode = models.CharField(max_length=10)
	addr_city = models.CharField(max_length=80)
	
	gender = models.CharField(max_length=1, blank=True)
	telephone = models.CharField(max_length=20, null=True)
	studentNumber = models.CharField(max_length=20, unique=True, null=True, blank=True)
	institute = models.ForeignKey('EduInstitute', null=True)
	study = models.ForeignKey('Study', null=True)

class Commission(Group):
	humanName = models.CharField(max_length=120)
	decription = models.TextField()

class Seat(models.Model):
	name = models.CharField(max_length=80)
	humanName = models.CharField(max_length=120)
	description = models.TextField()
	commission = models.ForeignKey('Commission')
	member = models.ForeignKey('Member')
	isGlobal = models.BooleanField()

	def __unicode__(self):
		return unicode(self.humanName) + " (" + unicode(self.commission) + ")"

class Alias(models.Model):
	source = models.CharField(max_length=80)
	target = models.CharField(max_length=80)

	def __unicode__(self):
		return unicode(self.source + " -> " + self.target)
