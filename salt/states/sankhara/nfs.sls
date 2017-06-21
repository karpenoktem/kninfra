nfs packages:
    pkg.installed:
        - pkgs:
            - nfs-common
/srv/phassa:
    mount.mounted:
        - device: {{ pillar['ip-phassa'] }}:/srv/nfs
        - fstype: nfs
        - mkmnt: true
