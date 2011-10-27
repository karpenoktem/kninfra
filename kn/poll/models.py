# vim: et:sta:bs=2:sw=4:
from django.db import models
from django.contrib.auth.models import User

class Poll(models.Model):
	name = models.CharField(max_length=80, primary_key=True)
	description = models.TextField()
	isOpen = models.BooleanField()

	def __unicode__(self):
		return unicode(self.name)

class AnswerSet(models.Model):
	description = models.TextField()

	def __unicode__(self):
		return self.description

class Answer(models.Model):
	answerSet = models.ForeignKey('AnswerSet')
	text = models.TextField()

	def __unicode__(self):
		return unicode(self.text)

class Question(models.Model):
	poll = models.ForeignKey('Poll')
	answers = models.ForeignKey('AnswerSet')
	text = models.TextField()

	def __unicode__(self):
		return unicode(self.text)

class Filling(models.Model):
	question = models.ForeignKey('Question')
	answer = models.ForeignKey('Answer')
	user = models.ForeignKey(User)

	def __unicode__(self):
		return unicode("%s: %s for %s" % (
				self.user,
				self.answer,
				self.question))