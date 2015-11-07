import tempfile
import os.path
import shutil

import pyx

from sarah.runtime import CallCatchingWrapper

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.servers.basehttp import FileWrapper
from django.views.decorators.cache import cache_page

from kn.base.conf import from_settings_import
from_settings_import("DT_MIN", "DT_MAX", globals())
from django.conf import settings

import kn.leden.entities as Es

@login_required
@cache_page(60 * 60)
def member_count(request):
    ret = _generate_member_count()
    g = pyx.graph.graphxy(width=20, x=pyx.graph.axis.linear(min=1,
                    painter=pyx.graph.axis.painter.regular(
                            gridattrs=[pyx.attr.changelist([
                                pyx.color.gray(0.8)])])))
    g.plot(pyx.graph.data.points(ret,x=1,y=2),
                [pyx.graph.style.symbol(size=0.03,
                        symbol=pyx.graph.style.symbol.plus)])
    # work-around for PyX trying to write in the current directory
    f = tempfile.TemporaryFile()
    old_wd = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    try:
        os.chdir(temp_dir)
        # Write PDF.  Prevent its call to f.close().
        g.writePDFfile(CallCatchingWrapper(f, lambda x: x == 'close',
                                                    lambda x,y,z,w: None))
    finally:
        os.chdir(old_wd)
        shutil.rmtree(temp_dir)
    f.seek(0)
    return HttpResponse(f, content_type='application/pdf')

def _generate_member_count():
    events = []
    for rel in Es.query_relations(_with=Es.id_by_name('leden'), how=None):
        events.append((max(rel['from'], Es.DT_MIN), True))
        if rel['until'] != Es.DT_MAX:
            events.append((rel['until'], False))
    N = 0
    old_days = -1
    old_N = None
    ret = []
    for when, what in sorted(events, key=lambda x: x[0]):
        N += 1 if what else -1
        days = (when - Es.DT_MIN).days
        if old_days != days:
            if old_N:
                ret.append([old_days, old_N])
            old_days = days
            old_N = N
    ret.append([days, N])
    ret = [(1 + days / 365.242, N) for days, N in ret]
    return ret

# vim: et:sta:bs=2:sw=4:
