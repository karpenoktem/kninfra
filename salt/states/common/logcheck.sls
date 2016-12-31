logcheck:
    pkg:
        - installed
/etc/logcheck/logcheck.conf:
    file.managed:
        - source: salt://common/logcheck.conf
        - template: jinja
# TODO should not overwrite everything in /etc/logcheck: it should just
#      merge the directories.
# https://github.com/bwesterb/x-logcheck:
#     git.latest:
#         - target: /etc/logcheck/
#         - force: true
#     require:
#         - pkg: git
