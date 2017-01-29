import datetime

from django import forms
from django.utils.translation import ugettext as _
from django.utils import six

from kn.planning.entities import Pool


class WorkerChoiceField(forms.ChoiceField):

    def __init__(self, *args, **kwargs):
        # TODO Reduce these queries into one.
        kwargs['choices'] = [(e._id, six.text_type(e.humanName))
                             for e in kwargs['choices']]
        if kwargs.get('sort_choices', False):
            kwargs['choices'].sort(key=lambda x: x[1])
            del kwargs['sort_choices']
        kwargs['choices'].insert(0, ('', _('Selecteer')))
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
                choices=pool.workers(),
                sort_choices=True,
                initial=vacancy.assignee_id,
                required=False)
            self.fields['shift_%s' % vacancy._id] = field
        for vacancy in vacancies:
            vacancy.set_form_field(self['shift_%s' % vacancy._id])


class EventCreateForm(forms.Form):
    name = forms.CharField(label="Naam", initial="Borrel")
    date = forms.DateField(label="Datum", initial=datetime.date.today())
    template = forms.ChoiceField(label="Soort", required=False, choices=(
        ('', _('Geen')),
        ('borrel', _('Borrel')),
        ('kleinfeest', _('Klein feest')),
        ('grootfeest', _('Groot feest')),
        ('dranktelling', _('Dranktelling')),
        ('dranklevering', _('Dranklevering')),
        ('vrijdag_zonder_tappers', _('Vrijdag')),
        ('vrijdag_met_tappers', _('Vrijdag (met tappers)')),
        ('koken', 'Koken'),
    ))


class AddVacancyForm(forms.Form):
    name = forms.CharField(label=_("Shiftnaam"), initial="eerste dienst")
    begin = forms.RegexField(
        label=_("Begintijd"), initial="20:30",
        regex=r'^[0123][0-9]:[0-5][0-9]$'
    )
    begin_is_approximate = forms.ChoiceField(
        initial=False,
        choices=((True, _("bij benadering")), (False, _("exact")))
    )
    end = forms.RegexField(label=_("Eindtijd"), initial="23:00",
                           regex=r'^[0123][0-9]:[0-5][0-9]$')
    end_is_approximate = forms.ChoiceField(
        initial=False,
        choices=((True, _("bij benadering")), (False, _("exact")))
    )
    pool = forms.ChoiceField(
        label=_("Type"),
        choices=[(x._id, x.name) for x in Pool.all()]
    )

# vim: et:sta:bs=2:sw=4:
