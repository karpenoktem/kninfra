/root/.ssh:
    file.directory:
        - mode: 700
/root/.ssh/config:
    file.managed:
        - source: salt://sankhara/root.ssh.config
        - mode: 600
        - template: jinja
{% if grains['vagrant'] %}
/root/.ssh/id_rsa:
    file.managed:
        - source: salt://sankhara/vagrant-id_rsa
        - mode: 400
{% else %}
# TODO
{% endif %}
