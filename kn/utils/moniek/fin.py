from django.conf import settings
from koert.gnucash.tools import open_gcf_in_git_repo
from koert.gnucash.export import get_user_balance



def fin_get_account(moniek, name, full_name):
    gcf = open_gcf_in_git_repo(
            settings.FIN_REPO_PATH,
            settings.FIN_FILENAME,
            cachepath=settings.FIN_CACHE_PATH)
    return get_user_balance(gcf.books[0],
            settings.FIN_CREDITORS_ACCOUNT+":"+full_name,
            settings.FIN_DEBITORS_ACCOUNT+":"+full_name)

# vim: et:sta:bs=2:sw=4:
