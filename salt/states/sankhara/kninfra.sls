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
mirte:
    pip.installed
sarah:
    pip.installed
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
/home/infra/.profile:
    file.managed:
        - source: salt://sankhara/profile
{% if grains['vagrant'] %}
/home/infra/repo:
    file.symlink:
        - target: /vagrant
{% else %}
https://github.com/karpenoktem/kninfra:
    git.latest:
        - target: /home/infra/repo
        - user: infra
    require:
        - pkg: git
{% endif %}
/home/infra/scm:
    file.directory:
        - user: infra
/home/infra/py:
    file.directory:
        - user: infra
/home/infra/bin:
    file.symlink:
        - target: /home/infra/repo/bin
/home/infra/settings.py:
    file.managed:
        - source: salt://sankhara/settings.py
        - template: jinja
        - user: infra
        - mode: 600
https://github.com/karpenoktem/regl:
    git.latest:
        - user: infra
        - target: /home/infra/scm/regl
    require:
        - pkg: git
/home/infra/py/regl:
    file.symlink:
        - target: /home/infra/scm/regl
{# We cannot set user/group on /vagrant.  Thus also not on /home/infra/repo.
 # We circumvent by using a symlink #}
/home/infra/repo/kn/settings.py:
    file.symlink:
        - target: /home/infra/settings.py
        {% if grains['vagrant'] %}
        - user: vagrant
        - group: vagrant
        {% endif %}
/home/infra/repo/bin/run-fcgi:
    cmd.run:
        - user: infra
