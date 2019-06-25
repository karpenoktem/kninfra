# vim: et:sta:bs=2:sw=4:
# _import.py
#   sets up the django environment and mailman for the utils
#


import imp
import os
import os.path
import sys

import django


def setup_virtual_package(name, path=os.curdir):
    """ Sets up a package at the given path with a given
        name """
    modulePath = os.path.abspath(path)
    f, fn, suffix = imp.find_module('__init__',
                                    [modulePath])
    imp.load_module(name, f, fn, suffix)
    sys.modules[name].__path__ = [modulePath]


if __name__ != '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kn.settings")
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(
        os.path.realpath(__file__[:-1] if __file__[-4:] in
                         ('.pyc', '.pyo') else __file__))), '..'))
    setup_virtual_package('kn', os.path.join(root, 'kn'))
    setup_virtual_package('protobufs', os.path.join(root, 'protobufs'))
    django.setup()
