from kn.agenda.fetch import fetch
from kn.agenda.entities import update

def update_site_agenda(giedo):
    update(fetch())
    return {'success': True}

# vim: et:sta:bs=2:sw=4:
