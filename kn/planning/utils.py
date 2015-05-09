from django.core.mail import EmailMessage

import kn.leden.entities as Es

def send_reminder(vacancy, update=True):
    to = vacancy.assignee
    e = vacancy.event
    p = vacancy.pool
    edate = e.date.strftime('%A %d %B')
    msgfmt = p.reminder_format
    msg = msgfmt % {
        'firstName': to.first_name,
        'date': edate,
        'time': vacancy.begin_time,
        'vacancyName': vacancy.name,
        'eventName': e.name}
    ccs = map(lambda x: Es.by_name(x).canonical_full_email, p.reminder_cc)
    subj = '%s, %s' % (vacancy.name.capitalize(), edate)
    em = EmailMessage(subj, msg, to=[to.canonical_full_email], headers={
            'Reply-To': Es.by_name(p.administrator).canonical_full_email},
        cc=ccs, bcc=ccs)
    em.send()
    if update:
        vacancy.reminder_needed = False
        vacancy.save()

# vim: et:sta:bs=2:sw=4:
