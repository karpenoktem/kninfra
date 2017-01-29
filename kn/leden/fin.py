from decimal import Decimal
from django.conf import settings
from time import strftime, gmtime


def quaestor():
    return {
        "email": "%s@%s" % (settings.QUAESTOR_USERNAME, settings.MAILDOMAIN),
        "name": "de penningmeester"
    }


class MutInfo:

    def __init__(self, data):
        self.data = data

    @property
    def trdescription(self):
        return self.data['tr-description']


class BalansInfo:

    def __init__(self, data):
        self.data = data
        self.total = Decimal(data['total'])
        self.mutations = [MutInfo(mut) for mut in data['mutations']]

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
        return "debitor" in self.data['accounts'] \
            or "creditor" in self.data['accounts']

    @property
    def mtime(self):
        return strftime("%Y-%m-%d", gmtime(self.data['mtime']))
