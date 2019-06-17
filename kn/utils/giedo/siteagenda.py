import logging

from kn.agenda.entities import update
from kn.agenda.fetch import fetch


def update_site_agenda():
    agendas = fetch()
    if agendas is None:
        logging.warning('agenda: could not fetch agenda')
        return {'error': 'Failed to fetch agendas'}
    update(agendas)
    return {'success': True}

# vim: et:sta:bs=2:sw=4:
