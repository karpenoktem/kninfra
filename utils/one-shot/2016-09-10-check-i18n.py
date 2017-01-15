""" Use crude heuristics to check which files are still not ready
    for translation. """

import os.path


class Program:
    def check_py(self, path):
        with open(path) as f:
            contents = f.read()
        ok = 'import ugettext from' in contents
        print '- [x]' if ok else '- [ ]',
        print os.path.relpath(path, self.repo_path)

    def check_html(self, path):
        with open(path) as f:
            contents = f.read()
        ok = '{% load i18n %}' in contents
        print '- [x]' if ok else '- [ ]',
        print os.path.relpath(path, self.repo_path)

    def main(self):
        self.repo_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), '..', '..')
        s = [self.repo_path]
        while s:
            path = s.pop()
            for c_fn in os.listdir(path):
                if c_fn.startswith('.'):
                    continue
                c_path = os.path.join(path, c_fn)
                if os.path.relpath(c_path, self.repo_path) == 'utils':
                    continue
                if os.path.isdir(c_path):
                    s.append(c_path)
                    continue
                if c_fn == 'settings.py':
                    continue
                if c_fn.endswith('.py'):
                    self.check_py(c_path)
                if c_fn.endswith('.html') or c_fn.endswith('.mail.txt'):
                    self.check_html(c_path)

if __name__ == '__main__':
    Program().main()
