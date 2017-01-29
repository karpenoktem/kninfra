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
            - python-httplib2
            - python-googleapi
            - python-ldap
            - python-smbpasswd
            - python-m2crypto
            - python-pyx
            - python-unidecode
            - python-six
            - gettext
            - imagemagick
mirte:
    pip.installed
sarah:
    pip.installed
tarjan:
    pip.installed
reserved:
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
fotos:
    group.present:
        - system: true
    user.present:
        - home: /var/fotos
        - system: true
        - shell: /bin/bash
        - createhome: false
        - groups:
            - fotos
/home/infra/.profile:
    file.managed:
        - source: salt://sankhara/infra.profile
/root/.profile:
    file.managed:
        - source: salt://sankhara/root.profile
        - template: jinja
{% if grains['vagrant'] %}
/home/infra/repo:
    file.symlink:
        - target: /vagrant
/root/kninfra:
    file.symlink:
        - target: /vagrant
/root/py:
    file.directory
/root/py/vagrantSettingsHack:
    file.directory
/root/py/vagrantSettingsHack/__init__.py:
    file.managed
/root/py/vagrantSettingsHack/settings.py:
    file.symlink:
        - target: /root/settings.py
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
/root/bin:
    file.symlink:
        - target: /root/kninfra/bin
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
# We cannot set user/group on /vagrant.  Thus also not on /home/infra/repo.
# We circumvent by using a symlink
/home/infra/repo/kn/settings.py:
    file.symlink:
        - target: /home/infra/settings.py
        {% if grains['vagrant'] %}
        - user: vagrant
        - group: vagrant
        {% endif %}
"giedo mysql user":
    mysql_user.present:
        - host: localhost
        - name: giedo
        - password: {{ pillar['secrets']['mysql_giedo'] }}
/home/infra/vpnkeys:
    file.directory:
        - user: infra
        - mode: 700
/var/run/infra:
    file.directory:
        - user: root
        - group: interinfra
        - mode: 770
/home/infra/storage:
    file.directory:
        - user: infra
/home/infra/storage/smoelen:
    file.directory:
        - user: infra
/home/infra/storage/graphs:
    file.directory:
        - user: infra
/var/fotos:
    file.directory:
        - user: fotos
        - group: fotos
{% if grains['vagrant'] %}
/var/fotos/test:
    file.symlink:
        - target: /home/infra/repo/kn/static/media/img
{% endif %}
/var/cache/fotos:
    file.directory:
        - user: infra
        - group: infra
/etc/default/daan:
    file.managed:
        - source: salt://sankhara/daan.default
        - template: jinja
/etc/default/giedo:
    file.managed:
        - source: salt://sankhara/giedo.default
/etc/systemd/system/daan.service:
    file.managed:
        - source: salt://sankhara/daan.service
/etc/systemd/system/cilia-tunnel.service:
    file.managed:
        - source: salt://sankhara/cilia-tunnel.service
/etc/systemd/system/giedo.service:
    file.managed:
        - source: salt://sankhara/giedo.service
giedo:
    service.running
/home/infra/repo/bin/run-fcgi:
    cmd.run:
        - user: infra
/etc/nginx/sankhara.d/90-kninfra.conf:
    file.managed:
        - source: salt://sankhara/kninfra.nginx.conf
        - template: jinja
{% if grains['vagrant'] %}
# If using vagrant, redirect the login to `vagrant' to the `infra' user.
/home/vagrant/.bash_login:
    file.managed:
        - contents: cd /home/infra && exec sudo su - infra
/etc/sudoers.d/vagrant-infra:
    file.managed:
        - contents: infra ALL=NOPASSWD:ALL
{% endif %}
