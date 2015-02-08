base:
    '*':
        - common.locale
        - common.sshd
        - common.adminutils
        - common.git
    'sankhara':
        - sankhara.mongo
        - sankhara.kninfra
        - sankhara.nginx
