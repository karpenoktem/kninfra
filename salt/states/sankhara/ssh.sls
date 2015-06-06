/root/.ssh:
    file.directory:
        - mode: 700
{% if grains['vagrant'] %}
/root/.ssh/id_rsa:
    file.managed:
        - source: salt://sankhara/vagrant-id_rsa
        - mode: 400
{% else %}
# TODO
{% endif %}
