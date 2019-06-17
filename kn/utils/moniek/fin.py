import koert.gnucash.export as koertexport
import protobufs.messages.moniek_pb2 as moniek_pb2
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

    absent_from_gnucash = moniek_pb2.FinNamesList()
    absent_from_website = moniek_pb2.FinNamesList()

    for t, tnames in six.iteritems(names):
        paths = gcf.meta['accounts'][t]
        found_one = False
        missingNames = set()

        for name in tnames:
            for path in paths:
                if name in book.ac_by_path(path).children:
                    found_one = True
                    break
            if not found_one:
                missingNames.add(name)

        getattr(absent_from_gnucash, t).extend(list(missingNames))

    for t, paths in six.iteritems(gcf.meta['accounts']):
        tnames = frozenset(names[t])
        missingNames = set()

        for path in paths:
            for name in book.ac_by_path(path).children:
                if name not in tnames:
                    missingNames.add(name)

        getattr(absent_from_website, t).extend(list(missingNames))

    return moniek_pb2.FinMissingNames(gnucash=absent_from_gnucash,
                                      website=absent_from_website)


def get_gnucash_object(moniek, year, handle):
    """Returns a list of objects with this handle,
    which should (but does not always) contain one object."""
    gcf = moniek.gcf_by_year(year)
    if gcf is None:
        return None
    book = gcf.book

    return [koertexport.export(obj) for obj in book.obj_by_handle(handle)]


def get_errors(moniek, year):
    gcf = moniek.gcf_by_year(year)
    if gcf is None:
        return None

    return koertexport.export_checks_of_book(gcf.book)


def get_years(moniek):
    return moniek.years


# vim: et:sta:bs=2:sw=4:
