ldap packages:
    pkg.installed:
        - pkgs:
            - slapd
            - phpldapadmin
            - ldap-utils
/etc/phpldapadmin/config.php:
    file.managed:
        - source: salt://sankhara/phpldapadmin-config.php
        - template: jinja
/etc/nginx/sankhara.d/10-phpldapadmin.conf:
    file.managed:
        - source: salt://sankhara/phpldapadmin.nginx.conf
        - template: jinja
salt://sankhara/initialize-ldap.py:
    cmd.script:
        - creates: /root/.ldap-initialized
        - args: >-
            {{ grains['fqdn'] }} {{ pillar['secrets']['ldap_admin'] }}
            {{ pillar['secrets']['ldap_infra'] }}
            {{ pillar['secrets']['ldap_daan'] }}
            {{ pillar['secrets']['ldap_freeradius'] }}
