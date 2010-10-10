from django.db import models
from django.contrib.auth.models import User

class ModerationRecord(models.Model):
	list = models.CharField(max_length=80, primary_key=True)
	at = models.DateTimeField()
	by = models.ForeignKey(User)
