nfs packages:
    pkg.installed:
        - pkgs:
            - nfs-server
/etc/exports:
    file.managed:
        - source: salt://phassa/exports
        - template: jinja
nfs running:
    service.running:
        - name: nfs-kernel-server
        - watch:
            - file: /etc/exports
