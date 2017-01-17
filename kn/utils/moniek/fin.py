from django.conf import settings
from koert.gnucash.export import get_user_balance, get_debitors



def fin_get_account(moniek, name, full_name):
    result = get_user_balance(moniek.gcf.book,
            settings.FIN_CREDITORS_ACCOUNT+":"+full_name,
            settings.FIN_DEBITORS_ACCOUNT+":"+full_name)
    result['mtime'] = gcf.mtime
    return result

def fin_get_debitors(moniek):
    return get_debitors(moniek.gcf.book,
            settings.FIN_CREDITORS_ACCOUNT,
            settings.FIN_DEBITORS_ACCOUNT)

# vim: et:sta:bs=2:sw=4:
