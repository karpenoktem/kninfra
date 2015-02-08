base:
    '*':
        - common.locale
        - common.sshd
        - common.nginx
        - common.adminutils
        - common.git
    'sankhara':
        - sankhara.mongo
        - sankhara.kninfra
