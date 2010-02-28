from kn.reglementen.models import Reglement, Version
from django.contrib import admin

for m in (Reglement, Version):
	admin.site.register(m)
