# vim: et:sta:bs=2:sw=4:
from django.db import models

class Reglement(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    humanName = models.CharField(max_length=120)
    description = models.TextField()

    def __unicode__(self):
        return self.humanName

    @models.permalink
    def get_absolute_url(self):
        return ('reglement-detail', (), {'name': self.name})

class Version(models.Model):
    reglement = models.ForeignKey(Reglement)
    name = models.CharField(max_length=30, primary_key=True)
    humanName = models.CharField(max_length=120, null=True)
    description = models.TextField()
    validFrom = models.DateField(null=True)
    validUntil = models.DateField(null=True)
    regl = models.TextField()
    cached_html = models.TextField(null=True)

    def __unicode__(self):
        return self.humanName

    @models.permalink
    def get_absolute_url(self):
        return ('version-detail', (), {
                'reglement_name': self.reglement.name,
                'version_name': self.name})