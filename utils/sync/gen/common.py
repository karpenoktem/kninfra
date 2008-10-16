from __future__ import with_statement

def read_ssv_file(filename):
        """ Reads values seperated by spaces in a simple one line file """
        with open(filename) as f:
                return f.readline()[:-1].split(' ')

DOMAIN = 'karpenoktem.nl'
LISTDOMAIN = 'lists.karpenoktem.nl'

EMAIL_ALLOWED = frozenset(
		    map(lambda x: chr(ord('a') + x), xrange(26)) +
		    map(lambda x: chr(ord('A') + x), xrange(26)) +
		    map(lambda x: chr(ord('0') + x), xrange(10)) +
		    ['.', '-'])

GALLERY_PATH = '/var/galleries/kn/'
MEMBERS_HOME = '/home/kn/'
MEMBER_PHOTO_DIR = 'fotos/'
