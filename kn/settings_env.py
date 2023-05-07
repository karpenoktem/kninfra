import json
import os

from django.utils.translation import ugettext_lazy as _

with open(os.environ["KN_SETTINGS"], "r") as f:
    globals().update(json.load(f))

# Load more settings from environment variables, useful for secrets.

for varname, value in os.environ.items():
    if varname.startswith("KN_"):
        globals()[varname[3:]] = value

# Settings that cannot be represented in json. These should not need to be
# changed anyway.

DT_MIN = datetime.datetime(2004, 8, 31)
DT_MAX = datetime.datetime(5004, 9, 1)

LANGUAGES = [
    ("nl", _("Nederlands")),
    ("en", _("Engels")),
]
