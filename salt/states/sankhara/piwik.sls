piwik apt source:
    pkgrepo.managed:
        - name: deb http://debian.piwik.org/ piwik main
        - file: /etc/apt/sources.list.d/piwik.list
        - key_url: salt://sankhara/piwik.gpg
piwik packages:
    pkg.installed:
        - pkgs:
            - piwik
/etc/nginx/sankhara.d/10-piwik.conf:
    file.managed:
        - source: salt://sankhara/piwik.nginx.conf
        - template: jinja
piwik mysql:
    mysql_user.present:
        - host: localhost
        - name: piwik
        - password: {{ pillar['secrets']['mysql_piwik'] }}
    mysql_database.present:
        - name: piwik
piwik mysql grant:
    mysql_grants.present:
        - grant: all privileges
        - database: piwik.*
        - user: piwik
# TODO install piwik.  See https://github.com/piwik/piwik/issues/10257
