# vim: et:sta:bs=2:sw=4:
# Generates a graphviz dot file
#  for the sheir fun of it

import _import  # noqa: F401
import MySQLdb
from common import read_ssv_file
from pydot import Node, Dot, Edge
from Mailman import MailList, Utils

MAILDOMAIN = "karpenoktem.nl"
LISTDOMAIN = "lists.karpenoktem.nl"


def gen_dot():
    d = Dot()
    nodes = dict()
    login = read_ssv_file('vpopmail.login')
    db = MySQLdb.connect(host='localhost', user=login[0],
        passwd=login[2], db=login[1])
    c = db.cursor()
    c.execute("SELECT alias, valias_line FROM valias WHERE domain=%s",
        (MAILDOMAIN, ))
    for alias, target in c.fetchall():
        assert target[0] == '&'
        target = target[1:]
        alias += "@"+MAILDOMAIN
        if alias not in nodes:
            nodes[alias] = Node(alias)
            d.add_node(nodes[alias])
        if target not in nodes:
            nodes[target] = Node(target)
            d.add_node(nodes[target])
        d.add_edge(Edge(nodes[alias], nodes[target]))
    for list in Utils.list_names():
        if list == 'plukdenacht2008':
            continue
        source = list+"@"+LISTDOMAIN
        if source not in nodes:
            nodes[source] = Node(source)
            d.add_node(nodes[source])
        m = MailList.MailList(list, lock=False)
        for member in m.members:
            if member not in nodes:
                nodes[member] = Node(member)
                d.add_node(nodes[member])
            d.add_edge(Edge(nodes[source], nodes[member]))
    d.write('the.dot')

if __name__ == '__main__':
    gen_dot()
