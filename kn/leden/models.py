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

class Member(models.Model):
	user = models.OneToOneField(User)
	dateOfBirth = models.DateField(null=True)
	dateJoined = models.DateField(null=True)

	addr_street = models.CharField(max_length=100)
	addr_number = models.CharField(max_length=20)
	addr_zipCode = models.CharField(max_length=10)
	addr_city = models.CharField(max_length=80)
	
	telephone = models.IntegerField(null=True)
	studentNumber = models.IntegerField(unique=True, null=True)
	institute = models.ForeignKey('EduInstitute', null=True)
	study = models.ForeignKey('Study', null=True)
	commissions = models.ManyToManyField('Commission')

	def __unicode__(self):
		return unicode(self.user)

class Commission(models.Model):
	group = models.OneToOneField(Group)
	name = models.CharField(max_length=120)
	decription = models.TextField()
	hoofd = models.ForeignKey('Member')
	
	def __unicode__(self):
		return unicode(self.name)
