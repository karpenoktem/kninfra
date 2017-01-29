from django.utils.translation import ugettext as _


def humanized_enum(it, normal_sep=u", ", final_sep=None):
    if final_sep is None:
        final_sep = _(" en ")
    lst = list(it)
    if len(lst) == 0:
        return ""
    if len(lst) == 1:
        return lst[0]
    return final_sep.join([normal_sep.join(lst[0:-1]), lst[-1]])

# vim: et:sta:bs=2:sw=4:
