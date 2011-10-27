# vim: et:sta:bs=2:sw=4:
# Hey Bas,
#
# Ik heb je laatst op een borrel aangesproken over jou welbekende
# grafiekjes.  Ik vroeg je of je misschien eens wilde kijken naar hoe
# snel leden actief worden binnen Karpe Nokten, of het afneemt en andere
# verband houdende zaken.  Jij zei toen dat ik je maar moest mailen omdat
# je het anders niet zou onthouden.  dus hierbij een herinneringsmailtje :)
#
# groetjes Iris Smits
import _import
import datetime

import kn.leden.entities as Es
from kn.settings import DT_MIN, DT_MAX
from kn.leden.mongo import _id

llut = dict()
clut = dict()
comms = [g for g in Es.by_name('fac-comms').get_bearers() if g.is_group]
comms.extend([g for g in Es.by_name('act-comms').get_bearers() if g.is_group])
comms.append(Es.by_name('bestuur'))
leden = Es.by_name('leden').get_members()
leden_lut = {}
comms_lut = {}
for c in comms:
    comms_lut[_id(c)] = c
for l in leden:
    clut[l] = (DT_MAX, None)
    llut[l] = DT_MAX
    leden_lut[_id(l)] = l

for rel in Es.query_relations(who=leden, _with=Es.by_name('leden'), how=None):
    w = leden_lut[rel['who']]
    llut[w] = min(llut[w], rel['from'])

for rel in Es.query_relations(who=leden, _with=comms, how=None):
    w = leden_lut[rel['who']]
    if rel['from'] < clut[w][0]:
        clut[w] = (rel['from'], comms_lut[rel['with']])

had = set()
for y in range(4,9):
    print
    print 'Jaar', y
    nnever = 0
    nalways = 0
    navg = 0
    avg_sum = datetime.timedelta(0)
    for l in Es.by_name('leden'+str(y)).get_members():
        if l not in llut:
            continue
        if l in had:
            continue
        had.add(l)
        if clut[l][0] == DT_MIN:
            nalways += 1
            continue
        if clut[l][0] == DT_MAX:
            nnever += 1
            continue
        avg_sum += clut[l][0] - llut[l]
        navg += 1

    print "Onbekend (actief)     %s" % nalways
    print "Nooit actief geweest  %s" % nnever
    print "Actief                %s" % navg
    print "Actief gem. na        %s" % (avg_sum / navg)