forum mysql:
    mysql_user.present:
        - host: localhost
        - name: forum
        - password: {{ pillar['secrets']['mysql_forum'] }}
    mysql_database.present:
        - name: forum
forum mysql grant 1:
    mysql_grants.present:
        - grant: all privileges
        - database: forum.*
        - user: forum
forum git clone:
    git.latest:
        - name: git://github.com/karpenoktem/punbb
        - target: /srv/forum
/srv/forum/cache:
    file.directory:
        - user: www-data
        - recurse: [user]
/srv/forum/img/avatars:
    file.directory:
        - user: www-data
        - recurse: [user]
/etc/nginx/sankhara.d/10-forum.conf:
    file.managed:
        - source: salt://sankhara/forum.nginx.conf
        - template: jinja
salt://sankhara/install-forum.py:
    cmd.script:
        - creates: /srv/forum/config.php
        - args: >-
            {{ pillar['secrets']['mysql_forum'] }}
            {{ grains['fqdn'] }}
forum mysql grant 2:
    mysql_grants.present:
        - grant: select
        - database: forum.users
        - user: giedo
