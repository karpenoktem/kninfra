ircd packages:
    pkg.installed:
        - pkgs:
            - inspircd
            - atheme-services

/etc/inspircd/inspircd.conf:
    file.managed:
        - template: jinja
        - source: salt://sankhara/inspircd.conf
/etc/inspircd/inspircd.motd:
    file.managed:
        - template: jinja
        - source: salt://sankhara/inspircd.motd
/etc/inspircd/inspircd.rules:
    file.managed:
        - source: salt://sankhara/inspircd.rules
/etc/atheme/atheme.conf:
    file.managed:
        - template: jinja
        - source: salt://sankhara/atheme.conf
/etc/default/atheme-services:
    file.managed:
        - source: salt://sankhara/atheme.default

inspircd running:
    service.running:
        - name: inspircd
        #- reload: True # ExecReload directive missing in systemd unit file
        - watch:
            - file: /etc/inspircd/inspircd.conf
            - file: /etc/inspircd/inspircd.motd
            - file: /etc/inspircd/inspircd.rules
atheme services running:
    service.running:
        - name: atheme-services
        - watch:
            - file: /etc/atheme/atheme.conf
            - file: /etc/default/atheme-services
