from decimal import Decimal
from time import gmtime, strftime

from django.conf import settings

import kn.leden.entities as Es


def quaestor():
    return {
        "email": "%s@%s" % (settings.QUAESTOR_USERNAME, settings.MAILDOMAIN),
        "name": "de penningmeester"
    }


def get_account_entities_of(user):
    """returns the entities whose accounts the user may inspect:
    for the moment the user itself and all the committees it belongs to"""
    comms_id = Es.id_by_name("comms")
    result = [user]
    for group in user.cached_groups:
        if group.has_tag(comms_id):
            result.append(group)
    return result


class TrInfo:

    def __init__(self, data):
        self.data = data
        self.mutations = [MutInfo(mut) for mut in data['muts']]
        self.value = Decimal(data['value'])
        self.sum = Decimal(data['sum'])


class MutInfo:

    def __init__(self, data):
        self.data = data
        self.value = Decimal(data['value'])
        self.sum = Decimal(data['sum'])


class BalansInfo:

    def __init__(self, data):
        self.data = data
        self.total = Decimal(data['total'])
        self.transactions = [TrInfo(tr) for tr in data['trs']]

    @property
    def abstotal(self):
        return abs(self.total)

    @property
    def our_account_number(self):
        return settings.BANK_ACCOUNT_NUMBER

    @property
    def our_account_holder(self):
        return settings.BANK_ACCOUNT_HOLDER

    @property
    def in_books(self):
        return len(self.data['accounts']) > 0

    @property
    def mtime(self):
        return strftime("%Y-%m-%d", gmtime(self.data['mtime']))
