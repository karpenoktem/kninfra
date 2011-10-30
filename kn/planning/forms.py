# vim: et:sta:bs=2:sw=4:
from django import forms

import kn.leden.entities as Es
from kn.planning.entities import Pool, Worker

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

class EventCreateForm(forms.Form):
    name = forms.CharField(label="Naam", initial="Borrel")
    date = forms.DateField(label="Datum", initial=datetime.date.today())
    template = forms.ChoiceField(label="Template", choices=(
        ('', 'Geen'),
        ('borrel', 'Borrel'),
        ('kleinfeest', 'Klein feest'),
        ('grootfeest', 'Groot feest'),
        ('dranktelling', 'Dranktelling'),
        ('dranklevering', 'Dranklevering'),
        ))

class AddVacancyForm(forms.Form):
    name = forms.CharField(label="Shiftnaam", initial="eerste dienst")
    begin = forms.RegexField(label="Begintijd", initial="20:30",
            regex=r'^[0123][0-9]:[0-5][0-9]$')
    end = forms.RegexField(label="Eindtijd", initial="23:00",
            regex=r'^[0123][0-9]:[0-5][0-9]$')
    pool = forms.ChoiceField(label="Type",
            choices=map(lambda x: (x._id, x.name), Pool.all()))
