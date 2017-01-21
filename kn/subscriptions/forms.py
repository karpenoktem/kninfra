from django import forms
from django.utils.translation import ugettext as _

from kn.leden.forms import EntityChoiceField
from kn.leden.mongo import _id
import kn.subscriptions.entities as subscr_Es


def get_allowed_owners(user):
    '''
    Get the entities (often groups) that this owner is allowed to use.
    Does not check for superuser capabilities (which may select any entity).
    '''

    entities = [user] + [g for g in user.cached_groups
                         if subscr_Es.may_set_owner(user, g)]
    return entities


def validate_event_name(name):
    if subscr_Es.event_by_name(name):
        raise forms.ValidationError(_('Naam voor computers bestaat al'))


def get_add_event_form(user, superuser=False, editing=False):
    class AddEventForm(forms.Form):
        humanName = forms.CharField(
            label='Naam',
            widget=forms.TextInput(attrs={'required': ''})
        )
        if not editing:
            name = forms.RegexField(label=_('Naam voor computers'),
                                    regex=r'^[a-z0-9-]+$',
                                    widget=forms.TextInput(attrs={
                                        'required': '',
                                        'pattern':  '[a-z0-9-]+'}),
                    validators=[validate_event_name])
        description = forms.CharField(
            label=_('Beschrijving'),
            widget=forms.Textarea(attrs={'required': ''})
        )
        cost = forms.DecimalField(label=_('Kosten'),
                                  initial='0',
                                  widget=forms.NumberInput(attrs={
                                      'required': '',
                                      'min':      '0'}))
        date = forms.DateField(label=_('Datum'),
                               widget=forms.DateInput(attrs={
                                   'required':    '',
                                   'placeholder': 'jjjj-mm-dd'}))
        max_subscriptions = forms.IntegerField(
            required=False,
            label=_('Maximum aantal deelnemers (optioneel)'),
            widget=forms.NumberInput(attrs={'placeholder': _('geen maximum')}))
        if superuser:
            owner = EntityChoiceField(label=_("Eigenaar"))
        else:
            owner = forms.ChoiceField(
                label=_('Eigenaar'),
                choices=[(_id(e), unicode(e.humanName))
                         for e in get_allowed_owners(user)]
            )
        has_public_subscriptions = forms.BooleanField(
            required=False,
            label=_('Inschrijvingen openbaar')
        )
        may_unsubscribe = forms.BooleanField(
            required=False,
            initial=False,
            label=_('Leden mogen zichzelf afmelden')
        )
    return AddEventForm

# vim: et:sta:bs=2:sw=4:
