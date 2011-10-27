from django import forms

import kn.leden.entities as Es
from kn.planning.entities import Worker

import datetime

class WorkerChoiceField(forms.ChoiceField):
	def __init__(self, *args, **kwargs):
                # TODO Reduce these queries into one.
		kwargs['choices'] = [(e._id, unicode(e.get_user().humanName))
                                        for e in kwargs['choices']]
		if kwargs.get('sort_choices', False):
			kwargs['choices'].sort(key=lambda x: x[1])
			del kwargs['sort_choices']
		kwargs['choices'].insert(0, ('', 'Selecteer'))
		super(WorkerChoiceField, self).__init__(*args, **kwargs)

class ManagePlanningForm(forms.Form):
	def __init__(self, *args, **kwargs):
		vacancies = kwargs['vacancies']
		del kwargs['vacancies']
		pool = kwargs['pool']
		del kwargs['pool']
		super(ManagePlanningForm, self).__init__(*args, **kwargs)
		for vacancy in vacancies:
			field = WorkerChoiceField(label='%s - %s' % (
                                        vacancy.begin_time, vacancy.end_time),
                                        choices=Worker.all_in_pool(pool),
                                        sort_choices=True,
                                        initial=vacancy.assignee_id,
                                        required=False)
			self.fields['shift_%s' % vacancy._id] = field
		for vacancy in vacancies:
			vacancy.set_form_field(self['shift_%s' % vacancy._id])
