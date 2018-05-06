/etc/systemd/system/infra-dir.service:
    file.managed:
        - source: salt://phassa/infra-dir.service
