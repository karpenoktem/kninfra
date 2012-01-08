# vim: et:sta:bs=2:sw=4:
import locale
import json
from cStringIO import StringIO
import subprocess
import os.path

from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
# from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from koert.drank.rikf import open_rikf_ar

from kn import settings
# from kn.leden.mongo import _id
# from kn.leden.date import date_to_dt, now
# from kn.base.http import JsonHttpResponse
from kn.barco.forms import BarformMeta, InvCountMeta

settings.DRANK_REPOSITORIES = ['drank6', 'drank7', 'drank8']
settings.DRANK_REPOS_PATH = '/home/infra/barco/%s/'

# The specific behaviour for each different form 
#  (barform, inventory count, ... ) is stored in a subclass
#  of the "FormSpecifics" class.
class FormSpecifics(object):
    def __init__(self, 
            django_form, 
            django_template, 
            dir_in_repo, 
            template_path # see explanation below
            ):
        self.django_form = django_form
        self.django_template = django_template
        self.template_path = template_path
        self.dir_in_repo = dir_in_repo

    def entered_data_to_file(self, fd, csv, template): 
        raise NotImplementedError


#   On Templates For Counts
#
# Most Forms contain a "Count" -- a dictionary where the
# names are strings (like product names) and the keys are decimals.
# The keys are grouped in categories and are presented in a table
# as prescribed by in a "template"-file for each form.


# The following function writes data (entered by the user) of count
# to a file in an order resembling the template.
def template_write_data_to_file(template, data, csv):
    emptyColumn = False
    column = 0
    while not emptyColumn:
        emptyColumn = True
        for row in template:
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
                if row[column] in data:
                    csv.write(str(data[row[column]]))
                    csv.write("\n")
                else:
                    csv.write("0\n")
        column += 1


class BarformSpecifics(FormSpecifics):
    def __init__(self):
        super(BarformSpecifics, self).__init__(
                django_form=BarformMeta,
                django_template="barco/barform.html",
                dir_in_repo="barforms",
                template_path="form-template-active.csv")

    def entered_data_to_file(self, fd, csv, template, prefill):
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
                csv.write(fd['comments'].replace("\r\n", "\n").replace("\n", "\n# "))
            csv.write("\n\n")
            template_write_data_to_file(template, prefill, csv)


class InvCountSpecifics(FormSpecifics):
    def __init__(self):
        super(InvCountSpecifics, self).__init__(
                django_form=InvCountMeta,
                django_template="barco/form.html",
                template_path="form-template-active.csv",
                dir_in_repo="inventory")

    def entered_data_to_file(self, fd, csv, template, prefill):
            csv.write("voorraadtelling\n\n")
            csv.write(str(fd['date']))
            csv.write(" # tellers: ")
            csv.write(fd['tellers'])
            if fd['comments'] != '':
                csv.write("\n\n# XXX ")
                csv.write(fd['comments'].replace("\n", "\n# "))
            csv.write("\n\n")
            template_write_data_to_file(template, prefill, csv)

      
settings.BARCO_FORMS = {
        'barform': BarformSpecifics(),
        'invcount': InvCountSpecifics(),
        }



@login_required
def barco_enterform(request, repos, formname):
    if repos not in settings.DRANK_REPOSITORIES:
        raise Http404
    if formname not in settings.BARCO_FORMS:
        raise Http404
    formspec = settings.BARCO_FORMS[formname]
    repopath = settings.DRANK_REPOS_PATH % (repos,)
    dir_path = os.path.join(repopath, formspec.dir_in_repo)
    template_path = os.path.join(dir_path, formspec.template_path)
    template = open_rikf_ar(template_path)

    prefill = {}
    if request.method == 'POST':
        form = (formspec.django_form)(request.POST)
        prefill = json.loads(request.POST['jsondata'])
        # The keys are unicode and that gives trouble when passing it to
        # the template and |safe'ing it. This line maps all keys to
        # non-unicode.
        prefill = dict(map(lambda x: (str(x[0]), x[1]), prefill.items()))
        if form.is_valid():
            # Dump the entered data to a file ...
            fd = form.cleaned_data
            csv = StringIO();
            csv.write("# Ingevoerd door "+ str(request.user.name) +"\n")
            formspec.entered_data_to_file(fd, csv, template, prefill)
            
            # commit it to the repository ...
            fn = os.path.join(formspec.dir_in_repo,'%s.csv'%(fd['formname']))
            with open(os.path.join(repopath, fn), 'w') as fh:
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

            # and get back to the user:
            request.user.push_message("Opgeslagen!")
            return HttpResponseRedirect(reverse('barco-enterform', 
                args=(repos,formname)))
    form = formspec.django_form()
    return render_to_response(formspec.django_template, 
            {'fields': template, 'form': form, 'prefill': prefill},
        context_instance=RequestContext(request))
