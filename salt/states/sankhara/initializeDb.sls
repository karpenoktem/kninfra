{% if grains['vagrant'] %}
/home/infra/initial-db.yaml:
    file.managed:
        - source: salt://sankhara/initial-db.yaml
Initialize database:
    cmd.script:
        - source: salt://sankhara/initializeDb.py
        - onchanges:
            - file: /home/infra/initial-db.yaml
{% endif %}
