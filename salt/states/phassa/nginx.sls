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
        - source: salt://phassa/site.nginx.conf
        - template: jinja
/etc/nginx/phassa.d/20-userdirs.conf:
    file.managed:
        - source: salt://phassa/userdirs.nginx.conf
nginx running:
    service.running:
        - name: nginx
        - watch:
            - file: /etc/nginx/sites-enabled/phassa.conf
            - file: /etc/nginx/phassa.d/*.conf
