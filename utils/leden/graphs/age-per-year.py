# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import pyx
import kn.leden.entities as Es


def main():
    N = 0
    ages = set([None])
    data = []
    while True:
        current = {None: 0}
        N += 1
        g = Es.by_name('leden%s' % N)
        if g is None:
            break
        start_dt, end_dt = Es.year_to_range(N)
        for m in g.get_members():
            if m.dateOfBirth is None:
                continue
            age = int((start_dt - m.dateOfBirth).days / 365.242)
            if age not in current:
                current[age] = 0
            if age not in ages:
                ages.add(age)
            current[age] += 1
        data.append(current)
    if None in ages:
        ages.remove(None)
    with open('age-per-year.txt', 'w') as f:
        f.write('#  ?')
        for age in xrange(min(*ages), max(*ages)):
            f.write(' ' + str(age))
        f.write('\n')
        for _year, d in enumerate(data):
            year = _year + 1
            f.write('%s %s ' % (year, d.get(None, 0)))
            for age in xrange(min(*ages), max(*ages)):
                f.write('%2d ' % d.get(age, 0))
            f.write('\n')
    g = pyx.graph.graphxy(width=14, x=pyx.graph.axis.bar())
    colass = {}
    for i, age in enumerate(xrange(min(*ages) + 1, max(*ages))):
        colass['y%s' % age] = i + 2
    styles = [pyx.graph.style.bar([
        pyx.color.gradient.ReverseHue.select(
            0, max(*ages) - min(*ages))])]
    for i, age in enumerate(xrange(min(*ages) + 1, max(*ages))):
        styles.extend([pyx.graph.style.stackedbarpos('y%s' % age),
                       pyx.graph.style.bar([
                           pyx.color.gradient.ReverseHue.select(
                               i + 1, max(*ages) - min(*ages))])])
    cdata = []
    for d in data:
        cum = 0
        d2 = {}
        for age in xrange(min(*ages), max(*ages)):
            cum += d.get(age, 0)
            d2[age] = cum
        cdata.append(d2)
    g.plot(pyx.graph.data.points(
        [[_year + 1] + [d.get(age, 0)
                        for age in xrange(min(*ages), max(*ages))]
         for _year, d in enumerate(cdata)],
        xname=0, y=1, **colass), styles)
    g.writePDFfile('age-per-year')

if __name__ == '__main__':
    main()
