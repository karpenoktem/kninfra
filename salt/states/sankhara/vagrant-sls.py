#!/usr/bin/python

import random
import string
from copy import copy

'''
Creates initial data for the grain vagrant.sls
'''

STATIC = {
    'ip-phassa':   '10.107.110.2',
    'ip-sankhara': '10.107.110.3',
    'ldap-suffix': 'dc=vagrant-sankhara,dc=lan',
}
SECRETS = ['chucknorris', 'django_secret_key', 'apikey', 'mysql_giedo',
           'mysql_wiki', 'mysql_wolk', 'mysql_forum', 'mysql_root',
           'mysql_daan', 'mailman_default', 'ldap_infra', 'ldap_daan',
           'ldap_freeradius', 'ldap_admin', 'ldap_saslauthd', 'wiki_key',
           'wiki_upgrade_key', 'wiki_admin', 'irc_services_secret',
           'irc_die_pass', 'irc_restart_pass']

def createVagrantGrains():
    data = copy(STATIC)
    data['secrets'] = {}
    for name in SECRETS:
        passwd = ''
        for i in range(16):
            passwd += random.choice(string.letters+string.digits)
        data['secrets'][name] = passwd
    return data



if __name__ == '__main__':
    data = createVagrantGrains()
    import yaml
    print yaml.dump(data, default_flow_style=False)
