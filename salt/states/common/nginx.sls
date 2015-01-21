nginx:
    pkg:
        - installed
/etc/nginx/sites-enabled/default:
    file.absent
nginx running:
    service.running:
        - name: nginx
