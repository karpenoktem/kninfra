import koert.gnucash.export as koertexport
import six


def get_account(moniek, name, full_name, account_type):
    gcf = moniek.gcf
    result = koertexport.get_user_balance(
        gcf.book, [
            path + ":" + full_name
            for path in gcf.meta['accounts'][account_type]])
    result['mtime'] = gcf.mtime
    return result


def get_debitors(moniek):
    gcf = moniek.gcf
    return koertexport.get_debitors(gcf.book, gcf.meta['accounts']['user'])


def check_names(moniek, names):
    gcf = moniek.gcf
    book = gcf.book

    absent_in_gnucash = {}
    absent_on_website = {}

    for t, tnames in six.iteritems(names):
        paths = gcf.meta['accounts'][t]
        found_one = False

        absent_in_gnucash[t] = set()

        for name in tnames:
            for path in paths:
                if name in book.ac_by_path(path).children:
                    found_one = True
                    break
            if not found_one:
                absent_in_gnucash[t].add(name)

        absent_in_gnucash[t] = list(absent_in_gnucash[t])

    for t, paths in six.iteritems(gcf.meta['accounts']):
        absent_on_website[t] = set()
        tnames = set(names[t])

        for path in paths:
            for name in book.ac_by_path(path).children:
                if name not in tnames:
                    absent_on_website[t].add(name)

        absent_on_website[t] = list(absent_on_website[t])

    return {'gnucash': absent_in_gnucash, 'website': absent_on_website}

# vim: et:sta:bs=2:sw=4:
