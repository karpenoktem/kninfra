import imp
import os.path
import sys


def setup_virtual_package(name, path=os.curdir):
    """ Sets up a package at the given path with a given
        name """
    modulePath = os.path.abspath(path)
    f, fn, suffix = imp.find_module('__init__', [modulePath])
    imp.load_module(name, f, fn, suffix)
    sys.modules[name].__path__ = [modulePath]

# vim: et:sta:bs=2:sw=4:
