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
/etc/nginx/sankhara.d/20-phassaProxy.conf:
    file.managed:
        - source: salt://sankhara/phassaProxy.nginx.conf
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
/etc/nginx/conf.d:
    file.directory
/etc/nginx/conf.d/20-ssl.conf:
    file.managed:
        - source: salt://sankhara/ssl.nginx.conf
/etc/nginx/certs:
    file.directory
/etc/nginx/certs/dhparam.pem:
    file.managed:
        - source: salt://sankhara/ssl.dhparam.pem
/etc/nginx/certs/ocsp-stapler.crt:
    file.managed:
        - source: salt://sankhara/ssl.ocsp-stapler.crt
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
