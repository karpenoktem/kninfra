nfs packages:
    pkg.installed:
        - pkgs:
            - nfs-server
/srv/nfs:
    file.directory
/srv/nfs/var:
    file.directory
{% for dir in ['home', 'groups', 'root', 'etc', 'var/log'] %}
/srv/nfs/{{ dir }}:
    file.directory:
        - user: root
    mount.mounted:
        - device: /{{ dir }}
        - opts: bind
        - fstype: none
{% endfor %}
# /srv/nfs/wolk:
#     mount.mounted:
#         - device: /srv/wolk
#         - opts: bind
#         - fstype: none
/etc/exports:
    file.managed:
        - source: salt://phassa/exports
        - template: jinja
nfs running:
    service.running:
        - name: nfs-kernel-server
        - watch:
            - file: /etc/exports
