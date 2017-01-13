import _import # noqa: F401

import kn.leden.entities as Es
from kn.planning.entities import Vacancy
from kn.leden.mongo import db, _id

wcol = db['planning_workers']

def main():
    count = 0
    for vacancy in Vacancy.all():
        if vacancy.assignee_id is None:
            continue
        worker_data = wcol.find_one({'_id': vacancy.assignee_id})
        if worker_data is None:
            continue
        user = Es.by_id(worker_data['user'])
        vacancy._data['assignee'] = _id(user)
        vacancy.save()
        count += 1
    print 'Converted %d vacancies.' % count

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
