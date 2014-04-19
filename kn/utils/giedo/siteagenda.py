import locale

from kn.agenda.fetch import fetch
from kn.agenda.entities import update

try:
    # Nederlandse afkortingen voor data
    locale.setlocale(locale.LC_ALL, 'nl_NL')
except Exception:
    pass

def update_site_agenda(giedo):
    update(fetch())
    return {'success': True}

update_site_agenda()

# vim: et:sta:bs=2:sw=4:
