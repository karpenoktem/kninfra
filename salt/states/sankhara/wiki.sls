wiki packages:
    pkg.installed:
        - pkgs:
            - php-intl
            - memcached
            - mediawiki
            - imagemagick
/etc/nginx/sankhara.d/10-wiki.conf:
    file.managed:
        - source: salt://sankhara/wiki.nginx.conf
        - template: jinja
wiki mysql:
    mysql_user.present:
        - host: localhost
        - name: wiki
        - password: {{ pillar['secrets']['mysql_wiki'] }}
    mysql_database.present:
        - name: wiki
wiki mysql grant 1:
    mysql_grants.present:
        - grant: all privileges
        - database: wiki.*
        - user: wiki
install wiki:
    cmd.run:
        - creates: /etc/mediawiki/.is-installed
        - name: >
            rm -f /etc/mediawiki/LocalSettings.php &&
            php /var/lib/mediawiki/maintenance/install.php KNWiki Admin \
                --dbname wiki --dbuser wiki \
                --dbpass {{ pillar['secrets']['mysql_wiki'] }} \
                --pass {{ pillar['secrets']['wiki_admin'] }} \
                --installdbuser wiki \
                --installdbpass {{ pillar['secrets']['mysql_wiki'] }} \
                --scriptpath /wiki &&
            touch /etc/mediawiki/.is-installed
/etc/mediawiki/LocalSettings.php:
    file.managed:
        - source: salt://sankhara/wiki-settings.php
        - template: jinja
        - user: www-data
        - mode: 600
"wiki knauth":
    git.latest:
        - name: https://github.com/karpenoktem/knauth
        - target: /etc/mediawiki/knauth
        - user: root
    require:
        - pkg: git
wiki mysql grant 2:
    mysql_grants.present:
        - grant: select
        - database: wiki.user
        - user: giedo
wiki mysql grant 3:
    mysql_grants.present:
        - grant: select
        - database: wiki.user_groups
        - user: giedo
