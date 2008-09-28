from __future__ import with_statement

def read_ssv_file(filename):
        """ Reads values seperated by spaces in a simple one line file """
        with open(filename) as f:
                return f.readline()[:-1].split(' ')

