import _import

from datetime import datetime
import json
import sys

import kn.leden.entities as Es
from kn.settings import DT_MIN, DT_MAX

def main(f):
	data = json.load(f)
	Es.ecol.drop()
	Es.rcol.drop()
	Es.mcol.drop()
	Es.ensure_indices()
	conv_inst = dict()
	conv_study = dict()
	conv_group = dict()
	conv_user = dict()
	for m in data['EduInstitute']:
		n = {	'types': ['institute'],
			'names': [],
			'tags': [],
			'humanNames': [{'human': m['name']}],
			'names': []}
		conv_inst[m['id']] = Es.ecol.insert(n)
	for m in data['Study']:
		n = {	'types': ['study'],
			'names': [],
			'tags': [],
			'humanNames': [{'human': m['name']}]}
		conv_study[m['id']] = Es.ecol.insert(n)
	for m in data['OldKnGroup']:
		n = {	'types': ['tag' if m['isVirtual'] else 'group'],
			'names': [m['name']],
			'tags': [],
			'humanNames': [{
				'name': m['name'],
				'human': m['humanName'],
				'genitive_prefix': m['genitive_prefix']
				}],
			'description': m['description'],
		   	'temp':{
				'is_virtual': m['isVirtual']
			}
			}
		conv_group[m['id']] = {'id': Es.ecol.insert(n),
				       'name': m['name']}
	for m in data['OldKnGroup']:
		if m['parent'] is not None:
			Es.ecol.update({'_id': conv_group[m['id']]['id']},
				{'$push': {'tags': conv_group[
							m['parent']]['id']}})
	for m in data['OldKnUser']:
		bits = m['password'].split('$')
		if len(bits) == 3:
			pwd = {'algorithm': bits[0],
			       'salt': bits[1],
			       'hash': bits[2]}
		else:
			pwd = None
		n = {
			'types': ['user'],
			'names': [m['username']],
			'tags': [],
			'humanNames': [{'human': m['first_name'] + ' ' +
						 m['last_name']}],
			'person': {
				'titles': [],
				'nick': m['first_name'],
				'given': None,
				'family': m['last_name'],
				'gender': m['gender']
			},
			'emailAddresses': [
				{'email': m['email'],
				 'from': DT_MIN,
				 'until': DT_MAX
				}],
			'addresses': [
				{'street': m['addr_street'],
				 'number': m['addr_number'],
				 'zip': m['addr_zipCode'],
				 'city': m['addr_city'],
				 'from': DT_MIN,
				 'until': DT_MAX
				}],
			'telephones': [
				{'number': m['telephone'],
				 'from': DT_MIN,
				 'until': DT_MAX}],
			'studies': [
				{'institute': conv_inst.get(m['institute']),
				 'study': conv_study.get(m['study']),
				 'from': DT_MIN,
				 'until': DT_MAX,
				 'number': m['studentNumber']}
			],
			'temp': {
				'oud': m['in_oud'],
				'aan': m['in_aan'],
				'incasso': m['got_incasso'],
				'joined': m['dateJoined'],
				'remarks': m['remarks']
			},
			'is_active': m['is_active'],
			'password': pwd
			}
		conv_user[m['id']] = Es.ecol.insert(n)
		for g in m['groups']:
			Es.rcol.insert({
				'with': conv_group[g]['id'],
				'who': conv_user[m['id']],
				'from': DT_MIN,
				'until': DT_MAX,
				'how': None})
	for m in data['OldSeat']:
		n = {'types': ['seat'],
		     'names': [conv_group[m['group']]['name'] + 
				'-' + m['name']],
		     'description': [m['description']],
		     'tags': [],
		     'humanNames': [{
			     	'name': conv_group[m['group']]['name'] +
			     		'-' + m['name'],
				'human': m['humanName']}]}
		i = Es.ecol.insert(n)
		Es.rcol.insert({'who': conv_user[m['user']],
				'from': DT_MIN,
				'until': DT_MAX,
				'how': i,
				'with': conv_group[m['group']]['id']})
	
if __name__ == '__main__':
	if len(sys.argv) == 1:
		sys.argv.append('old.json')
	with open(sys.argv[1]) as f:
		main(f)	
