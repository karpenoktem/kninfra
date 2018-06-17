# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

from kn.planning.entities import Vacancy
from kn.planning.utils import send_reminder

vacancies = Vacancy.all_needing_reminder()
for vacancy in vacancies:
    if vacancy.assignee is None:
        continue
    send_reminder(vacancy)
