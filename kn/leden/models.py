from django.db import models
from django.contrib.auth.models import User, Group

from kn.leden.settings import MAILDOMAIN

class Entity(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=30, unique=True)

	children = models.ManyToManyField('Entity', blank=True)


	def __unicode__(self):
		return self.name

class Seat(Entity):
	humanName = models.CharField(max_length=120)
	description = models.TextField()
	group = models.ForeignKey('KnGroup')
	isGlobal = models.BooleanField()

	@property
	def primary_name(self):
		return (self.name if self.isGlobal else
			self.group.name + '-' + self.name)

	def __unicode__(self):
		return unicode(self.humanName) + " (" + \
				unicode(self.group) + ")"

class KnUser(Entity):
	user = models.OneToOneField(User)

	first_name = models.CharField(max_length=30, blank=True)
	last_name = models.CharField(max_length=30, blank=True)
	
	email = models.EmailField(blank=True)

	dateOfBirth = models.DateField(null=True, blank=True)
	dateJoined = models.DateField(null=True, blank=True)
	
	addr_street = models.CharField(max_length=100, blank=True)
	addr_number = models.CharField(max_length=20, blank=True)
	addr_zipCode = models.CharField(max_length=10, blank=True)
	addr_city = models.CharField(max_length=80, blank=True)
	
	gender = models.CharField(max_length=1, blank=True)
	telephone = models.CharField(max_length=20, null=True)
	studentNumber = models.CharField(max_length=20,
					 unique=True,
					 null=True,
					 blank=True)
	institute = models.ForeignKey('EduInstitute', null=True)
	study = models.ForeignKey('Study', null=True)

	@property
	def primary_name(self):
		return self.username

	@property
	def full_name(self):
		bits = self.last_name.split(',', 1)
		if len(bits) == 1:
			return self.first_name + ' ' + self.last_name
		return self.first_name + bits[1] + ' ' + bits[0]

	humanName = full_name

	@models.permalink
	def get_absolute_url(self):
		return ('knuser-detail', (), {'name': self.username})

class KnGroup(Entity):
	group = models.OneToOneField(Group)

	humanName = models.CharField(max_length=120)
	genitive_prefix = models.CharField(max_length=20,
					   default='van de')
	description = models.TextField()
	isVirtual = models.BooleanField()
	subscribeParentToML = models.BooleanField()
	
	@property
	def primary_name(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('kngroup-detail', (), {'name': self.name})

class NamedMixin(object):
	@property
	def primary_email(self):
		return self.primary_name + '@' + MAILDOMAIN

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

class Certificate(models.Model):
	name = models.CharField(max_length=80)

	def __unicode__(self):
		return self.name

class CertificateOwnership(models.Model):
	certificate = models.ForeignKey('Certificate')
	user = models.ForeignKey('OldKnUser')
	start = models.DateField(null=True, blank=True)
	end = models.DateField(null=True, blank=True)

class OldKnUser(User, NamedMixin):
	dateOfBirth = models.DateField(null=True, blank=True)
	dateJoined = models.DateField(null=True, blank=True)
	
	addr_street = models.CharField(max_length=100, blank=True)
	addr_number = models.CharField(max_length=20, blank=True)
	addr_zipCode = models.CharField(max_length=10, blank=True)
	addr_city = models.CharField(max_length=80, blank=True)
	
	gender = models.CharField(max_length=1, blank=True)
	telephone = models.CharField(max_length=20, null=True)
	studentNumber = models.CharField(max_length=20,
					 unique=True,
					 null=True,
					 blank=True)
	institute = models.ForeignKey('EduInstitute', null=True)
	study = models.ForeignKey('Study', null=True)
	got_incasso = models.BooleanField()

	@property
	def primary_name(self):
		return self.username

	def get_full_name(self):
		bits = self.last_name.split(',', 1)
		if len(bits) == 1:
			return self.first_name + ' ' + self.last_name
		return self.first_name + bits[1] + ' ' + bits[0]

	@models.permalink
	def get_absolute_url(self):
		return ('oldknuser-detail', (), {'name': self.username})

	def __hash__(self):
		return self.pk.__hash__()

	def __eq__(self, other):
		if not isinstance(other, (OldKnUser, User)):
			return False
		return self.pk == other.pk

class OldKnGroup(Group, NamedMixin):
	parent = models.ForeignKey('OldKnGroup')
	humanName = models.CharField(max_length=120)
	genitive_prefix = models.CharField(max_length=20,
					   default='van de')
	description = models.TextField()
	isVirtual = models.BooleanField()
	subscribeParentToML = models.BooleanField()
	
	@property
	def primary_name(self):
		return self.name

	@models.permalink
	def get_absolute_url(self):
		return ('oldkngroup-detail', (), {'name': self.name})

	def __eq__(self, other):
		if not isinstance(other, (OldKnGroup, Group)):
			return False
		return self.pk == other.pk

class OldSeat(models.Model, NamedMixin):
	name = models.CharField(max_length=80)
	humanName = models.CharField(max_length=120)
	description = models.TextField()
	group = models.ForeignKey('OldKnGroup')
	user = models.ForeignKey('OldKnUser')
	isGlobal = models.BooleanField()

	@property
	def primary_name(self):
		return (self.name if self.isGlobal else
			self.group.name + '-' + self.name)

	def __unicode__(self):
		return unicode(self.humanName) + " (" + \
				unicode(self.group) + ")"

class Alias(models.Model):
	source = models.CharField(max_length=80)
	target = models.CharField(max_length=80)

	def __unicode__(self):
		return unicode(self.source + " -> " + self.target)

class Transaction(models.Model):
	user = models.ForeignKey('OldKnUser')
	value = models.DecimalField(max_digits=11, decimal_places=2)
	date = models.DateField()
	type = models.ForeignKey('TransactionType')
	description = models.TextField()
	
	def __unicode__(self):
		return unicode('%s %s %s (%s): %s' % (self.user,
						      self.date,
						      self.value,
						      self.type.name,
						      self.description))

class TransactionType(models.Model):
	name = models.CharField(max_length=80)

	def __unicode__(self):
		return unicode(self.name)
