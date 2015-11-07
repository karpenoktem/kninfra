/etc/motd:
    file.managed:
        - template: jinja
        - source: salt://common/motd
