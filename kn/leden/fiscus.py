import kn.leden.entities as Es

from decimal import Decimal

class Debitors:
    def __init__(self, data):
        self.data = dict([(n,{'debt': Decimal(debt)}) for (n,debt) in data])

        for user in Es.users():
            name = user.full_name
            if name in self.data:
                self.data[name]['user'] = user



