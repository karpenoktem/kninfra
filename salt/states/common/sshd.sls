ssh packages:
    pkg.installed:
        - pkgs:
            - openssh-server
            - sshguard
/etc/sshguard/whitelist:
    file.managed:
        - source: salt://common/sshguard-whitelist
ssh:
    service:
        - running
sshguard:
    service:
        - running
        - watch:
            - file: /etc/sshguard/whitelist
