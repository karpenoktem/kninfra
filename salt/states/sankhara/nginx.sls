nginx packages:
    pkg.installed:
        - pkgs:
            - nginx
            - fcgiwrap
            - php5-fpm
            - php-apc
/etc/nginx/sites-enabled/default:
    file.absent
/etc/nginx/sankhara.d:
    file.directory
/etc/nginx/backends:
    file.directory
/etc/nginx/backends/fcgiwrap:
    file.managed:
        - source: salt://sankhara/fcgiwrap.nginx-backend
/etc/nginx/backends/php:
    file.managed:
        - source: salt://sankhara/php.nginx-backend
/etc/nginx/sites-enabled/sankhara.conf:
    file.managed:
        - source: salt://sankhara/site.nginx.conf
        - template: jinja
/etc/php5/fpm/php.ini:
    file.managed:
        - source: salt://sankhara/php.ini
nginx running:
    service.running:
        - name: nginx
        - watch:
            - file: /etc/nginx/sites-enabled/sankhara.conf
            - file: /etc/nginx/sankhara.d/*.conf
php running:
    service.running:
        - name: php5-fpm
        - watch:
            - file: /etc/php5/fpm/php.ini
