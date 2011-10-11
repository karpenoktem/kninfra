from django import forms
import kn.leden.entities as Es
import datetime

# XXX indien niet gewijzigd importeren uit kn.leden.forms
class EntityChoiceField(forms.ChoiceField):
        def __init__(self, *args, **kwargs):
                kwargs['choices'] = [(e._id, unicode(e.humanName))
                                        for e in  kwargs['choices']]
                if kwargs.get('sort_choices', False):
                        kwargs['choices'].sort(cmp=lambda x,y: cmp(x[1],y[1]))
                        del kwargs['sort_choices']
                super(EntityChoiceField, self).__init__(*args, **kwargs)

class ManagePlanningForm(forms.Form):
	pass
