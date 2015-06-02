nginx packages:
    pkg.installed:
        - pkgs:
            - nginx
/etc/nginx/sites-enabled/default:
    file.absent
/etc/nginx/phassa.d:
    file.directory
/etc/nginx/sites-enabled/phassa.conf:
    file.managed:
        - source: salt://sankhara/site.nginx.conf
        - template: jinja
nginx running:
    service.running:
        - name: nginx
        - watch:
            - file: /etc/nginx/sites-enabled/phassa.conf
            # - file: /etc/nginx/phassa.d/*.conf
