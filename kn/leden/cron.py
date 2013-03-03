""" Scheduled functions """

import kn.leden.entities as Es

from kn.base.mail import render_then_email

def send_informacie_digest():
    """ Sends the notifications for the informacie. """
    ntfs = Es.pop_all_informacie_notifications()
    if not ntfs:
        return
    render_then_email('leden/informacie-digest.mail.txt',
                      Es.by_name('informacie').canonical_full_email, {
                                'ntfs': ntfs})

# vim: et:sta:bs=2:sw=4:
