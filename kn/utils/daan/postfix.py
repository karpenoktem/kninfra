from subprocess import call

import six

from django.conf import settings


def set_postfix_slm_map(tbl):
    # TODO check whether the entries are valid and within karpenoktem.nl!
    with open(settings.POSTFIX_SLM_MAP, 'w') as f:
        for k, v in six.iteritems(tbl):
            f.write("%s %s\n" % (k, ', '.join(v.values)))
    call(['postmap', settings.POSTFIX_SLM_MAP])


def set_postfix_map(tbl):
    # TODO check whether the entries are valid and within karpenoktem.nl!
    with open(settings.POSTFIX_VIRTUAL_MAP, 'w') as f:
        for k, v in six.iteritems(tbl):
            if not v.values:
                continue
            f.write("%s %s\n" % (k, ', '.join(v.values)))
    call(['postmap', settings.POSTFIX_VIRTUAL_MAP])

# vim: et:sta:bs=2:sw=4:
