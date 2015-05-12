nginx:
    pkg:
        - installed
/etc/nginx/sites-enabled/default:
    file.absent
/etc/nginx/sites-enabled/sankhara:
    file.managed:
        - source: salt://sankhara/nginx-site
        - template: jinja
nginx running:
    service.running:
        - name: nginx
        - watch:
            - file: /etc/nginx/sites-enabled/sankhara
