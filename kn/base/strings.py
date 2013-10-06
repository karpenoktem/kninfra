
import json
import os

def humanize_list(l, module):
    path = os.path.dirname(os.path.dirname(__file__)) + '/' + module + '/strings.json'
    messages = json.load(open(path))
    return map(lambda s: messages.get(s, s), l)
