phpmyadmin packages:
    pkg.installed:
        - pkgs:
            - phpmyadmin
/etc/nginx/sankhara.d/10-phpmyadmin.conf:
    file.managed:
        - source: salt://sankhara/phpmyadmin.nginx.conf
        - template: jinja
