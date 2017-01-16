import _import  # noqa: F401

import kn.fotos.entities as fEs


def main():
    for e in fEs.all():
        e.update_search_text()

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
