#!/usr/bin/env python3

# Very simple git update hook script to check whether the committed files look
# somewhat like XML.
# Note: it doesn't try to validate the XML. It doesn't even check
# subdirectories. It is pretty dumb.

import subprocess
import sys

XML_FILES = ['xml', 'gnucash']

ref = sys.argv[1]
oldobject = sys.argv[2]
newobject = sys.argv[3]


def catfile(objecthash):
    ''' Returns the contents of the given git object hash. '''
    return subprocess.check_output(['git', 'cat-file', '-p', objecthash]).decode()


# A commit looks somewhat like this:
#
#     tree <hash>
#     parent <hash>
#     author <name> <email> <timestamp>
#     committer <name> <email> <timestamp>
#
#     <commit message>
#
# We're only interested in the tree.
for line in catfile(newobject).split('\n'):
    if line.startswith('tree '):
        treehash = line.split()[1]

# From this tree (actually: directory index), extract the file names and hashes.
for line in catfile(treehash).split('\n'):
    if not line:
        continue
    # file name and hash
    objecthash = line.split(maxsplit=3)[2]
    objectname = line.split(maxsplit=3)[3]
    if objectname.rsplit('.')[-1] in XML_FILES:
        # contents of the file
        contents = catfile(objecthash)
        if not contents.startswith('<?xml '):
            print("File doesn't look like XML, make sure compression is disabled:", objectname)
            sys.exit(1)
