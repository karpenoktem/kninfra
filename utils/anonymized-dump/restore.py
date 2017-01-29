import _import  # noqa: F401

from kn.leden.mongo import db

import bson

import kn.leden.entities as Es
import kn.moderation.entities as Es_mod
import kn.planning.entities as Es_plan
import kn.poll.entities as Es_poll
import kn.reglementen.entities as Es_regl
import kn.subscriptions.entities as Es_subscr


def main():
    print 'Are you sure you want to run this?'
    return
    db.command('dropDatabase')
    print 'Creating indices'
    print ' leden'
    Es.ensure_indices()
    print ' moderation'
    Es_mod.ensure_indices()
    print ' planning'
    Es_plan.ensure_indices()
    print ' poll'
    Es_poll.ensure_indices()
    print ' regl'
    Es_regl.ensure_indices()
    print ' subscriptions'
    Es_subscr.ensure_indices()
    print
    print 'Restoring data'
    print ' entities'
    for e in bson.decode_all(open('entities.bsons').read()):
        db['entities'].save(e)
    print ' relations'
    for e in bson.decode_all(open('relations.bsons').read()):
        db['relations'].save(e)
    print ' events'
    for e in bson.decode_all(open('events.bsons').read()):
        db['events'].save(e)


if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
