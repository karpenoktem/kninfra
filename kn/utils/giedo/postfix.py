import logging
import kn.leden.entities as Es
from kn.settings import LISTS_MAILDOMAIN

def update_postfix():
        tbl = dict()
        for e in Es.all():
                if e.canonical_email is None or e.name is None:
                        continue
                for nm in e.other_names:
                        tbl[str(nm)] = (e.canonical_email,)
                if e.type == 'user':
                        tbl[str(e.name)] = (e.primary_email,)
                elif e.type == 'group':
                        if e.got_mailman_list:
                                tbl[str(e.name)] = ('%s@%s' % (str(e.name),
                                                        LISTS_MAILDOMAIN),)
                        else:
                                tbl[str(e.name)] = [m.canonical_email
                                                for m in e.get_members()]
                else:
                        logging.warn("postfix: unhandled type: %s" % e.type)

