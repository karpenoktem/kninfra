mailman packages:
    pkg.installed:
        - pkgs:
            - mailman
fcgiwrap:
    service.running:
        - enable: True
/etc/nginx/sankhara.d/10-mailman.conf:
    file.managed:
        - source: salt://sankhara/mailman.nginx.conf
        - template: jinja
/etc/mailman/mm_cfg.py:
    file.managed:
        - source: salt://sankhara/mm_cfg.py
        - template: jinja
