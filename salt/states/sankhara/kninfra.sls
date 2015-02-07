packages:
    pkg.installed:
        - pkgs:
            - python-django
            - msgpack-python
            - python-setuptools
            - python-pyparsing
            - python-markdown
            - python-flup
            - python-pymongo
            - python-mysqldb
            - python-imaging
            - python-pip
infra:
    user.present:
        - home: /home/infra
        - uid: 2000
        - guid: 2000
interinfra:
    group.present:
        - gid: 3000
        - addusers:
            - infra
            - www-data
{% if grains['vagrant'] %}
/home/infra/repo:
    file.symlink:
        - target: /vagrant
{% else %}
https://github.com/karpenoktem/kninfra:
    git.latest:
        - target: /home/infra/repo
    require:
        - pkg: git
{% endif %}
/home/infra/bin:
    file.symlink:
        - target: /home/infra/repo/bin
/home/infra/repo/bin/run-fcgi:
    cmd.run:
        - user: infra
