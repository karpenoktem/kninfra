import _import  # noqa: F401

import kn.fotos.entities as fEs
import multiprocessing


def cache(the_id):
    e = fEs.by_id(the_id)
    print the_id
    for c in e.CACHES:
        print c
        e.ensure_cached(c)


def main():
    pool = multiprocessing.Pool(7)
    pool.map(cache, [e._id for e in fEs.all()])

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
