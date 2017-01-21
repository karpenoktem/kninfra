# vim: et:sta:bs=2:sw=4:

# NOTE stub: dangerous!

import re
import os
import sys
import os.path

MODELINE = "# vim: et:sta:bs=2:sw=4:"


def check_spaces(path):
    try:
        with open(path) as f:
            lines = f.readlines()
    except IOError:
        return
    tabs = map(lambda x: len(re.match('^ *', x).group(0)), lines)
    fours = len(filter(lambda x: x != 0 and x % 4 == 0, tabs))
    eights = len(filter(lambda x: x != 0 and x % 8 == 0, tabs))
    if eights < 0.90 * fours:
        return
    if eights < 5 or fours < 5:
        return
    print path, 'fours -> eights', fours, eights
    for i in xrange(len(lines)):
        s = tabs[i] / 8 * 4
        s += tabs[i] % 8
        lines[i] = (' ' * s) + lines[i].strip(' ')
    with open(path, 'w') as f:
        f.write(''.join(lines))


def check_tabs(path):
    try:
        with open(path) as f:
            txt = f.read()
    except IOError:
        return
    if "\t" not in txt:
        return
    txt = txt.expandtabs(4)
    with open(path, 'w') as f:
        f.write(txt)


def check_stray_whitespace(path):
    try:
        with open(path) as f:
            lines = f.readlines()
    except IOError:
        return
    stripped_lines = map(lambda x: x.rstrip(), lines)
    if lines != stripped_lines:
        with open(path, 'w') as f:
            f.write("\n".join(stripped_lines))


def check_modeline(path):
    changed = False
    try:
        with open(path) as f:
            txt = f.read()
    except IOError:
        return
    modeline_regex = '^# vim:.*$'
    m = re.search(modeline_regex, txt, re.MULTILINE)
    if m:
        if m.group(0) != MODELINE:
            print path, 'Updated modeline'
            txt = txt[:m.start(0)] + MODELINE + txt[m.end(0):]
            changed = True
    else:
        # Add the modeline as first line (if there is no hashbang)
        print path, 'Added modeline'
        if txt.startswith('#!'):
            nextline = txt.index("\n")
            txt = txt[:nextline] + "\n" + MODELINE + txt[nextline:]
        else:
            txt = MODELINE + "\n" + txt
        changed = True
    if changed:
        with open(path, 'w') as f:
            f.write(txt)


def main(rpath):
    stack = ['']
    while stack:
        spath = stack.pop()
        dpath = os.path.join(rpath, spath)
        for child in os.listdir(dpath):
            cpath = os.path.join(dpath, child)
            if child == '.git':
                continue
            if os.path.isdir(cpath):
                stack.append(os.path.join(spath, child))
                continue
            if child.endswith('.py'):
                # check_spaces(cpath)
                check_tabs(cpath)
                check_modeline(cpath)
                check_stray_whitespace(cpath)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        path = os.path.expanduser('~/repo-dev')
    else:
        path = sys.argv[1]
    main(path)
