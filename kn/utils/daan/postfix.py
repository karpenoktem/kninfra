from django.conf import settings
from subprocess import call


def set_postfix_slm_map(daan, tbl):
    # TODO check whether the entries are valid and within karpenoktem.nl!
    with open(settings.POSTFIX_SLM_MAP, 'w') as f:
        for k, v in tbl.iteritems():
            f.write("%s %s\n" % (k, ', '.join(v)))
    call(['postmap', settings.POSTFIX_SLM_MAP])


def set_postfix_map(daan, tbl):
    # TODO check whether the entries are valid and within karpenoktem.nl!
    with open(settings.POSTFIX_VIRTUAL_MAP, 'w') as f:
        for k, v in tbl.iteritems():
            v = filter(lambda x: x, v)
            if not v:
                continue
            f.write("%s %s\n" % (k, ', '.join(v)))
    call(['postmap', settings.POSTFIX_VIRTUAL_MAP])

# vim: et:sta:bs=2:sw=4:
