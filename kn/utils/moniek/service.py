import logging
import os.path

import grpc
import msgpack
import protobufs.messages.moniek_pb2 as moniek_pb2
import protobufs.messages.moniek_pb2_grpc as moniek_pb2_grpc
import yaml
from google.protobuf.timestamp_pb2 import Timestamp
from koert.gnucash import tools as koerttools

from django.conf import settings

from kn.utils.moniek import fin


class Moniek(moniek_pb2_grpc.MoniekServicer):

    def __init__(self):
        super(Moniek, self).__init__()

        with open(settings.FIN_YAML_PATH) as f:
            self.settings = yaml.load(f)

        self._gcf_by_year = {}

        # populate cache
        for year in self.settings['years']:
            self.gcf_by_year(year)

    def FinGetAccount(self, request, context):
        account = fin.get_account(
            self, request.name, request.fullName, request.accountType)
        ret = moniek_pb2.FinGetAccountResp(
            total=account['total'],
            mtime=account['mtime'])
        for accountName in account['accounts']:
            ret.accounts[accountName] = True  # this is a set, not a map
        for transaction in account['trs']:
            mutations = []
            for mutation in transaction['muts']:
                mutations.append(moniek_pb2.FinMutation(**mutation))
            timestamp = Timestamp()
            timestamp.FromSeconds(int(transaction['date']['timestamp']))
            ret.transactions.append(moniek_pb2.FinTransaction(
                date=timestamp,
                description=transaction['description'],
                mutations=mutations,
                num=transaction['num'],
                sum=transaction['sum'],
                value=transaction['value'],
            ))
        return ret

    def FinGetDebitors(self, request, context):
        ret = moniek_pb2.FinDebitors()
        for debitor in fin.get_debitors(self):
            ret.debitors.append(moniek_pb2.FinDebitor(name=debitor[0],
                                                      debt=debitor[1]))
        return ret

    def FinCheckNames(self, request, context):
        return fin.check_names(self, {'user': request.user,
                                      'group': request.group})

    def FinGetGnuCashObject(self, request, context):
        data = fin.get_gnucash_object(self, request.year, request.handle)
        if data is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return moniek_pb2.FinObject()
        packed = msgpack.packb(data, use_bin_type=True)
        return moniek_pb2.FinObject(msgpack=packed)

    def FinGetYears(self, request, context):
        ret = moniek_pb2.FinYears()
        for year, path in fin.get_years(self).items():
            ret.years[year] = path
        return ret

    def FinGetErrors(self, request, context):
        data = fin.get_errors(self, request.year)
        if data is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return moniek_pb2.FinErrors()
        ret = moniek_pb2.FinErrors()
        for error in data:
            check = moniek_pb2.FinCheck(
                type=error['check']['type'],
                name=error['check']['name'],
                description=error['check']['description'],
            )
            ret.errors.append(moniek_pb2.FinError(
                check=check,
                objects=error['objects']))
        return ret

    @property
    def gcf(self):
        return self.gcf_by_year(self.settings['current year'])

    @property
    def years(self):
        return self.settings['years']

    def gcf_by_year(self, year):
        if year not in self.settings['years']:
            return None
        onlyafter = None
        if year in self._gcf_by_year:
            cached_gcf = self._gcf_by_year[year]
            onlyafter = max(cached_gcf.mtime, cached_gcf.yamltime)
        relpath = self.settings['years'][year]
        path = os.path.join(os.path.dirname(settings.FIN_YAML_PATH), relpath)
        updated_gcf = koerttools.open_yaml(path, onlyafter=onlyafter)
        if updated_gcf is not None:
            self._gcf_by_year[year] = updated_gcf
            logging.info('loaded new version of fin%s' % (year,))
        return self._gcf_by_year[year]

# vim: et:sta:bs=2:sw=4:
