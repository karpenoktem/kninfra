mysql-server:
    pkg:
        - installed
mysql:
    service:
        - running
# Note that salt uses the root mysql user to execute its states.
# Thus the order of the following two commands is important.
"mysql root user":
    mysql_user:
        - present
        - name: root
        - password: {{ pillar['secrets']['mysql_root'] }}
/root/.my.cnf:
    file.managed:
        - source: salt://sankhara/root.my.cnf
        - template: jinja
        - mode: 600
        - user: root
        - group: root
