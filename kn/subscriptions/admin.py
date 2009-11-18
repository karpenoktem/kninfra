from django.contrib import admin
from kn.subscriptions.models import Event, EventSubscription

admin.site.register(Event)
admin.site.register(EventSubscription)
