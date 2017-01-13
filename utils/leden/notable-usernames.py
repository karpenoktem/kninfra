# vim: et:sta:bs=2:sw=4:
import _import

from kn.leden.models import OldKnUser, OldKnGroup

leden = list(OldKnGroup.objects.get(name='leden').user_set.all())
leden.extend(OldKnGroup.objects.get(name='leden-oud').user_set.all())
leden.sort(cmp=lambda x, y: cmp(x.first_name, y.first_name))

years = list()

i = 1
while True:
    try:
        g = OldKnGroup.objects.get(name='leden%s' % i)
    except OldKnGroup.DoesNotExist:
        break
    years.append(frozenset(g.user_set.all()))
    i += 1

firstnames = dict()
for l in leden:
    if l.first_name not in firstnames:
        firstnames[l.first_name] = 0
    firstnames[l.first_name] += 1

for l in leden:
    if l.username != l.first_name.lower() \
            or firstnames[l.first_name] > 1:
        memb = ' '.join(['*' if l in year else ' ' for year in years])
        print "%-12s %-15s  %-20s %-20s" % (l.username, l.first_name,
                            l.last_name, memb)
