kninfra packages:
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
            - python-html2text
mirte:
    pip.installed
sarah:
    pip.installed
infra:
    group.present:
        - gid: 2000
    user.present:
        - home: /home/infra
        - uid: 2000
        - shell: /bin/bash
        - groups:
            - infra
            - interinfra
            - list
            {% if grains['vagrant'] %}
            - sudo
            - vagrant
            {% endif %}
/home/infra/.profile:
    file.managed:
        - source: salt://sankhara/profile
{% if grains['vagrant'] %}
/home/infra/repo:
    file.symlink:
        - target: /vagrant
/root/kninfra:
    file.symlink:
        - target: /vagrant
{% else %}
"kninfra clone infra":
    git.latest:
        - name: https://github.com/karpenoktem/kninfra
        - target: /home/infra/repo
        - user: infra
    require:
        - pkg: git
"kninfra clone root":
    git.latest:
        - name: https://github.com/karpenoktem/kninfra
        - target: /root/kninfra
        - user: root
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
/root/settings.py:
    file.managed:
        - source: salt://sankhara/settings-daan.py
        - template: jinja
        - user: root
        - mode: 600
/home/infra/settings.py:
    file.managed:
        - source: salt://sankhara/settings.py
        - template: jinja
        - user: infra
        - mode: 600
https://github.com/awesterb/koert:
    git.latest:
        - user: infra
        - target: /home/infra/scm/koert
    require:
        - pkg: git
/home/infra/py/koert:
    file.symlink:
        - target: /home/infra/scm/koert
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
/etc/nginx/sankhara.d/90-kninfra.conf:
    file.managed:
        - source: salt://sankhara/kninfra.nginx.conf
        - template: jinja
{% if grains['vagrant'] %}
/home/vagrant/.bash_login:
    file.managed:
        - contents: cd /home/infra && exec sudo su - infra
/etc/sudoers.d/vagrant-infra:
    file.managed:
        - contents: infra ALL=NOPASSWD:ALL
{% endif %}
