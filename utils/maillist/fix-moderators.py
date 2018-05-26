# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401
import argparse

from kn.utils.hans.mailman import MailList, Utils

SECRETARY = 'secretaris@karpenoktem.nl'
ALLOWED_OWNERS = ['wortel@karpenoktem.nl',
                  SECRETARY]


def main(dryrun=True):
    '''
    Set the secretary as moderator for every maillist that holds incoming mail
    and doesn't have a moderator yet. Otherwise only root gets a notification
    and mail might be unintentionally not sent.
    '''
    for name in sorted(Utils.list_names()):
        ml = MailList.MailList(name, True)
        try:
            changed = False
            if ml.generic_nonmember_action == 0:  # Accept
                pass
            elif ml.generic_nonmember_action == 1:  # Hold
                if ml.moderator == []:
                    changed = True
                    ml.moderator = [SECRETARY]
                    print('%-20s moderator set to %s'
                          % (name, SECRETARY))
                elif ml.moderator != [SECRETARY]:
                    print('%s: warning: moderator is %s'
                          % (name, ml.moderator))
            else:
                print('%s: warning: generic_nonmember_action=%d'
                      % (name, ml.generic_nonmember_action))
            if changed and not dryrun:
                ml.Save()
        finally:
            ml.Unlock()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    options = parser.parse_args()
    dryrun = not options.apply
    main(dryrun)
