# vim: et:sta:bs=2:sw=4:
import locale
import json
from cStringIO import StringIO
import subprocess

from django.http import Http404 #, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
# from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
# from django.core.urlresolvers import reverse

from koert.drank.rikf import open_rikf_ar

from kn import settings
# from kn.leden.mongo import _id
# from kn.leden.date import date_to_dt, now
# from kn.base.http import JsonHttpResponse
from kn.barco.forms import *

settings.DRANK_REPOSITORIES = ['drank6', 'drank7', 'drank8']

@login_required
def barco_barform(request, repos):
    if repos not in settings.DRANK_REPOSITORIES:
        raise Http404
    repopath = '/home/infra/barco/%s/' % repos
    fields = open_rikf_ar(repopath + '/barforms/form-template-active.csv')
    prefill = {}
    if request.method == 'POST':
        form = BarFormMeta(request.POST)
        prefill = json.loads(request.POST['jsondata'])
        # The keys are unicode and that gives trouble when passing it to
        # the template and |safe'ing it. This line maps all keys to
        # non-unicode.
        prefill = dict(map(lambda x: (str(x[0]), x[1]), prefill.items()))
        if form.is_valid():
            fd = form.cleaned_data
            csv = StringIO();
            csv.write("# Ingevoerd door "+ str(request.user.name) +"\n")
            csv.write("Bar;;;;\n\n")
            csv.write(fd['pricebase'])
            csv.write(";")
            csv.write(str(fd['date']))
            csv.write(";")
            csv.write(fd['tapper'])
            csv.write(";")
            csv.write(fd['dienst'])
            csv.write(";")
            csv.write(str(fd['beginkas']))
            csv.write(";")
            csv.write(str(fd['eindkas']))
            if fd['comments'] != '':
                csv.write("\n\n# XXX ")
                csv.write(fd['comments'].replace("\n", "\n# "))
            csv.write("\n\n")
            emptyColumn = False
            column = 0
            while not emptyColumn:
                emptyColumn = True
                for row in fields:
                    if column >= len(row):
                        continue
                    emptyColumn = False
                    if row[column] == '':
                        continue
                    if row[column][0] == '!':
                        csv.write("# ");
                        csv.write(row[column][1:])
                        csv.write("\n");
                    else:
                        csv.write(row[column])
                        csv.write(";")
                        if row[column] in prefill:
                            csv.write(str(prefill[row[column]]))
                            csv.write("\n")
                        else:
                            csv.write("0\n")
                column += 1
            fn = 'barforms/%s.csv' % (fd['formname'])
            with open(repopath + fn, 'w') as fh:
                fh.write(csv.getvalue())
            subprocess.call(['/usr/bin/git', 'add', fn], cwd=repopath)
            msg = ("Barform %s ingevoerd via kninfra\n\n"
                    "Signed-off-by: kninfra <root@karpenoktem.nl>" %
                    fd['formname'])
            author = "%s <%s>" % (str(request.user.humanName),
                    request.user.canonical_email)
            subprocess.call(['/usr/bin/git', 'commit', '--author', author,
                '-m', msg, fn], cwd=repopath)
            subprocess.call(['/usr/bin/git', 'pull', '--rebase'], cwd=repopath)
            subprocess.call(['/usr/bin/git', 'push'], cwd=repopath)
    else:
        form = BarFormMeta()
    return render_to_response('barco/barform.html', {'fields': fields,
        'form': form, 'prefill': prefill},
        context_instance=RequestContext(request))
