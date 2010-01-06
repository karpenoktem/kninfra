from django.contrib import admin
from kn.subscriptions.models import Event, EventSubscription

class EventSubscriptionAdmin(admin.ModelAdmin):
	list_display = ('user', 'event', 'debit')
	list_filter = ('event', 'debit', )
	search_fields = ('user', 'event')
	ordering = ('id', )

admin.site.register(Event)
admin.site.register(EventSubscription, EventSubscriptionAdmin)
