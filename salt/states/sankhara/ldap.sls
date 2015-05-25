ldap packages:
    pkg.installed:
        - pkgs:
            - slapd
            - phpldapadmin
/etc/nginx/sankhara.d/10-phpldapadmin.conf:
    file.managed:
        - source: salt://sankhara/phpldapadmin.nginx.conf
        - template: jinja
# TODO
