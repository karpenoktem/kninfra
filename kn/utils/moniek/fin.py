from koert.gnucash.export import get_debitors, get_user_balance


def fin_get_account(moniek, name, full_name, account_type):
    gcf = moniek.gcf
    result = get_user_balance(
        gcf.book, [
            path + ":" + full_name
            for path in gcf.meta['accounts'][account_type]])
    result['mtime'] = gcf.mtime
    return result


def fin_get_debitors(moniek):
    gcf = moniek.gcf
    return get_debitors(gcf.book, gcf.meta['accounts']['user'])

# vim: et:sta:bs=2:sw=4:
