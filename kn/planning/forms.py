from django import forms
import kn.leden.entities as Es
import datetime

# XXX indien niet gewijzigd importeren uit kn.leden.forms
class EntityChoiceField(forms.ChoiceField):
	def __init__(self, *args, **kwargs):
		kwargs['choices'] = [(e._id, unicode(e.humanName)) for e in kwargs['choices']]
		if kwargs.get('sort_choices', False):
			kwargs['choices'].sort(cmp=lambda x,y: cmp(x[1],y[1]))
			del kwargs['sort_choices']
		super(EntityChoiceField, self).__init__(*args, **kwargs)

class ManagePlanningForm(forms.Form):
	def __init__(self, *args, **kwargs):
		vacancies = kwargs['vacancies']
		del kwargs['vacancies']
		super(ManagePlanningForm, self).__init__(*args, **kwargs)
		for vacancy in vacancies:
			field = EntityChoiceField(label='%s - %s' % (vacancy.begin_time, vacancy.end_time), choices=Es.users(), sort_choices=True, initial=vacancy.assignee_id)
			self.fields['shift_%s' % vacancy._id] = field
		print self.base_fields
		print self.is_bound
		for vacancy in vacancies:
			vacancy.set_form_field(self.__getitem__('shift_%s' % vacancy._id))
