from koert.gnucash.export import get_debitors, get_user_balance


def fin_get_account(moniek, name, full_name):
    gcf = moniek.gcf
    result = get_user_balance(gcf.book,
                              [gcf.meta['creditors account'] + ":" + full_name,
                              gcf.meta['debitors account'] + ":" + full_name])
    result['mtime'] = gcf.mtime
    return result


def fin_get_debitors(moniek):
    gcf = moniek.gcf
    return get_debitors(gcf.book,
                        gcf.meta['creditors account'],
                        gcf.meta['debitors account'])

# vim: et:sta:bs=2:sw=4:
